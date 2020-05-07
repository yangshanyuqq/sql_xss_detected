from HTMLParser import HTMLParser
from lib.core.settings import XSS_TAG_MARKER
from lib.core.settings import XSS_MARKER
import re

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self):
        # 继承父类的构造方法
        super(MyHTMLParser, self).__init__()
        self.xss_list = []  

    def handle_starttag(self, tag, attrs):
        # 遍历属性和值
        
        self.tag = tag
        for attr in attrs:
            key = attr[0]
            value = attr[1]
            # 输出在value时,判断是否在特殊属性内
            if value and key:
                if XSS_MARKER in value:
                    if key in "hrefdatasrc":
                        tmp_dict = {
                            "type": "xss_attr_value",
                            "text": self.get_starttag_text()
                        }
                        self.xss_list.append(tmp_dict)
                    else:
                        tmp_dict = {
                            "type": "normal_attr_value",
                            "text": self.get_starttag_text()
                        }
                        self.xss_list.append(tmp_dict)

    def handle_endtag(self, tag):
        return

    def handle_data(self, data):
        # print ("Encountered some data  :" + data)
        # 当输出值在标签之间时
        if XSS_MARKER in data:
            if self.tag == "script":
                # 判断是否在注释符后面
                flag = re.findall("//.*?" + XSS_MARKER, data)
                if len(flag) == 0:
                    xss_type = "script_data"
                else:
                    xss_type = "exp_script_data"
                tmp_dict = {
                    "type": xss_type,
                    "text": data
                }
                self.xss_list.append(tmp_dict)
            else:
                tmp_dict = {
                    "type": "normal_data",
                    "text": data
                }
                self.xss_list.append(tmp_dict)

""" # instantiate the parser and fed it some HTML
parser = MyHTMLParser()
parser.feed('<html><head><title>Test</title></head>'
            '<body><h1>Parse me!</h1></body></html>') """