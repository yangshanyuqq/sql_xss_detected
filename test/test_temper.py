import pytest
import sys
sys.path.append("..")
from xss.temper.hex_10 import Hex_10
from xss.temper.hex_16 import Hex_16
from xss.temper.uppercase import UpperCase
from xss.temper.addkeywords import AddKeywords
from xss.setting import LIGHT_MODEL
from xss.setting import HEAVY_MODEL
import logging
logging.basicConfig(level=logging.DEBUG)



def test_hex_10():
    payload = '<img src="javascript:alert(65534);">' 
    logging.debug(Hex_10().temper(payload))

def test_hex_16():
    # payload = 'yy78pq"><iframe src="javascript:alert(1)"><img src="11"' 
    payload = '"javascript:alert(1)"'
    logging.debug(Hex_16().temper(payload).pop())

def test_add_keywords():
    payload = '<script>alert(1)</script>'
    logging.debug(AddKeywords().temper(payload, LIGHT_MODEL))
    logging.debug(AddKeywords().temper(payload, HEAVY_MODEL))

def test_uppercase():
    payload = 'ss"onclick=alert(1)'
    logging.debug(UpperCase().temper(payload, LIGHT_MODEL))
    logging.debug(UpperCase().temper(payload, HEAVY_MODEL))