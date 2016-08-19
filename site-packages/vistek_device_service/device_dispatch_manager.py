#!/usr/bin/env python
# -*- coding=utf-8 -*-

import Vistek.Data as v_data
import Vistek.Device as v_device

import device_center_client
import device_dispatch_client
import device_dispatch_server
import device_process
import threadpool

import multiprocessing, time, threading
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET
HostNodeName = "host"
HostAttrManucName = "manufacture"
HostAttrCfgFileName = "cfg_file"
HostAttrCountName = "counts"
HostSessionServiceName = "SessionFactory"
HostMaxDeviceCount = 500

def do_start_host(manu_type, connect_str, db_config_file=None):
    print("host starts -------")
    if db_config_file is not None:
        client = device_dispatch_client.DispatchClient(manu_type, connect_str, db_config_file)
    else:
        client = device_dispatch_client.DispatchClient(manu_type, connect_str)
    client.start()
    while True:
        time.sleep(1)

class DeviceDispatchManager():
    def __init__(self, center_config, server_config_file, host_cfg_file, manager_type, db_config_file=None):
        center_conn = center_config
        self._xml_cfg_tree = ET.ElementTree()
        name = "dispatch"
        self._manager_type = manager_type
        if db_config_file is not None:
            self._db_config_file = db_config_file
        if manager_type == v_device.RegisterType.rtCheck:
            self._center_client = device_center_client.DeviceCenterClient(center_conn, manager_type)
        else:
            self._dispatch_server = device_dispatch_server.DispatchServer(name, center_conn, server_config_file)
        self._host_cfg_file = host_cfg_file#hikesdk onvif psia
        self._xml_cfg_tree.parse(self._host_cfg_file)
        self._host_client_list = []
        self._try_proc_list = []
        self._host_counts = {}#manuc counts.
        # self._start_host_thrd = threading.Thread(target=DeviceDispatchManager._do_normal, name="start_hosts", args=(self, ))

    def start(self):
        if self._manager_type == v_device.RegisterType.rtCheck:
            self._do_check()
        elif self._manager_type == v_device.RegisterType.rtNormal:
            # self._dispatch_server.start()
            # if self._start_host_thrd:
            #     self._start_host_thrd.start()
            self._do_nomal()
        else:
            print("manager not starting ,type error, type:{0}".format(self._manager_type))

    def _do_check(self):
        self._center_client.start()

    def _do_nomal(self):
        '''
        rtNormal模式下的总start函数
        :return:
        '''
        self._dispatch_server.start()
        while not self._dispatch_server.is_start:
            time.sleep(1)
        root_node = self._xml_cfg_tree.getroot()
        for host in root_node.iter(HostNodeName):
            manu_type = host.get(HostAttrManucName)
            host_count = host.get(HostAttrCountName)
            for item in range(int(host_count)):
                process_name = "{0}-{1}".format(manu_type, item)
                if hasattr(self, "_db_config_file"):
                    host_proc = multiprocessing.Process(target=do_start_host\
                                                        , name= process_name\
                                                        , args=(manu_type, self._dispatch_server.conn_str()\
                                                        , self._db_config_file))
                else:
                    host_proc = multiprocessing.Process(target=do_start_host, name= process_name, args=(manu_type, self._dispatch_server.conn_str(),))
                host_proc.daemon = True
                host_proc.start()
                #client = device_dispatch_client.DispatchClient(manu_type, self._dispatch_server.conn_str())
                #client.start()
                self._host_client_list.append(host_proc)

    def _do_normal(self):
        while True:
            if self._dispatch_server.device_count() and 0 < len(self._dispatch_server.device_count()):
                device_count = self._dispatch_server.device_count()
                for manuc, count in device_count.items():
                    need_start_host_count = 0
                    if manuc in self._host_counts:
                        cur_count = self._host_counts.get(manuc)
                        change_count = count - cur_count
                        if 0 < change_count:
                            need_start_host_count = int(change_count/HostMaxDeviceCount)
                    elif 0 < count:
                        need_start_host_count = int(count/HostMaxDeviceCount) + 1
                    if 0 < need_start_host_count:
                        print("host start")
                        self._host_counts.update({manuc:count})
                        for item in range(need_start_host_count):
                            process_name = "{0}-{1}".format(manuc, item)
                            host_proc = multiprocessing.Process(target=do_start_host, name= process_name, args=(manuc, self._dispatch_server.conn_str(),))
                            #host_proc.daemon = True
                            host_proc.start()
                            self._host_client_list.append(host_proc)
            time.sleep(60)

    def stop(self):
        if self._center_client:
            self._center_client.stop()
        if self._dispatch_server:
            self._dispatch_server.stop()
        for client in self._host_client_list:
            client.terminate()

def test_manager_check():
    manager_check = DeviceDispatchManager("device_dispatch_service:tcp -h localhost -p 54300", "config_dispatch.server", "host_cfg.xml", v_device.RegisterType.rtCheck)
    manager_check.start()
    #raw_input()
def test_manager_normal():
    manager_normal = DeviceDispatchManager("device_dispatch_service:tcp -h localhost -p 54300", "config_dispatch.server", "host_cfg.xml", v_device.RegisterType.rtNormal)
    manager_normal.start()
    #raw_input()

if __name__ == "__main__":
    test_manager_normal()
    #test_manager_normal()
    test_manager_check()
    # manager_check = DeviceDispatchManager("device_dispatch_service:tcp -h 172.16.0.20 -p 54300", "config_dispatch.server", "host_cfg.xml", v_device.RegisterType.rtNormal)
    # manager_check.start()
    #time.sleep(5)
    #manager_normal = DeviceDispatchManager("device_dispatch_service:tcp -h 172.16.0.10 -p 54300", "config_dispatch.server", "host_cfg.xml", v_device.RegisterType.rtNormal)
    #manager_normal.start()
    raw_input()
