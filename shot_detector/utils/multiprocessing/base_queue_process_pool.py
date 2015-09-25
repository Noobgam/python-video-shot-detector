# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import six
import logging
import multiprocessing

from shot_detector.utils.collections import Condenser


from .queue_worker import QueueWorker
from .function_task import FunctionTask


PROCESSES = multiprocessing.cpu_count()
CHUNK_SIZE = 1024

class BaseQueueProcessPool(object):

    __logger = logging.getLogger(__name__)

    def __init__(self, processes=PROCESSES, chunk_size=CHUNK_SIZE):
        self.processes = processes
        self.task_queue = multiprocessing.JoinableQueue()
        self.result_queue = multiprocessing.Queue()
        self.condenser = Condenser(chunk_size)
        self.queue_size = 0
        self.value_size = 0
        self.worker_list = [
            QueueWorker(
                task_queue = self.task_queue,
                result_queue = self.result_queue,
                worker_number = worker_number
            )
            for worker_number in xrange(self.processes)
        ]

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        #self.join()
        self.close()

    def start(self):
        for worker in self.worker_list:
            worker.start()

    def apply_async(self, func, value, *args, **kwargs):
        self.value_size += 1
        self.condenser.charge(value)
        if self.condenser.is_charged:
            values = self.condenser.get()
            self.map_async(func, values, *args, **kwargs)

    def map_async(self, func, iterable, map_func=None, *args, **kwargs):
        if not map_func:
            map_func = self.map
        task = FunctionTask(
            map_func, func, iterable, self.queue_size, *args, **kwargs
        )
        self.put_task(task)

    @staticmethod
    def map(func, iterable, reduce_func=list, number=None, *args, **kwargs):
        result = (func(item, *args, **kwargs) for item in iterable)
        result = reduce_func(result)
        return (number, result)

    def put_task(self, task):
        self.queue_size += 1
        return self.task_queue.put(task)

    def get_result(self, block=True, timeout=None):
        return self.result_queue.get(block, timeout)

    def close(self):
        self.__logger.info('self.queue_size = %s' % self.processes)
        for i in xrange(self.processes):
            self.task_queue.put(None)

    def join(self, block=True, timeout=None, reduce_func=list):
        self.__logger.info('self.queue_size 1 = %s' % self.task_queue.qsize())
        self.task_queue.join()
        results = self.get_all_results(block, timeout, reduce_func)
        return results

    def get_all_results(self, block=True, timeout=None, reduce_func=list):
        self.__logger.info('self.queue_size 2 = %s' % [self.queue_size, self.value_size])
        result = sorted(self.get_result(block, timeout) for i in xrange(self.queue_size))
        result = reduce_func(result)
        return result

