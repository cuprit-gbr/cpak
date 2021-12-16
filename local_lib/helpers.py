import os
import json
from slugify import slugify
import mimetypes

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
