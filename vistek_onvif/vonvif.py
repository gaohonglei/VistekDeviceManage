#!/usr/bin/env python
# -*- coding:utf-8 -*-

import inspect, time, os, sys, collections
from urlobject import URLObject
from vistek_util import functionTools
import eventlet

try:
    import onvif_wrap
except:
    from . import onvif_wrap
import onvif_global_value
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET

class uri_parser():
    """uri parser"""
    def __init__(self, uri):
        """init function"""
        self.uri = URLObject(uri)
        self.params = self.uri.query.dict
    def user_name(self):
        return self.uri.username

    def password(self):
        return self.uri.password

    def ip(self):
        return self.uri.hostname

    def port(self):
        return self.uri.port

    def add_func_param(self, param):
        self.params.update(param)

    def func_name(self, name):
        query = self.uri.query.dict
        if query.has_key(name):
            return query[name]
        else:
            return ''

    def func_params(self, name):
        query = self.uri.query.dict
        if query[name] == 'register_device':
            self.add_func_param({'ip':self.uri.hostname})
            self.add_func_param({'port':self.uri.port})
            self.add_func_param({'user_name':self.uri.username})
            self.add_func_param({'user_pwd':self.uri.password})
        if self.params.has_key(name):
            self.params.pop(name)
        return self.params

@functionTools.timelimited(5)
def try_process_device(device):
    try:
        func = getattr(onvif_wrap, "try_get_device_info")
        if func:
            # waiter = eventlet.greenthread.spawn(func, device)
            # out_data = waiter.wait()
            out_data = func(device)
            return out_data
        else:
            return None
    except functionTools.TimeoutException:
        print("try onvif device time out!!!")
        return None

def getStatusQueue():
    return onvif_wrap.get_status_queue()

def request_cmd(device_id, uri, params):
    """device cmd"""
    func_lists = dir(onvif_wrap)
    parser = uri_parser(uri)
    parser.add_func_param({'device_id':device_id})
    #print('begin device_id:', device_id, 'uri:', uri, 'params:', params, 'func_param:', parser.func_params('func'))
    func_name = parser.func_name('func')
    if func_name in func_lists:
        cmd_func = getattr(onvif_wrap, func_name)
        cmd_params = parser.func_params('func')
        params_lists = []
        need_args = inspect.getargspec(cmd_func).args
        for call_args in need_args:
            if cmd_params.has_key(call_args):
                params_lists.append(cmd_params.get(call_args))
        out_data = cmd_func(**cmd_params)
        return out_data

def getCurrentDeviceInfo():
    return onvif_global_value.get_current_device_info()

def test_timeout():
    import Vistek.Data as v_data
    device = v_data.DmDevice()
    device.DeviceID = "ddd"
    # device.IP = "172.16.2.190"
    # device.Port = 85
    # device.Username = "888888"
    # device.Password = "888888"
    device.IP = "172.16.1.198"
    device.Port = 80
    device.Username = "admin"
    device.Password = "admin123"
    print("begin time:{0}",time.asctime(time.localtime(time.time())))
    try_process_device(device)
    print("end time:{0}",time.asctime(time.localtime(time.time())))
if __name__ == '__main__':
    # test_timeout()
    out_data = request_cmd('172.16.1.191', "http://admin:12345@172.16.1.191:80/device?func=register_device", '')
    while True:
        out_data = request_cmd('172.16.1.191', "http://172.16.1.191:80/device/meida?func=get_stream_url&channel=1", '')
        time.sleep(5)
    raw_input()

