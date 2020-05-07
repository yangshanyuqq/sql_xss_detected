import requests
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
import random
import string
import re
from lib.utils.page import similar_web
from itertools import chain
import traceback

import sys
import threading
from subprocess import Popen,PIPE
from urllib import parse
from urllib.parse import quote
import traceback
from functools import reduce


class Url:
    def __init__(self, url, method, data, headers):
        self.url = url
        self.method = self.origin_method = method
        self.header_method = ""
        # post数据
        self.data = data
        self.origin_data = self.data.copy()
        # 普通header头部数据
        self.headers = headers
        self.origin_headers = self.headers.copy()
        # cookie数据
        # self.headers["cookie"]
        self.cookies = self.headers["Cookie"]
        self.params = self.get_params()
        self.params_num = len(self.params)
        self.request = self.http_request(self.url)
        self.f_requests = self.get_f_requests()

    # 给参数赋值
    def url_replacer(self, target_key, target_value, new_value, url=""):
        '''
            给某个参数赋某值
            url默认为对象的url
            returns: url或者data字典
        '''
        # 赋默认值
        if url == "":
            url = self.url
        if self.method == "get":
            new_url = url.replace(target_key + "=" + target_value, target_key + "=" + new_value)
            return new_url
        elif self.method == "post":
            tmp_data = self.origin_data.copy()
            for key,value in self.origin_data.items():
                if target_key == key and target_value == value:
                    tmp_data[key] = new_value
            return tmp_data
        elif self.method == "cookie":
            new_cookies = self.cookies.replace(target_key + "=" + target_value, target_key + "=" + new_value)
            return new_cookies
        else:
            return new_value
        

    def url_replacer_all(self, new_value, url=""):
        '''
            给所有参数后面添加一个值
            url默认为该对象的url
            returns: url
        '''
        if url == "":
            url = self.url
        # 为get参数赋值
        if self.method == "get":
            for param_dict in self.params:
                url = url.replace("=" + param_dict["value"], "=" + param_dict["value"] + new_value)
        elif self.method == "post":
            for key,value in self.data.items():
                self.data[key] = new_value
        return url

    # 判断是否为数字
    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass
    
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
    
        return False

    # 判断参数值类型
    def get_params(self):
        '''
            封装成列表字典型
            [
                {"key":"xx", "value":"yy"},
                {"key":"zz", "value":"cc"},
            ]
        '''
        params_list = []
        if self.method == "cookie":
            cookies_list = self.cookies.split(";")
            for cookie_param in cookies_list:
                key_value = cookie_param.split("=")
                tmp_dict = {"key": key_value[0], "value": key_value[1]}
                params_list.append(tmp_dict)

        elif self.method == "get":
            params = parse.parse_qs(parse.urlparse(self.url).query)
            for key, value in params.items():
                tmp_dict = {"key": key, "value": value[0]}
                params_list.append(tmp_dict)

        elif self.method == "post":
            for key,value in self.data.items():
                tmp_dict = {"key": key, "value": value}
                params_list.append(tmp_dict)

        elif self.method == "ua":
            tmp_dict = {
                "key": "ua_param", "value": self.headers["User-Agent"]
            }
            params_list.append(tmp_dict)

        elif self.method == "referer":
            tmp_dict = {
                "key": "referer_param", "value": self.headers["Referer"]
            }
            params_list.append(tmp_dict)
        return params_list

    def get_f_requests(self):
        '''
            获取每个参数的报错页面
            返回每个参数的报错页面列表
            returns: []
        '''
        f_requests = []
        if self.method == "get":
            for param_dict in self.params:
                new_url = self.url_replacer(param_dict["key"], param_dict["value"], param_dict["value"] + "'")
                f_requests.append(self.http_request(new_url))
        elif self.method == "post":
            for key,value in self.data.items():
                new_url = self.url_replacer(key, value, value + "'")
                f_requests.append(self.http_request(new_url))
        return f_requests

    # http请求函数, 返回返回包的内容
    def http_request(self, url):
        if url == []:
            return False
        if self.method == "cookie":
            self.headers["Cookie"] = url
        elif self.method == "ua":
            self.headers["User-Agent"] = url
        elif self.method == "referer":
            self.headers["Referer"] = url

        if self.origin_method == "get":
            try:
                r = requests.get(url = url, headers = self.headers, timeout = 10)
                return r
            except requests.exceptions.ReadTimeout:
                return "timeout"
            except:
                traceback.print_exc()
                return False

        elif self.origin_method == "post":
            try:
                if self.method != "post":
                    r = requests.post(url = self.url, headers = self.headers, data = self.data, timeout = 10)
                else:
                    if url == self.url:
                        return requests.post(url = self.url, headers = self.headers, data = self.data, timeout = 10)
                    r = requests.post(url = self.url, headers = self.headers, data = url, timeout = 10)
                # 还原参数
                self.data = self.origin_data.copy()
                return r
            except requests.exceptions.ReadTimeout:
                return "timeout"
            except:
                traceback.print_exc()
                return False

    def check_url_page(self, id, url):
        '''
            页面相似度算法
            查看某个参数的页面相似度
            返回bool
        '''
        # 新页面
        r = self.http_request(url)

        if r and r != "timeout":
            # 真页面
            html1 = self.request.text
            # 假页面
            if self.method not in ["get", "post"]:
                html2 = self.f_requests[0].text
            else:
                html2 = self.f_requests[id].text
            html3 = r.text
            percent = similar_web(html1, html3)
            percent2 = similar_web(html2, html3)
            # print(percent, percent2)
            if percent > 0.985 and percent2 <= 0.985:
                return True
            else:
                return False

    def check_url_time(self, url):
        '''
            延时时间和所设置时间对比,判断是否存在延时注入
            returns: bool
        '''
        r = self.http_request(url)
        if r:
            # 超时直接说明存在延时
            if r == "timeout":
                return True
            else:
                time = r.elapsed.seconds
                if  time >= 5:
                    return True
        return False


    def http_payload(self, param, payload, boundaries):
        '''
            后面才想到要封装的,单个payload和boundaries
            returns: url or url_list
        '''
        # 随机数字&字符
        rand_num = str(random.randint(1000,9999))
        rand_num2 = str(random.randint(1000,9999))
        rand_str = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        rand_str2 = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        if len(boundaries) == 1:
            boundarie_dict = boundaries[0]
            payload = boundarie_dict["prefix"] + payload + boundarie_dict["suffix"]
            payload = payload.replace('[RANDSTR]',rand_str).replace('[RANDNUM2]',rand_num2).replace('[RANDSTR2]',rand_str2)
            url = self.url_replacer(param["key"], param["value"], param["value"] + payload)
            return url
        else:
            url_list = []
            for boundarie_dict in boundaries:
                payload2 = boundarie_dict["prefix"] + payload + boundarie_dict["suffix"]
                payload2 = payload2.replace('[RANDSTR]',rand_str).replace('[RANDNUM2]',rand_num2).replace('[RANDSTR2]',rand_str2)
                url = self.url_replacer(param["key"], param["value"], param["value"] + payload2)
                url_list.append(url)
            return url_list

    def http_request_payload(self, param, boundaries, payload_dict, is_expression=False, is_version=False):
        '''
            遍历某个参数单个payload_dict并返回url_list
            returns: [] or [], []
        '''
        new_url_list = []
        new_version_list = []
        for boundarie_dict in boundaries:
            # 随机数字&字符
            rand_num = str(random.randint(1000,9999))
            rand_num2 = str(random.randint(1000,9999))
            rand_str = ''.join(random.sample(string.ascii_letters + string.digits, 4))
            rand_str2 = ''.join(random.sample(string.ascii_letters + string.digits, 4))
            if is_expression:
                payload = boundarie_dict["prefix"] + "and(" + payload_dict["expression"] + ")" + boundarie_dict["suffix"]
            else:
                payload = boundarie_dict["prefix"] + payload_dict["payload"] + boundarie_dict["suffix"]
            payload = payload.replace('[RANDNUM]',rand_num).replace('[RANDSTR]',rand_str).replace('[RANDNUM2]',rand_num2).replace('[RANDSTR2]',rand_str2)
            # 对该参数进行检测          
            new_url = self.url_replacer(param["key"],param["value"],param["value"] + payload)
            new_url_list.append(new_url)
            if is_version:
                new_version_list.append(payload_dict["version"])
        if is_version:
            return new_url_list, new_version_list
        else:
            return new_url_list            

    def http_request_payloads(self, param, boundaries, payloads, is_expression = False, is_version = False):
        '''
            遍历payload或者表达式
            返回二维url列表
            returns: [] or [], []
        '''
        # 增加一个返回version列表
        version_list = []
        new_url_list = []
        # 遍历boundaries和expressions
        for payload_dict in payloads:
            if is_version:
                tmp_url_list, tmp_version_list = self.http_request_payload(param, boundaries, payload_dict, is_expression, is_version)
                new_url_list.append(tmp_url_list)
                version_list.append(tmp_version_list)
            else:
                tmp_url_list = self.http_request_payload(param, boundaries, payload_dict, is_expression, is_version)
                new_url_list.append(tmp_url_list)
        if is_version:
            return list(chain.from_iterable(new_url_list)), list(chain.from_iterable(version_list))
        else:
            return list(chain.from_iterable(new_url_list))

    def check_keyword(self, url, keyword, is_not_re=True):
        '''
        页面源码正则匹配关键字
        returns: []
        '''
        r = self.http_request(url)
        if is_not_re:        
            keyword = keyword.replace('(','\(').replace(')','\)')
        if r:
            page_text = r.text
            result = re.findall(keyword, page_text)
            if result and len(result) != 0:
                return result
            else:
                return False
        return False

    def check_keywords(self, url, keywords):
        '''
            页面源码匹配多个关键字
            只要有一个不为空就返回True
        '''
        r = self.http_request(url)
        if r:
            page_text = r.text
            for keyword in keywords:
                if len(re.findall(keyword, page_text)) != 0:
                    return True
        return False

