import os
import json
from slugify import slugify
import mimetypes
import glob
from collections import Counter
import wget
import zipfile
import tarfile
import pathlib
import copy

def generate_secure_name(file_path):
    file, ext = os.path.splitext(file_path)
    secure_name_no_extension = slugify(file, lowercase=False)
    return secure_name_no_extension + ext


def path_to_dict(path):
    file_path = os.path.basename(path)

    d = {
        'name': file_path,
        'safe_name': generate_secure_name(file_path)
    }
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path, x)) for x in os.listdir(path)]
    else:
        d['type'] = "file"
        d['mime_type']: mimetypes.MimeTypes().guess_type(file_path)[0]
    return d


def write_logfile(log_content, log_file_name):
    log_content = json.dumps(log_content, indent=4)
    with open(log_file_name, "w", encoding='utf-8') as log:
        log.write(log_content)


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


def iter_files(file_list, server_settings):
    separated_filelist = {
        "files_to_upload": {},
        "files_exceed_size": {},
        "files_with_duplicate_names": [],
        "files_missing_or_wrong_extension": {}
    }

    for i, file in enumerate(file_list):
        file_name = os.path.basename(file)
        full_file_path, file_extension = os.path.splitext(file)
        file_extension = file_extension.strip(".")
        filesize = os.path.getsize(file) / 1000000
        settings_max_filesize = float(server_settings["allowed_max_upload_size"])
        if file_name == 'metadata.pdf':
            continue

        if not file_extension \
                or file_extension not in server_settings["allowed_extensions"] \
                and filesize <= settings_max_filesize:
            target = 'files_missing_or_wrong_extension'
        elif filesize > settings_max_filesize:
            target = 'files_exceed_size'
        else:
            target = 'files_to_upload'
        separated_filelist[target][i] = {'path': file,
                                         'filesize': filesize,
                                         'filename': file_name,
                                         'safe_filename': generate_secure_name(file_name)
                                         }
    separated_filelist['files_with_duplicate_names'] = check_filenames_for_duplicates(file_list)
    return separated_filelist


def download_archive(url, out):
    try:
        d_file = wget.download(url, out)
        return d_file
    except Exception as e:
        return e


def extract_archive(d_file, out):
    os.path.join(out, d_file)

    if zipfile.is_zipfile(d_file):
        with zipfile.ZipFile(d_file, 'r') as zip_ref:
            zip_ref.extractall(out)
        return out

    if tarfile.is_tarfile(d_file):
        tar_archive = tarfile.open(d_file)
        tar_archive.extractall(out)
        tar_archive.close()
        return out

    return None

def remove_user_path(folder_path, user_dict):

    if isinstance(user_dict, dict):
        user_dict_copy = copy.deepcopy(user_dict)
        for file in user_dict_copy.values():
            root_folder = pathlib.PurePath(folder_path)
            clean_path = os.path.join(root_folder.name, file['filename'])
            file['path'] = clean_path
        return user_dict_copy