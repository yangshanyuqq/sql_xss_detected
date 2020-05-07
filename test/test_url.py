import sys
sys.path.append("..")
from lib.utils.url import Url
from lib.core.settings import gen_fake_header
from lib.core.settings import BOUNDARIES_FILE_NAME
from lib.core.settings import DETECTED_FILE_NAME
import os
from lib.utils.json_file import *
import pytest
import logging
import random
import string
logging.basicConfig(level=logging.DEBUG)



boundaries = get_json("../"+BOUNDARIES_FILE_NAME, "low")
expressions = get_json("../"+DETECTED_FILE_NAME,"mysql")
data = {
    "uname": "admin", "passwd":"admin", "submit":"Submit"
}
urls = Url("http://192.168.45.144:81/sqli-labs-master/Less-1/index.php?id=1&s=2", "get", [], gen_fake_header())
urls2 = Url("http://192.168.45.144:81/sqli-labs-master/Less-1/index.php?id=1&s=2", "post", data, gen_fake_header())
payloads = ["'", '"']
# 随机数字
rand_num = str(random.randint(1000,9999))
rand_str = ''.join(random.sample(string.ascii_letters + string.digits, 4))
parmas = urls.params

@pytest.mark.url
def test_url():
    logging.getLogger("test_url")
    logging.info((boundaries,True))
    logging.info((expressions, True))
    urls.http_request_payloads(parmas[0],boundaries, expressions, True)

@pytest.mark.http
def test_http_request():
    logging.getLogger("test_http")
    logging.info(urls.http_request(urls.url).content)
    logging.info(urls2.http_request(urls.url).headers)
    urls.url = "http://127.0.0.1"
    logging.info(urls.http_request(urls.url).content)

@pytest.mark.keyword
def test_keyword():
    tmp_urls = Url(r"http://192.168.45.1/xss/xssgame/level10.php?name=2&t_sort=ysy%22%3E%3Cimg%20sRc=1/onERRor=%22aLErt(1)", "get", [],gen_fake_header())
    logging.info(tmp_urls.check_keyword(r'http://192.168.45.1/xss/xssgame/level10.php?name=2&t_sort=ysy%22%3E%3Cimg%20sRc=1 onERRor=%22alert(1)', '(<img sRc=1 onERRor="alert".*>)'))

@pytest.mark.similar
def test_similar():
    tmp_urls = Url('http://192.168.45.1/sqli-labs-master/Less-8/index-oracle.php?id=1', "get", [], gen_fake_header())
    logging.info(tmp_urls.check_url_page(0,"http://192.168.45.1/sqli-labs-master/Less-8/index-oracle.php?id=1"))

@pytest.mark.post
def test_http_post():
    data = {
        "uname": "admin", "passwd":"admin", "submit":"Submit"
    }
    change_data = {
        "uname": "ss"
    }    
    tmp_urls = Url("http://192.168.45.144:81/sqli-labs-master/Less-11/index.php", "post", data, gen_fake_header())
    replace_url = tmp_urls.url_replacer("uname", "admin", "admins")
    logging.info(replace_url)
    # 检测post请求
    logging.info(tmp_urls.http_request(replace_url).text)

@pytest.mark.params
def test_params():
    data = {
        "uname": "ysy", "passwd":"ysy", "submit":"Submit"
    }
    urls = Url("http://192.168.45.144:81/sqli-labs-master/Less-20/index.php?id=1", "post", data, gen_fake_header())
    logging.info(urls.headers["User-Agent"])
    logging.info(urls.headers["Referer"])
    logging.info(urls.headers["Cookie"].split(";"))          
    # urls.method = "cookie"
    # logging.info(urls.get_params())