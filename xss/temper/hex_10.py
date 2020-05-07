# coding=utf-8
import re
import traceback
import random
from xss.temper.temper import Temper
from xss.setting import LIGHT_MODEL
from xss.setting import HEAVY_MODEL



class Hex_10(Temper):

    def __init__(self):
        super(Hex_10, self).__init__()
        self.keywords = super(Hex_10, self).get_keywords()
        self.payload = None

    def temper(self, payload_set, model=LIGHT_MODEL, **kw):
        """
        10进制编码 将 <img src='javascript:alert(1)'>变成
        <IMG SRC=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;
        &#39;&#88;&#83;&#83;&#39;&#41;>
        只变换html标签内部
        :param payload_set: 
        :param model: 
        :param kw: 
        :return: 
        """
        temp_payload_set = payload_set
        if not isinstance(payload_set, set):
            payload_set = set()
            payload_set.add(temp_payload_set)
        payloads = set()
        for payload in payload_set:
            self.payload = payload
            payloads.add(self.keyword_tenhex(payload, 1))
            payloads.add(self.keyword_tenhex(payload, 2))
        return payloads

    def keyword_tenhex(self, str, model=1):
        """
        将src, href中的标签10进制化
        两种模式
        &#106;
        &#0000106
        :param str: 
        :return: 
        """
        encode_str = ""
        result_str = ""
        try:
            link_content = re.findall('(?:src|href)=(".*?")', str, re.S)[0]
            if "javascript" in link_content:
                for char in link_content.replace("\"", ""):
                    if model == 1:
                        encode_str += "&#{};".format(ord(char))
                    elif model == 2:
                        encode_str += "&#0{}".format(ord(char))
                result_str = str.replace(link_content, encode_str)
        except IndexError:
            pass
        return result_str

if __name__ == "__main__":
    payload = '<img src="javascript:alert(65534);">'
    payloads = set()
    payloads.add(payload)
    print(Hex_10().temper(payloads))
    # print (Hex10().temper(payload,))
