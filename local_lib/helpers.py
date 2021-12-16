import os
import json
from slugify import slugify
import mimetypes
import glob
from collections import Counter


def generate_secure_name(file_path):
    file, ext = os.path.splitext(file_path)
    secure_name_no_extension = slugify(file, lowercase=False)
    return secure_name_no_extension+ext

def path_to_dict(path):
    file_path = os.path.basename(path)

    d = {
        'name': file_path,
        'safe_name': generate_secure_name(file_path)
    }
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
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


def iter_files(file_list, settings_dict, allowed_extensions):
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
        settings_max_filesize = int(settings_dict['max_filesize'])
        if file_name == 'metadata.pdf':
            continue

        if not file_extension \
                or file_extension not in allowed_extensions \
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
