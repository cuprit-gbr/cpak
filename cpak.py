#!/usr/bin/env python3

import click
from local_lib.utils import create_settings, read_metatadata_from_pdf, \
    confirm_metadata, create_package_with_metadata_values, \
    read_settings_file_as_dict, upload_resources_to_package, check_if_settings_exists
from local_lib.custom_validator import URL
from local_lib.decorators import check_if_project_folder_and_metadata_exist
import os
from version import version

@click.group()
def cli():
    """This script creates a cKAN dataset based on a metadata PDF and uploads all valid files
    in a folder and subfolders"""
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
@click.option('--overwrite',
              help='overwrite settings?',
              required=False,
              default=False,
              type=bool)
def set_settings(api_key, url, owner_org, max_filesize, overwrite):
    """This command will create a settings file called 'settings.ini'.
    The settings file contains default settings like upload limits next to your api key."""
    create_settings(api_key, url, owner_org, max_filesize, overwrite)

@cli.command()
def show_settings():
    """This command shows content of current 'settings.ini'."""
    check_if_settings_exists()
    with open('settings.ini', 'r') as f:
        print(f.read())
    pass

@cli.command()

def show_version():
    """Show the current script version"""
    click.echo(os.path.basename(__file__))
    click.echo(version)

@cli.command()
@click.option('--folder_path',  help='your iDAI.open_data API Key', required=True)
@check_if_project_folder_and_metadata_exist
def upload_package(folder_path):
    """This command will upload a package to cKAN. It needs a folder path as input.
    The folder must contain a pdf called metadata.pdf. The Form data is used to create a new packge"""

    check_if_settings_exists()
    metadata_file_path = os.path.join(folder_path, 'metadata.pdf')
    settings_dict = read_settings_file_as_dict('settings.ini')

    pdf_form_data = read_metatadata_from_pdf(metadata_file_path)
    confirm_metadata(pdf_form_data)
    new_package_name = create_package_with_metadata_values(pdf_form_data, settings_dict['defaults']) # before check if package already exists

    click.confirm(f"\n--- \nYour Package {new_package_name} has been created continue read and upload files?", abort=True)
    upload_resources_to_package(folder_path, settings_dict['defaults'], new_package_name) # iter files, validate extension and filesize



if __name__ == '__main__':
    cli()