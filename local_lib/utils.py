from datetime import datetime
from os import path
import click
from PyPDF2 import PdfFileReader
import os
import ckanapi
from slugify import slugify
import pprint
import pathlib
from local_lib.helpers import path_to_dict, \
    write_logfile, \
    find_files_in_directory, \
    iter_files
from tabulate import tabulate


try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0


def get_correct_settings_path():
    # check if user called script from bin folder
    folder = pathlib.Path(__file__).resolve()
    parent_folder = folder.parent.parent.name

    settings_file = 'settings.ini'
    if parent_folder == "cpak":
        settings_path = os.path.abspath(
            os.path.join(folder, '..', '..', '..', settings_file)
        )
    else:
        settings_path = os.path.abspath(
            os.path.join(folder, '..', '..', settings_file)
        )

    return settings_path


def create_settings(api_key, url, owner_org, max_filesize, username, overwrite):
    settings_path = get_correct_settings_path()
    # instantiate
    config = ConfigParser()
    file_exists = path.isfile(settings_path)
    if file_exists and overwrite is False:
        print("settings file already exists. please delete it first or set --overwrite=True")
        exit()
    # add a new section and some values
    config.add_section('defaults')
    config.set('defaults', 'url', url)
    config.set('defaults', 'api_key', api_key)
    config.set('defaults', 'username', username)
    config.set('defaults', 'max_filesize', max_filesize)
    config.set('defaults', 'owner_org', owner_org)
    with open(settings_path, 'w') as configfile:
        config.write(configfile)
    click.echo("settings.ini created")


def read_metatadata_from_pdf(metadata_file_path):
    pdf_reader = PdfFileReader(open(metadata_file_path, "rb"))
    # currently we use getFields() as getFormTextFields ignores dropdowns
    # https://github.com/mstamy2/PyPDF2/issues/391
    pdf_form_data = pdf_reader.getFields()  # returns a python dictionary
    return pdf_form_data


def confirm_metadata(pdf_form_data):
    click.echo("The used metadata is:")
    title = "None"
    metadata = []
    for field in pdf_form_data.values():
        if field['/T'] == "title" and '/V' not in field:
            title = False
        if '/V' not in field:
            metadata.append([field['/T'], "-", "NOT OK"])
            if field['/T'] == "title":
                title = False
        else:
            metadata.append([field['/T'], field['/V'], "OK"])

    print(tabulate(metadata))

    if not title:
        click.echo("ERROR: The title is empty this package cannot be created!")
        quit()

    click.confirm('\nIs the data correct?', abort=True)


def check_if_package_already_exists(title, settings_dict, number=False):
    ckan = ckanapi.RemoteCKAN(settings_dict['url'],
                              apikey=settings_dict['api_key'],
                              user_agent='ckan_admin_uploader')

    is_unique_title = f"{title}"
    if number:
        is_unique_title = f"{title}_{number}"

    try:
        ckan.action.package_show(id=is_unique_title)
        click.echo(f" - The title '{is_unique_title}' is already in use, retrying.")
        number = number + 1
        return check_if_package_already_exists(title, settings_dict, number)
    except:
        return is_unique_title


def get_lisence_key(lisence_name):
    license_dict = {
        "cc-by": "Creative Commons Attribution",
        "cc-by-sa": "Creative Commons Attribution Share-Alike",
        "cc-zero": "Creative Commons CCZero",
        "cc-nc": "Creative Commons Non-Commercial (Any)",
        "gfdl": "GNU Free Documentation License",
        "notspecified": "License not specified",
        "odc-by": "Open Data Commons Attribution License",
        "odc-odbl": "Open Data Commons Open Database License (ODbL)",
        "odc-pddl": "Open Data Commons Public Domain Dedication and License (PDDL)",
        "other-at": "Other (Attribution)",
        "other-nc": "Other (Non-Commercial)",
        "uk-ogl": "UK Open Government Licence (OGL)",
        "other-closed": "Other (Not Open)",
        "other-open": "Other (Open)",
        "other-pd": "Other (Public Domain)"
    }
    return list(license_dict.keys())[list(license_dict.values()).index(lisence_name)]


def create_package_with_metadata_values(pdf_form_data, settings_dict):
    # create a simplified version of the raw pdf objects
    pdf_form_data_simplified = {k: v.get('/V', "") for (k, v) in pdf_form_data.items()}
    unique_title = check_if_package_already_exists(slugify(pdf_form_data_simplified['title']), settings_dict)
    click.echo(f"{unique_title} is unique and will be used")

    ckan = ckanapi.RemoteCKAN(settings_dict['url'],
                              apikey=settings_dict['api_key'],
                              user_agent='ckan_admin_uploader')

    # create the final payload with a unique title
    resource_dict = {
        "name": unique_title,
        "maintainer": "he",
        "private": True,
        "owner_org": settings_dict['owner_org']
    }

    final_payload = {**resource_dict, **pdf_form_data_simplified}
    final_payload['license_id'] = get_lisence_key(pdf_form_data_simplified['license_title'])
    final_payload['publisher'] = f"{pdf_form_data_simplified['firstname']}, " \
                                 f"{pdf_form_data_simplified['lastname']}"

    try:
        ckan.action.package_create(**final_payload)
        return unique_title
    except Exception as e:
        print(e)
        exit()


