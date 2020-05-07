#!/usr/bin/env python


import re
from lub.utils.url import Url
from lib.core.settings import WAF_ATTACK_VECTORS

__product__ = "360 Web Application Firewall (360)"

def detect(urls):
    retval = False

    for vector in WAF_ATTACK_VECTORS:
        if urls.params_num > 0:
            urls.url = urls.url + "&" + vector
        else:
            urls.url = urls.url + vector
            headers = urls.http_request().headers
            

    return retval