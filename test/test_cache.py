import pytest
import sys
sys.path.append("..")
from lib.utils.log import Log
from lib.utils.cache import Cache
from lib.core.settings import SQLITE_FILE_NAME
import json


log = Log("test.log")
cache = Cache(SQLITE_FILE_NAME)
url = "http://sample.com"

@pytest.mark.create
def test_create_cache():
    log.debug(cache.create_cache())

@pytest.mark.insert
def test_insert_cache():
    db_name = "mysql"
    boundaries = [{
        "prefix": "'",
        "suffix": "and'[RANDNUM]'='[RANDNUM]"
    }]
    detected_type = "error"
    method_type = "ua"
    cache.insert(url, db_name, boundaries, detected_type, method_type)

@pytest.mark.get
def test_get_cache():
    url = "http://sample.com"
    result = cache.get_cache(url)
    log.info(result)
    assert result is not None