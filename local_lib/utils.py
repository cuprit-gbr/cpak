from os import path
import click
from PyPDF2 import PdfFileReader
import os
import ckanapi
from slugify import slugify
import glob
import pprint
from collections import Counter

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0


def create_settings(api_key, url, owner_org, max_filesize, overwrite):
    # instantiate
    ini_name = 'settings.ini'
    config = ConfigParser()
    file_exists = path.isfile(ini_name)
    if file_exists and overwrite is False:
        print("settings file already exists. please delete it first or set --overwrite=True")
        exit()
    # add a new section and some values
    config.add_section('defaults')
    config.set('defaults', 'url', url)
    config.set('defaults', 'api_key', api_key)
    config.set('defaults', 'max_filesize', max_filesize)
    config.set('defaults', 'owner_org', owner_org)
    with open(ini_name, 'w') as configfile:
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
    for field in pdf_form_data.values():
        if field['/T'] == "title" and '/V' not in field:
            title = False
        if '/V' not in field:
            click.echo(f" {field['/T']} = ")
            if field['/T'] == "title":
                title = False
        else:
            click.echo(f" {field['/T']} = {field['/V']}")

    if not title:
        click.echo("ERROR: The title is empty this package cannot be created!")
        quit()

    click.confirm('Is the data correct? Do you want to continue?', abort=True)


def check_if_package_already_exists(title, settings_dict, number=False):
    ckan = ckanapi.RemoteCKAN(settings_dict['url'],
                              apikey=settings_dict['api_key'],
                              user_agent='ckan_admin_uploader')

    if not number:
        is_unique_title = f"{title}"
    else:
        is_unique_title = f"{title}_{number}"

    try:
        ckan.action.package_show(id=is_unique_title)
        click.echo(f"the title '{is_unique_title}' is already in use, "
                   f"trying again with a higher number appended!")
        number = number + 1
        return check_if_package_already_exists(title, settings_dict, number)
    except Exception as e:
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
    # create a simple version of the raw pdf objects
    pdf_form_data_simplified = {k: v['/V'] for (k, v) in pdf_form_data.items()}
    unique_title = check_if_package_already_exists(slugify(pdf_form_data_simplified['title']), settings_dict)
    click.echo(f"{unique_title} is unique and will be used")

    # api obj
    ckan = ckanapi.RemoteCKAN(settings_dict['url'],
                              apikey=settings_dict['api_key'],
                              user_agent='ckan_admin_uploader')

    # create the final payload with a unique title
    resource_dict = {
        "name": unique_title,
        "maintainer": "he",
        "private": False,
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


def read_settings_file_as_dict(filename):
    parser = ConfigParser()
    parser.read(filename)
    settings_dict = {section: dict(parser.items(section)) for section in parser.sections()}
    return settings_dict


def find_files_in_directory(folder_path):
    search_path = os.path.join(folder_path, '**', '*')
    file_list = glob.iglob(search_path, recursive=True)
    file_list = [file for file in file_list if os.path.isfile(file)]
    return file_list


def check_filenames_for_duplicates(file_list):
    only_filenames = [os.path.basename(file) for file in file_list]
    count_duplicates = Counter(only_filenames)
    duplicates_filenames = list([item for item in count_duplicates if count_duplicates[item] > 1])
    return duplicates_filenames


def iter_files(file_list, settings_dict):
    ignore_extensions = ['.exe']

    separated_filelist = {
        "files_to_upload": {},
        "files_exceed_size": {},
        "files_with_duplicate_names": [],
        "files_missing_or_wrong_extension": {}
    }

    for i, file in enumerate(file_list):
        file_name = os.path.basename(file)
        full_file_path, file_extension = os.path.splitext(file)
        filesize = os.path.getsize(file) / 1000000
        settings_max_filesize = int(settings_dict['max_filesize'])
        blocked_chars = 'ß?!#äüöÄÜÖß '
        if file_name == 'metadata.pdf':
            continue

        if not file_extension \
                or file_extension in ignore_extensions \
                or any(i in file_name for i in blocked_chars) \
                and filesize <= settings_max_filesize:
            target = 'files_missing_or_wrong_extension'
        elif filesize > settings_max_filesize:
            target = 'files_exceed_size'
        else:
            target = 'files_to_upload'
        separated_filelist[target][i] = {'path': file,
                                         'filesize': filesize,
                                         'filename': file_name}
    separated_filelist['files_with_duplicate_names'] = check_filenames_for_duplicates(file_list)
    return separated_filelist


def upload_resources_to_package(folder_path, settings_dict, new_package_name):
    # api obj
    ckan = ckanapi.RemoteCKAN(settings_dict['url'],
                              apikey=settings_dict['api_key'],
                              user_agent='ckan_admin_uploader')

    all_files = find_files_in_directory(folder_path)
    separated_filelist = iter_files(all_files, settings_dict)

    if separated_filelist['files_exceed_size']:
        click.echo("\n--- \nNO UPLOAD: Following files exceed the allowed settings limit:\n")
        pprint.pprint(separated_filelist['files_exceed_size'])
    if separated_filelist['files_missing_or_wrong_extension']:
        click.echo("\n--- \nNO UPLOAD: Following filenames use special chars are, "
                   "allowed by extension or have no extension:\n")
        pprint.pprint(separated_filelist['files_missing_or_wrong_extension'])
    if separated_filelist['files_with_duplicate_names']:
        click.echo("\n--- \nWARNING: Following files have duplicate names but might be uploaded if"
                   "extension and filesize are fine:\n")
        pprint.pprint(separated_filelist['files_with_duplicate_names'])
    if separated_filelist['files_to_upload']:
        click.echo("\n--- \nUPLOAD: Following files look fine and will be uploaded:\n")
        pprint.pprint(separated_filelist['files_to_upload'])

    click.confirm('Do you like to upload above files?', abort=True)

    click.echo("--- \nThe final payload")
    for file in separated_filelist['files_to_upload'].values():
        click.echo(f" uploading: {file['path']}")
        # upload resource

        ckan.action.resource_create(
            package_id=new_package_name,
            url='n.N.',  # ignored but required by CKAN<2.6
            name=file['filename'],
            description='',
            upload=open(file['path'], 'rb'))

    click.echo(f"\n=== \nJob done ...")
    click.echo(f"You can visit the dataset {settings_dict['url']}dataset/{new_package_name}")


def check_if_settings_exists():
    settings_file = 'settings.ini'
    file_exists = os.path.isfile(settings_file)
    if file_exists:
        return True
    else:
        click.echo("settings_does_not_exist")
        quit()
