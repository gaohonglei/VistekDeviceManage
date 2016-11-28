#!/usr/bin/env python
# -*- coding=utf-8 -*-

import threading, os, logging, sys

import Vistek.Device as v_device

#import Vistek.Data as v_data
if sys.version_info < (3, 5):
    import DeviceDispatchSessionI
else:
    from . import DeviceDispatchSessionI

if not os.path.exists("log"):
    os.mkdir("log")
log_file = "log\{0}.log".format(__name__)
log_level = logging.DEBUG

logger = logging.getLogger(__name__)
handler = logging.FileHandler(log_file)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(funcName)s:%(lineno)s]  %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(log_level)
class DeviceDispatchServiceI(v_device.DeviceDispatchServiceV1):
    def __init__(self, reaper, name):
        self._service_list = {}#sdk onvif psia 起的会话self._service_list[id] = proxy  proxy = v_device.DeviceDispatchSessionPrx.uncheckedCast(c.adapter.addWithUUID(session))
        self._session_map = {}#{uuid:session}session = DeviceDispatchSessionI.DeviceDispatchSessionI(unique_id)
        self._reaper = reaper#检测_sessions中超时的对话，并关闭
        self._lock = threading.Lock()
        self._name = name#dispatch
        self._id_list = []#每个DispatchClient id
        self._push_proxy = None#self._center_client.proxy
        self._callback_clients = list()
        self._push_proxy=None#上层设备服务v_device.DeviceDispatchServiceV1Prx.checkedCast(self._conn)
    def setPushProxy(self, proxy):
        if not self._push_proxy:
            self._push_proxy = proxy

    def sessionMap(self):
        return self._session_map

    def data_callback(self, *args, **kwargs):
        clients = self._callback_clients[:]
        print("-----Dispatch Service-----args:{0} kwargs:{1}.".format(args, kwargs))
        for client in clients:
            client.MessageReceived(*args, **kwargs)

    def SubscribeCallback(self, ident, c):
        callback_client = v_device.DeviceCallbackPrx.uncheckedCast(c.con.createProxy(ident))
        self._callback_clients.append(callback_client)

    # def register1(self, id, c):
    #     self._lock.acquire()
    #     try:
    #         if id not in self._id_list:
    #             session = DeviceDispatchSessionI.DeviceDispatchSessionI(self._name)
    #             if session.session_id() not in self._session_map:
    #                 self._session_map[session.session_id()] = session
    #             proxy = v_device.DeviceDispatchSessionPrx.uncheckedCast(c.adapter.addWithUUID(session))
    #             self._service_list[id] = proxy
    #             logger.info("server session create session:{0} timestamp:{1} counts:{2}".format(session, session.timestamp(), len(self._session_map)))
    #             self._reaper.add(proxy, session)
    #             return proxy
    #         else:
    #             return self._service_list[id]
    #     finally:
    #         self._lock.release()

    def register2(self, id, manuc, c):
        self._lock.acquire()
        logger.info("{0}------{1}--------{2}".format(id,manuc,c))
        try:
            if id not in self._id_list:
                unique_id = "{0}:{1}".format(str(id), str(manuc))
                session = DeviceDispatchSessionI.DeviceDispatchSessionI(unique_id)
                proxy = v_device.DeviceDispatchSessionPrx.uncheckedCast(c.adapter.addWithUUID(session))
                self._service_list[id] = proxy
                if unique_id not in self._session_map:
                    self._session_map[unique_id] = session
                self._reaper.add(proxy, session)
                logger.info("server session create session:{0} timestamp:{1}".format(proxy, session.timestamp()))
                return proxy
            else:
                return self._service_list[id]
        finally:
            self._lock.release()

    def PushDeviceStreamInfo(self, urls, c):
        if self._push_proxy:
            self._push_proxy.PushDeviceStreamInfo(urls)
            return 0
        else:
            return -1

    def PushDeviceStreamInfos(self, urls, c):
        if self._push_proxy:
            try:
                logging.info("{0}".format(urls))
                self._push_proxy.PushDeviceStreamInfos(urls)
                return 0
            except:
                return -1
        else:
            return -1

    def unregister(self, id, current=None):
        if id in self._service_list:
            del self._service_list[id]
        else:
            logger.warning("id:{0} not exists.".format(id))
