import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from local_lib.utils import *
from pathlib import Path
import pytest
import urllib.request


def test_get_correct_settings_path():
    settings_path = get_correct_settings_path()
    p = Path(settings_path)
    assert p.name == "settings.ini"


"""
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("localhost", 8888)

def test_httpserver(httpserver):
    body = "Hello, World!"
    endpoint = "/hello"
    httpserver.expect_request(endpoint).respond_with_data(body)
    with urllib.request.urlopen(httpserver.url_for(endpoint)) as response:
        result = response.read().decode()
    assert body == result
"""

"""
# TODO: test ckanapi
def test_load_settings_from_server(httpserver):

    body = {
        "ext": "abc",
        "max_size": "20"
    }
    endpoint = "/hello"

    settings_dict = { "url": httpserver.url_for(endpoint),
                    "api_key": "dummy"
    }
    httpserver.expect_request(endpoint).respond_with_data(body)
    response = load_settings_from_server(settings_dict)
    print(response)
    assert False
"""