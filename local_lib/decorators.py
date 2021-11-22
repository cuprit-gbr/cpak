from functools import update_wrapper
import click
import os

"""
def capitalise_input(f):
    @click.pass_context
    def run(ctx, *args, **kwargs):
        kwargs['folder_path'] = kwargs['folder_path'].upper()
        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(run, f)
"""

def check_if_settings_exists(f):
    settings_file = 'settings.ini'
    file_exists = os.path.isfile(settings_file)

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    settings_path = os.path.join(__location__, 'settings.ini')
    print(__location__)

    if file_exists:
        @click.pass_context
        def run(ctx, *args, **kwargs):
            return ctx.invoke(f, *args, **kwargs)
        return update_wrapper(run, f)

    else:
        click.echo("settings.ini does not exist")

def check_if_project_folder_and_metadata_exist(f):
    @click.pass_context
    def run(ctx, *args, **kwargs):
        folder_path = kwargs['folder_path']
        folder_exists = os.path.isdir(folder_path)
        file_exists = os.path.isfile(os.path.join(folder_path,'metadata.pdf'))
        if all([folder_exists,file_exists]):
            kwargs['folder_path'] = kwargs['folder_path']
            return ctx.invoke(f, *args, **kwargs)
        else:
            click.echo(f"this folder {folder_path} does not exist "
                       f"or is missing a pdf called 'metadata.pdf'")
            exit()
    return update_wrapper(run, f)

