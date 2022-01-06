#!/usr/bin/env python3

import click
from local_lib.utils import *

from local_lib.custom_validator import URL

from local_lib.decorators import check_if_project_folder_and_metadata_exist, \
    check_if_settings_exists
import os
from local_lib.helpers import download_archive, extract_archive
from version import version

# global settings
try:
    settings_path = get_correct_settings_path()
    settings_dict = read_settings_file_as_dict(settings_path)['defaults']
except:
    pass

@click.group()
def cli():
    """This script creates a cKAN dataset based on a metadata PDF and uploads all valid files
    of a folder (subfolders included).
    Note: run [command] --help on commands to get more information.
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
@click.option('--username',
              help='Your Username, will be written to package-upload-log.json',
              required=True,
              type=str)
@click.option('--overwrite',
              is_flag=True)
def set_settings(api_key, url, owner_org, username, overwrite):
    """Create file 'settings.ini' """
    create_settings(api_key, url, owner_org, username, overwrite)


@cli.command()
@check_if_settings_exists
def show_settings():
    """Show settings and version."""
    click.echo(f"\nScript Version: {version}\n---".upper())

    settings_path = get_correct_settings_path()
    click.echo(f"Local settings path: ".upper()+f"{settings_path}\n")
    try:
        with open(settings_path, 'r') as f:
            print(f.read())
    except:
        pass


    server_config = load_settings_from_server(settings_dict)
    click.echo(f"---\nServer settings:".upper())
    click.echo(f"Max upload-size: {server_config['allowed_max_upload_size']} MB")
    click.echo(f"Allowed extensions: {server_config['allowed_extensions']}\n")


@cli.command()
@click.option('--slug', '-s', help='Slugs of datasets each as -s', required=True, multiple=True)
def delete_datasets(slug):
    """Batch delete datasets by slug."""
    click.echo(f"Following datasets will be deleted {slug}")
    click.confirm("Are you sure?")
    delete_package(slug, settings_dict)


@cli.command()
@click.option('--url', '-u', help='Resource URL (only zip or tar.gz) i.e. "https://example.com/data.zip"', required=True)
@click.option('--out', '-o', help='Local directory to extract file to i.e. /tmp', required=True)
@click.option('--no-unpack', help="If set archive will not be unpacked", is_flag=True)
def fetch_archive(url, out, no_unpack):
    """Fetch zip or tar resource and unpack it. You can then use the extracted dir as input for
     upload-package command """
    click.echo(f"Fetching: {url}")
    d_file = download_archive(url, out)
    if not no_unpack:
        click.echo(f"Extracting zip: {d_file} to {out}")
        extract_archive(d_file, out)


@cli.command()
def review_needed():
    """Show all pending datasets."""
    get_pending_datasets(settings_dict)


@cli.command()
@click.option('--folder_path', help='The path to your data folder: Example "/tmp/my_dataset"', required=True)
@check_if_project_folder_and_metadata_exist
@check_if_settings_exists
def upload_package(folder_path):
    """Upload a package to cKAN. It needs a folder path as input.
    The folder must contain a pdf called metadata.pdf. The Form data is used to create a new packge"""

    metadata_file_path = os.path.join(folder_path, 'metadata.pdf')

    pdf_form_data = read_metatadata_from_pdf(metadata_file_path)
    confirm_metadata(pdf_form_data)
    new_package_name = create_package_with_metadata_values(pdf_form_data, settings_dict)

    click.echo(f"\n--- \nYour package {new_package_name} has been created\n--- ")
    server_settings = load_settings_from_server(settings_dict)
    upload_resources_to_package(folder_path,
                                settings_dict,
                                new_package_name,
                                server_settings)  # iter files, validate extension and filesize


if __name__ == '__main__':
    cli()
