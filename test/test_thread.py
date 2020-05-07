import pytest
import sys
sys.path.append("..")
from lib.utils.log import Log
from lib.utils.thread_queue import MyTask,MyThread
from lib.core.settings import gen_fake_header
from lib.utils.url import Url
import queue


def test_1():
    queue_length = 1
    # 先进后出队列
    my__queue = queue.Queue(queue_length*10)
    threads = []
    urls = Url("http://sample.com","test",[],gen_fake_header())
    payload = "test"
    data_payload = "data_test"
    param_id = 1
    top_boundaries = []
    param = "test"
    i = 2
    j = 3

    for i in range(queue_length*10):
        mt = MyTask(urls, payload, data_payload, param_id, top_boundaries, param, i, j)
        my__queue.put_nowait(mt)

    for i in range(queue_length):
        mtd = MyThread(my__queue, payload)
        threads.append(mtd)

    for i in range(queue_length):
        threads[i].start()

    for i in range(queue_length):
        threads[i].join()

    for i in range(queue_length):
        assert threads[i].result == i