from functools import update_wrapper
import click
import os
from local_lib.utils import get_correct_settings_path

def check_if_project_folder_and_metadata_exist(f):
    @click.pass_context
    def run(ctx, *args, **kwargs):
        folder_path = kwargs['folder_path']
        folder_exists = os.path.isdir(folder_path)
        file_exists = os.path.isfile(os.path.join(folder_path, 'metadata.pdf'))
        if all([folder_exists, file_exists]):
            kwargs['folder_path'] = kwargs['folder_path']
            return ctx.invoke(f, *args, **kwargs)
        else:
            click.echo(f"this folder {folder_path} does not exist "
                       f"or is missing a pdf called 'metadata.pdf'")
            exit()

    return update_wrapper(run, f)

def check_if_settings_exists(f):
    @click.pass_context
    def run(ctx, *args, **kwargs):
        settings_path = get_correct_settings_path()
        file_exists = os.path.isfile(settings_path)
        if not file_exists:
            click.echo("settings.ini does not exist")
            quit()
        return ctx.invoke(f, *args, **kwargs)

    return update_wrapper(run, f)



