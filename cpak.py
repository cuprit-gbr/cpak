#!/usr/bin/env python3

import click
from local_lib.utils import create_settings, read_metatadata_from_pdf, \
    confirm_metadata, create_package_with_metadata_values, \
    read_settings_file_as_dict, upload_resources_to_package, \
    check_if_settings_exists, get_correct_settings_path, delete_package, load_allowed_extensions, \
    get_pending_datasets

from local_lib.custom_validator import URL

from local_lib.decorators import check_if_project_folder_and_metadata_exist
import os
from version import version


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
def show_settings():
    """This command shows content of current 'settings.ini'."""
    settings_path = get_correct_settings_path()
    click.echo(settings_path)
    # TODO: refactor needed
    check_if_settings_exists()
    with open(settings_path, 'r') as f:
        print(f.read())
    pass

@cli.command()
def show_version():
    """Show the current script version"""
    click.echo(os.path.basename(__file__))
    click.echo(version)

@cli.command()
@click.option('--slug','-s',  help='Slugs of datasets each as -s', required=True, multiple=True)
def delete_datasets(slug):
    """Batch delete datasets"""
    click.echo(f"Followin datasets will be deleted {slug}")
    click.confirm("Are you sure?")

    settings_path = get_correct_settings_path()
    settings_dict = read_settings_file_as_dict(settings_path)
    delete_package(slug, settings_dict['defaults'])

@cli.command()
def show_allowed_extension():
    """Show allowed extensions to upload"""

    settings_path = get_correct_settings_path()
    settings_dict = read_settings_file_as_dict(settings_path)
    allowed_extension = load_allowed_extensions(settings_dict['defaults'])
    print(allowed_extension)

@cli.command()
def show_pending_datasets():
    """Show all pending datasets (private)"""
    settings_path = get_correct_settings_path()
    settings_dict = read_settings_file_as_dict(settings_path)
    get_pending_datasets(settings_dict['defaults'])


@cli.command()
@click.option('--folder_path',  help='your iDAI.open_data API Key', required=True)
@check_if_project_folder_and_metadata_exist
def upload_package(folder_path):
    """This command will upload a package to cKAN. It needs a folder path as input.
    The folder must contain a pdf called metadata.pdf. The Form data is used to create a new packge"""

    check_if_settings_exists()
    metadata_file_path = os.path.join(folder_path, 'metadata.pdf')
    settings_path = get_correct_settings_path()
    settings_dict = read_settings_file_as_dict(settings_path)

    pdf_form_data = read_metatadata_from_pdf(metadata_file_path)
    confirm_metadata(pdf_form_data)
    new_package_name = create_package_with_metadata_values(pdf_form_data, settings_dict['defaults']) # before check if package already exists

    click.echo(f"\n--- \nYour package {new_package_name} has been created?\n--- ")
    allowed_extensions = load_allowed_extensions(settings_dict['defaults'])
    upload_resources_to_package(folder_path,
                                settings_dict['defaults'],
                                new_package_name,
                                allowed_extensions) # iter files, validate extension and filesize



if __name__ == '__main__':
    cli()