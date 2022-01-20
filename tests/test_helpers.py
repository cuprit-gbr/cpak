import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from local_lib.helpers import *
import pytest
from pathlib import Path
import os

# Run with:
# python3 -m pytest -q test*.py
# python3 -m pytest  -q test_utils.py::test_download_file
# pytest --exitfirst --verbose --failed-first

@pytest.fixture(scope="session")
def get_tmp_dir(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data")
    return fn


def test_generate_secure_name():
    filename = generate_secure_name("ö.txt")
    assert filename == "o.txt"


"""
def test_json_matcher(httpserver: HTTPServer):
    httpserver.expect_request("/foo", json={"foo": "bar"}).respond_with_data("Hello world!")
    assert requests.get(httpserver.url_for("/foo")).status_code == 500
    resp = requests.get(httpserver.url_for("/foo"), json={"foo": "bar"})
    assert resp.status_code == 200
    assert resp.text == "Hello world!"
    assert requests.get(httpserver.url_for("/foo"), json={"foo": "bar", "foo2": "bar2"}).status_code == 500
"""

def test_download_file(get_tmp_dir):
    out = str(get_tmp_dir)
    d_file = download_archive("https://github.com/cuprit-gbr/cpak-testdata/raw/main/sample.zip", out)
    print(get_tmp_dir)
    print(d_file)
    file_name = Path(d_file)
    assert file_name.exists()


def test_extract_archive(get_tmp_dir):
    d_file = str(get_tmp_dir)+"/sample.zip"
    out = str(get_tmp_dir)
    d_dir = extract_archive(d_file, out)
    print(get_tmp_dir)
    print(d_file)
    assert os.path.isdir(d_dir)


def test_write_logfile(get_tmp_dir):
    logfile = str(get_tmp_dir)+"/log.json"
    content = "Hello"
    write_logfile(content, logfile)
    assert os.path.isfile(logfile)

    with open(logfile) as f:
        lines = f.read().rstrip().replace('"', '')
        print(lines)
    assert lines == "Hello"


def test_find_files_in_directory(get_tmp_dir):
    file_structure = find_files_in_directory(str(get_tmp_dir)+"/sample")
    print(file_structure)
    assert len(file_structure) > 0, "Length of file structure is 0"


def test_iter_files(get_tmp_dir):
    file_list = find_files_in_directory(str(get_tmp_dir)+"/sample")
    server_settings = {"allowed_max_upload_size": "200",
                       "allowed_extensions": ["txt"]}
    files = iter_files(file_list, server_settings)
    print(files)
    assert "filename" in files["files_to_upload"][0]


def test_check_filenames_for_duplicates(get_tmp_dir):
    file_list = find_files_in_directory(str(get_tmp_dir)+"/sample")
    duplicates = check_filenames_for_duplicates(file_list)
    assert len(duplicates) == 0


def test_path_to_dict(get_tmp_dir):
    return_dict = path_to_dict(str(get_tmp_dir) + "/sample")
    assert "children" in return_dict


def test_remove_user_path():
    dict = {
        0: {
            'path': '/Users/private_name/data/metadata Kopie.pdf',
            'filename': 'metadata Kopie.pdf'
            },
        1: {
            'path': '/Users/private_name/data/a.zip',
            'filename': 'a.zip'
            }
    }

    cleaned_dict = remove_user_path("/Users/private_name/data/", dict)
    path_cleaned = []
    for item in cleaned_dict.values():
        path_cleaned.append("private_name" in item["path"])
    assert all(path_cleaned) == 0


