# -*- encoding: utf-8 -*-
'''
@File    :   detected.py
@Time    :   2020/04/23 20:48:11
@Author  :   ysy_zi 
'''

# here put the import lib
import os
from dbms.check_dbms import CheckDbms
from lib.utils.url import Url
from lib.utils.cache import Cache
from lib.core.settings import *
from data.json_file import get_json
from lib.utils.page import similar_web
from dbms.check_union import CheckUnion
from lib.utils.log import Log
from xss.check_xss import CheckXss
import argparse


def sql_detected(log, url, method_type, detected_level, shell):
    data = {
        "uname": "admin", "passwd":"admin", "submit":"Submit"
    }
    if method_type == "get":
        urls = Url(url, method_type , [], gen_fake_header())
    else:
        urls = Url(url, method_type , data, gen_fake_header())
    dbms = CheckDbms(urls, log, detected_level, shell)
    dbms.detected()

    # mysql_url_list = [
    #     'http://192.168.45.144:81/sqli-labs-master/Less-1/index.php?id=1',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-2/index.php?id=1',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-3/index.php?id=1',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-8/index.php?id=1',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-9/index.php?id=1',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-11/index.php',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-13/index.php',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-18/index.php',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-19/index.php',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-20/index.php',
    # ]
    # oracle_url_list = [
    #     # 'http://192.168.45.1/sqli-labs-master/Less-1/index-oracle.php?id=1',
    #     # 'http://192.168.45.1/sqli-labs-master/Less-2/index.php?id=1',
    #     # 'http://192.168.45.1/sqli-labs-master/Less-3/index.php?id=1',
    #     # 'http://192.168.45.1/sqli-labs-master/Less-8/index-oracle.php?id=1',
    #     'http://192.168.45.1/sqli-labs-master/Less-9/index-oracle.php?id=1',
    #     # 'http://192.168.45.1/sqli-labs-master/Less-11/index.php'
    #     # 'http://192.168.45.1/sqli-labs-master/Less-13/index.php'
    # ]
    # mssql_url_list = [
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-1/index-mssql.php?id=1',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-2/index.php?id=1',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-3/index.php?id=1',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-8/index-mssql.php?id=1',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-9/index-mssql.php?id=1',
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-11/index.php'
    #     # 'http://192.168.45.144:81/sqli-labs-master/Less-13/index.php'
    # ]
    # for url in mysql_url_list:
    #     mysql_urls = Url(url, "get" , [], gen_fake_header())
    #     # 11 13
    #     # mysql_urls = Url(url, "post" , data, gen_fake_header())
    #     dbms = CheckDbms(mysql_urls, log, "low")
    #     dbms.detected()
    # """ for url in oracle_url_list:
    #     oracle_urls = Url(url, "get" , [], gen_fake_header())
    #     dbms = CheckDbms(oracle_urls, log)
    #     dbms.detected() """
    # """ for url in mssql_url_list:
    #     mssql_urls = Url(url, "get" , [], gen_fake_header())
    #     dbms = CheckDbms(mssql_urls, log)
    #     dbms.detected() """
    

def xss_detected(log, url):
    log.info("开始检测xss")
    """ xss_url_list = [
        "http://192.168.45.1/xss/xssgame/level1.php?name=1&x=2",
        "http://192.168.45.1/xss/xssgame/level2.php?keyword=2",
        "http://192.168.45.1/xss/xssgame/level3.php?keyword=2",
        "http://192.168.45.1/xss/xssgame/level4.php?keyword=2",
        "http://192.168.45.1/xss/xssgame/level5.php?keyword=2",
        "http://192.168.45.1/xss/xssgame/level6.php?keyword=2",
        "http://192.168.45.1/xss/xssgame/level7.php?keyword=2",
        r"http://192.168.45.1/xss/xssgame/level8.php?keyword=2&submit=%E6%B7%BB%E5%8A%A0%E5%8F%8B%E6%83%85%E9%93%BE%E6%8E%A5",
        "http://192.168.45.1/xss/xssgame/level9.php?name=2", 
        "http://192.168.45.1/xss/xssgame/level9a.php?name=2",
        "http://192.168.45.1/xss/xssgame/level10.php?name=2",
        "http://192.168.45.1/xss/xssgame/level11.php?name=2",
    ]
    for url in xss_url_list: """
    xss_urls = Url(url, "get" , [], gen_fake_header())
    xss = CheckXss(xss_urls, log)
    xss_result = xss.detected()
    log.debug('检测出xss_payload:')
    log.debug(xss_result)
    
def main():
    # 创建缓存数据库
    cache = Cache(SQLITE_FILE_NAME)
    cache.create_cache()
    logs_root_dir = LOG_DIR_NAME
    
    """ # 检测sql注入,并生成检测的报告
    sql_log_name = os.path.join(logs_root_dir, "sql.log")
    sql_log = Log(sql_log_name)
    sql_detected(sql_log) """

    """ # 检测xss,并生成检测的报告
    xss_log_name = os.path.join(logs_root_dir, "xss.log")
    xss_log = Log(xss_log_name)
    xss_detected(xss_log) """
    
    parser = argparse.ArgumentParser()
    parser.description='please input url and method_type and detected_level...'
    parser.add_argument("-u", "--url", help="input url", type=str)
    parser.add_argument("-m", "--method_type", help="input get or post",  type=str, default="get")
    parser.add_argument("-v", "--detected_level", help="input low or high", type=str, default="low")
    parser.add_argument("-t", "--detected_type", help="input xss or sql", type=str)
    parser.add_argument("-o", "--shell", help="input anything", type=str, default=None)
    parser.add_argument("-r", "--file_name", help="input file_name", type=str, default=None)
    args = parser.parse_args()

    url = args.url
    method_type = args.method_type
    detected_level = args.detected_level
    detected_type = args.detected_type
    shell = args.shell
    file_name = args.file_name

    # print(url)
    # print(detected_type)
    # return

    if file_name is not None:
        with open(file_name, 'r') as f1:
            url_list = f1.readlines()
            for i in range(0, len(url_list)):
                url_list[i] = url_list[i].strip('\n')
    else:
        url_list = []
        url_list.append(url)

    for url in url_list:
        print(url)
        if detected_type == "xss":
            xss_log_name = os.path.join(logs_root_dir, "xss.log")
            xss_log = Log(xss_log_name)
            xss_detected(xss_log, url)
        else:
            sql_log_name = os.path.join(logs_root_dir, "sql.log")
            sql_log = Log(sql_log_name)
            sql_detected(sql_log, url, method_type, detected_level, shell)    
            


if __name__ == "__main__":
    main()
    print("ddddddd")
