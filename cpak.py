#!/usr/bin/env python3

import click
from local_lib.utils import *

from local_lib.custom_validator import URL

from local_lib.decorators import check_if_project_folder_and_metadata_exist, check_if_settings_exists
import os
from version import version
import wget
import zipfile
import tarfile

# global settings
try:
    settings_path = get_correct_settings_path()
    settings_dict = read_settings_file_as_dict(settings_path)['defaults']
except:
    pass

@click.group()
def cli():
    """This script creates a cKAN dataset based on a metadata PDF and uploads all valid files
    in a folder and subfolders.
    Note run [command]--help on commands to get more information.
    Example: cpak set-settings --help
    """
    pass

@cli.command()
@click.option('--api-key', help='your iDAI.open_data API Key', required=True, type=str)
@click.option('--url', help='your iDAI.open_data url', required=True, type=URL())
@click.option('--owner-org',
              help='The owner organisation. (default: dai-external)',
              required=False,
              default='dai-external',
              type=str)
@click.option('--max-filesize',
              help='Max file size of a file to upload',
              required=False,
              default=20,
              type=str)
@click.option('--username',
              help='Your Username, will be written to package.json',
              required=True,
              type=str)
@click.option('--overwrite',
              help='overwrite settings?',
              required=False,
              default=False,
              type=bool)
def set_settings(api_key, url, owner_org, max_filesize, username, overwrite):
    """This command will create a settings file called 'settings.ini'.
    The settings file contains default settings like upload limits next to your api key."""
    create_settings(api_key, url, owner_org, max_filesize, username, overwrite)


@cli.command()
@check_if_settings_exists
def show_local_settings():
    """This command shows content of current 'settings.ini'."""
    settings_path = get_correct_settings_path()
    click.echo(f"Local settings path: {settings_path}")
    click.echo(f"Local settings:\n---")
    try:
        with open(settings_path, 'r') as f:
            print(f.read())
    except:
        pass

    click.echo(f"Script name: {os.path.basename(__file__)}")
    click.echo(f"Version: {version}")


@cli.command()
def show_version():
    """Show the current script version"""
    click.echo(os.path.basename(__file__))
    click.echo(version)


@cli.command()
@click.option('--slug', '-s', help='Slugs of datasets each as -s', required=True, multiple=True)
def delete_datasets(slug):
    """Batch delete datasets"""
    click.echo(f"Following datasets will be deleted {slug}")
    click.confirm("Are you sure?")
    delete_package(slug, settings_dict['defaults'])


@cli.command()
@click.option('--url', '-u', help='Resource URL (only zip or tar.gz) i.e. "https://example.com/data.zip"', required=True)
@click.option('--out', '-o', help='Local directory to exctract file to i.e. extract', required=True)
def fetch__extract_archive(url, out):
    """Fetch zip or tar resource and unpack it"""
    current_path = os.getcwd()
    out_path = current_path+"/"+out

    click.echo(f"Fetching: {url}")
    d_file = wget.download(url)

    if zipfile.is_zipfile(d_file):
        click.echo(f"Extracting zip: {d_file} to out_path")
        with zipfile.ZipFile(d_file, 'r') as zip_ref:
            zip_ref.extractall(out_path)

    if tarfile.is_tarfile(d_file):
        click.echo(f"Extracting tar: {d_file} to out_path")
        tar_archive = tarfile.open(d_file)
        tar_archive.extractall(out_path)
        tar_archive.close()


@cli.command()
def show_server_settings():
    """Show allowed extensions to upload"""
    server_config = load_settings_from_server(settings_dict)
    click.echo(f"Max upload-size: {server_config['allowed_max_upload_size']}")
    click.echo(f"Allowed extensions: {server_config['allowed_extensions']}")


@cli.command()
def show_pending_datasets():
    """Show all pending datasets (private)"""
    get_pending_datasets(settings_dict)


@cli.command()
@click.option('--folder_path', help='your iDAI.open_data API Key', required=True)
@check_if_project_folder_and_metadata_exist
@check_if_settings_exists
def upload_package(folder_path):
    """This command will upload a package to cKAN. It needs a folder path as input.
    The folder must contain a pdf called metadata.pdf. The Form data is used to create a new packge"""

    metadata_file_path = os.path.join(folder_path, 'metadata.pdf')

    pdf_form_data = read_metatadata_from_pdf(metadata_file_path)
    confirm_metadata(pdf_form_data)
    new_package_name = create_package_with_metadata_values(pdf_form_data, settings_dict)

    click.echo(f"\n--- \nYour package {new_package_name} has been created?\n--- ")
    server_settings = load_settings_from_server(settings_dict)
    upload_resources_to_package(folder_path,
                                settings_dict,
                                new_package_name,
                                server_settings)  # iter files, validate extension and filesize


if __name__ == '__main__':
    cli()
