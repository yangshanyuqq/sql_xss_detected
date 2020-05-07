# -*- encoding: utf-8 -*-
'''
@File    :   sql.py
@Time    :   2020/04/24 21:12:28
@Author  :   ysy_zi 
'''

# here put the import lib
import sqlite3
import os
import traceback
import json


class Cache:
    def __init__(self, file_name):
        self.file_name = file_name

    def create_cache(self):
        '''
            文件名
            创建缓存数据库到当前目录
        '''
        conn = sqlite3.connect(self.file_name)
        try:
            c = conn.cursor()
            c.execute('''CREATE TABLE SQL_CACHE
                (URL TEXT PRIMARY KEY NOT NULL,
                DB_NAME            CHAR(50),
                BOUNDARIES        CHAR(50),
                DETECTED_TYPE        CHAR(50),
                METHOD_TYPE         CHAR(50));''')
            return True
        except:
            # traceback.print_exc()
            return False
        finally:
            conn.commit()
            conn.close()

    def insert(self, url, db_name, boundaries, detected_type, method_type):
        '''
            新增url,db_name,boundaries,detected_type,method_type
        '''
        if len(boundaries) != 0:
            # 处理boundaries字典
            boundaries = json.dumps(boundaries[0])
        else:
            boundaries = json.dumps(boundaries)
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        # 查重
        cursor = c.execute("SELECT URL from SQL_CACHE WHERE URL = '{}'".format(url))
        if c.fetchone() is None:
            # insert_sql = "INSERT INTO SQL_CACHE (URL,DB_NAME,BOUNDARIES,DETECTED_TYPE) VALUES ('{}','{}','{}','{}')".format(url,db_name,boundaries,detected_type)
            # print(insert_sql)
            c.execute("INSERT INTO SQL_CACHE (URL,DB_NAME,BOUNDARIES,DETECTED_TYPE,METHOD_TYPE) VALUES (?,?,?,?,?)", (url,db_name,boundaries,detected_type,method_type))
        conn.commit()
        conn.close()
    
    def get_cache(self, url):
        '''
            获取缓存中的db_name,boundaries,detected_type
            返回None或者字典
        '''
        data_dict = {}
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT * from SQL_CACHE WHERE URL = '{}'".format(url))
        data = c.fetchone()
        if data == None:
            return False
        else:
            for i,value in enumerate(data):
                if i == 1:
                    data_dict["db"] = value
                elif i == 2:
                    tmo_dict = json.loads(value)
                    tmp_list = []
                    tmp_list.append(tmo_dict)
                    data_dict["boundaries"] = tmp_list
                elif i == 3:
                    data_dict["detected_type"] = value
                elif i == 4:
                    data_dict["method_type"] = value
            return data_dict