def read_settings_file_as_dict(filename):
    parser = ConfigParser()
    parser.read(filename)
    settings_dict = {section: dict(parser.items(section)) for section in parser.sections()}
    return settings_dict


def upload_resources_to_package(folder_path, settings_dict, new_package_name, server_settings):
    # api obj
    ckan = ckanapi.RemoteCKAN(settings_dict['url'],
                              apikey=settings_dict['api_key'],
                              user_agent='ckan_admin_uploader')

    #  create logfile
    log_file_name = os.path.join(folder_path, 'package.json')
    open(log_file_name, "w")

    # create list of files
    all_files = find_files_in_directory(folder_path)
    separated_filelist = iter_files(all_files, server_settings)

    #  start logfile content
    log_file_name = os.path.join(folder_path, 'package.json')
    open(log_file_name, "w")

    log_content = {}
    log_content['uploaded_by'] = settings_dict['username']
    log_content['uploaded_date'] = str(datetime.now())
    log_content['original_dataset'] = path_to_dict(folder_path)

    # fill dataset overview dict
    if separated_filelist['files_exceed_size']:
        click.echo("\n--- \nNO UPLOAD: Following files exceed the allowed settings limit:\n")
        pprint.pprint(separated_filelist['files_exceed_size'])
        log_content['files_exceed_size'] = separated_filelist['files_exceed_size']

    if separated_filelist['files_missing_or_wrong_extension']:
        click.echo("\n--- \nNO UPLOAD: Following filenames are "
                   "not allowed by extension or have no extension:\n")
        pprint.pprint(separated_filelist['files_missing_or_wrong_extension'])
        log_content['files_missing_or_wrong_extension'] = separated_filelist['files_missing_or_wrong_extension']

    if separated_filelist['files_with_duplicate_names']:
        click.echo("\n--- \nWARNING: Following files have duplicate names but might be uploaded if"
                   " extension and filesize are fine:\n")
        pprint.pprint(separated_filelist['files_with_duplicate_names'])
        log_content['files_with_duplicate_names'] = separated_filelist['files_with_duplicate_names']

    if separated_filelist['files_to_upload']:
        click.echo("\n--- \nUPLOAD: Following files look fine and will be uploaded:\n")
        pprint.pprint(separated_filelist['files_to_upload'])
        log_content['files_to_upload'] = separated_filelist['files_to_upload']

    # write logfile
    write_logfile(log_content, log_file_name)
    click.echo("\n---\nCreated logfile from your file structure\n---")

    # uploading of files
    click.confirm('Do you like to upload above files?', abort=True)

    failed_uploads = []
    click.echo("--- \nUploading ...")
    for file in separated_filelist['files_to_upload'].values():
        try:
            click.echo(f" ... uploading: {file['path']}")
            ckan.action.resource_create(
                package_id=new_package_name,
                url='n.N.',  # ignored but required by CKAN<2.6
                name=slugify(file['filename'], lowercase=False),
                description='',
                upload=open(file['path'], 'rb'))
            click.echo(f" uploaded: {file['path']}")

        except Exception as e:
            click.echo(f"{file['filename']} failed : {e}")
            failed_uploads.append(file['filename'])
            pass

    if len(failed_uploads) > 0:
        click.echo("Those files failed to upload. Please try by use of the GUI")
        for failed in failed_uploads:
            click.echo(failed)

    click.echo(f"\n=== \nJob done ...")
    click.echo(f"You can view the dataset {settings_dict['url']}dataset/{new_package_name}")


def delete_package(slug, settings_dict):
    ckan = ckanapi.RemoteCKAN(settings_dict['url'],
                              apikey=settings_dict['api_key'],
                              user_agent='ckan_admin_uploader')
    for res in slug:
        try:
            print(res)
            ckan.action.dataset_purge(id=res)
        except Exception as e:
            print(e)
            pass


def load_settings_from_server(settings_dict):
    ckan = ckanapi.RemoteCKAN(settings_dict['url'],
                              apikey=settings_dict['api_key'],
                              user_agent='ckan_admin_uploader')

    try:
        server_settings = ckan.action.get_conf()
        server_settings = {"allowed_extensions": server_settings["ext"],
                           "allowed_max_upload_size": server_settings["max_size"]
                           }
        return server_settings
    except Exception as e:
        print(e)
        pass


def get_pending_datasets(settings_dict):
    ckan = ckanapi.RemoteCKAN(settings_dict['url'],
                              apikey=settings_dict['api_key'],
                              user_agent='ckan_admin_uploader')
    try:
        all_resources = ckan.action.package_search(
            include_private=True,
            rows=1000
        )["results"]
        click.echo('\nFollowing datasets are still set to private')
        i=1
        results = [['nr.', 'author', 'dataset']]

        for resource in all_resources:
            if resource['private']:
                results.append([i, resource['author'], settings_dict['url']+"dataset/"+resource['name']])
                i = i+1
        print(tabulate(results))
    except Exception as e:
        print(e)
        pass
