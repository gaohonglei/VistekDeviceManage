#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
@version: 0.0.1
@author: lee
@license: Apache Licence
@contact: shida23577@hotmail.com
@software: PyCharm Community Edition
@file: device_watch_server.py
@time: 2016/6/2 10:12
"""
__title__ = ''
__version = ''
__build__ = 0x000
__author__ = 'lee'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 li shi da'

import Ice

import threading, os, time
import vistek_util.DeviceWatchServiceI as DeviceWatchServiceI
class DeviceWatchServer():
    def __init__(self, server_config_file):
        self._service_name = "DeviceWatching"
        self._communicator = None
        self._port = 65000
        if os.path.exists(server_config_file):
            self.__init_ice_config(server_config_file)
        else:
            raise "server config file is empty!!"
        if self._communicator is not None:
            if getattr(self, "_adapter", None) is None:
                self._adapter = self._communicator.createObjectAdapter(self._service_name)
        self._start_thrd = threading.Thread(target=self._do_start, name="boot_watch_server", args={self, })

    def __init_ice_config(self, watch_server_config_file):
        init_data = Ice.InitializationData()
        center_pros = Ice.createProperties(sys.argv)
        init_data.properties.load(watch_server_config_file)
        # center_pros.setProperty("Ice.MessageSizeMax", "5120")
        # center_pros.setProperty("Ice.RetryIntervals", "0 100 500 1000")
        # center_pros.setProperty("Ice.ThreadPool.Client.Size", "8")
        # map(lambda a, b:center_pros.setProperty(key, item), properties.items())
        # center_pros.setProperty(key, item)
        # for key, item in properties.items():
        # init_data.properties = center_pros
        self._communicator = Ice.initialize(sys.argv, init_data)
        return self._communicator

    def _do_start(self):
        watch_service = DeviceWatchServiceI.DeviceWatchService()
        self._adapter.add(watch_service)
        self._adapter.activate()
        self._communicator.waitForShutDown()

    def start(self):
        if self._start_thrd:
            if not self._start_thrd.isDaemon():
                self._start_thrd.setDaemon(True)
            self._start_thrd.start()

    def stop(self):
        if self._start_thrd and self._start_thrd.is_alive():
            self._start_thrd.join(timeout=5)
        del self._start_thrd

if __name__ == "__main__":
    watch_server = DeviceWatchServer("cofing_watch.config")
    watch_server.start()
    while 1:
        time.sleep(1)
