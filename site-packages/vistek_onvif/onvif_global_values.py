#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
@version: 0.0.1
@author: lee
@license: Apache Licence
@contact: shida23577@hotmail.com
@software: PyCharm Community Edition
@file: onvif_global_values.py
@time: 2016/5/25 10:48
"""
__title__ = ''
__version = ''
__build__ = 0x000
__author__ = 'lee'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 li shi da'

try:
    import Queue
except:
    import queue as Queue
device_list = {}#device_id device_info
def get_device_list():
    global device_list
    return device_list

device_status_list = {}#device_id status
def get_device_status_list():
    global device_status_list
    return device_status_list

device_status_change_count_list = {}#status_id(device_id:channel) count
def get_device_change_count_list():
    global device_status_change_count_list
    return device_status_change_count_list

all_status_queue = Queue.Queue()
def get_all_status_queue():
    global all_status_queue
    return all_status_queue

status_change_queue = Queue.Queue()
def get_status_change_queue():
    global status_change_queue
    return status_change_queue

is_start = False
