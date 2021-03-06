#!/usr/bin/env python
#coding=utf-8

import Vistek.Device as v_device
import Vistek.Data as v_data

import uuid, threading, time, Ice, logging, os

if not os.path.exists("log"):
    os.mkdir("log")
log_file = "log\{0}.log".format(__name__)
log_level = logging.DEBUG

logger = logging.getLogger(__name__)
handler = logging.FileHandler(log_file)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(funcName)s:%(lineno)s]  %(message)s")
logger.disabled = False
class DeviceDispatchSessionI(v_device.DeviceDispatchSession):
    def __init__(self, name):
        self._name = name
        self._device_list = dict()#设备列表,已经存在的设备则，不在需要添加里面，device_dispatcher服务分发的设备
        self._delay_push_status_list = list()
        self._push_session = None#client.__center_session
        self._id = uuid.uuid4()
        self._device_list_mutex = threading.Lock()#操作self._device_list时必须加锁
        self._timestamp = time.time()
        self._lock = threading.Lock()
        self._destroy = False # true if destroy() was called, false otherwise.

    def session_id(self):
        return self._id

    def setDispatchDevices(self, device_list):
        pass

    def DeviceListsCount(self):
        with self._device_list_mutex:
            return len(self._device_list)
    def PushDevice(self, device_id, device):
        with self._device_list_mutex:
            if device_id not in self._device_list:
                self._device_list[device_id] = device

    def PopDevice(self, device_id):
        with self._device_list_mutex:
            if device_id in self._device_list:
                self._device_list.pop(device_id)

    def PushAlterDevice(self, device):
        pass

    def SetPushSession(self, session):
            self._push_session = session

    def GetDeviceList(self, current=None):
        with self._device_list_mutex:
            return list(self._device_list.values())

    def UpdateDeviceList(self, list, current=None):
        if self._push_session:
            try:
                self._push_session.UpdateDeviceList(list)
                return 0
            except Exception,ex:
                logger.info("Exception:{0}".format(ex))
        return 1

    def KeepAlive(self, c):
        self._lock.acquire()
        try:
            if self._destroy:
                raise Ice.ObjectNotExistException()
            self._timestamp = time.time()
        finally:
            self._lock.release()

    def getName(self):
        self._lock.acquire()
        try:
            if self._destroy:
                raise Ice.ObjectNotExistException()
            return self._name
        finally:
            self._lock.release()

    def destroy(self, c):
        self._lock.acquire()
        try:
            if self._destroy:
                raise Ice.ObjectNotExistException()
            self._destroy = True
            logger.warning("time:", time.asctime(time.localtime(time.time())),"The session " + self._name + " is now destroyed.")
            try:
                c.adapter.remove(c.id)
                #for p in self._objs:
                    #c.adapter.remove(p.ice_getIdentity())
            except Ice.ObjectAdapterDeactivatedException as ex:
                # This method is called on shutdown of the server, in
                # which case this exception is expected.
                pass
            #self._objs = []
        finally:
            self._lock.release()

    def timestamp(self):
        self._lock.acquire()
        try:
            if self._destroy:
                raise Ice.ObjectNotExistException()
            return self._timestamp
        finally:
            self._lock.release()

    def PushDeviceStatus(self, info, current=None):
        if self._push_session:
            try:
                self._push_session.PushDeviceStatus(info)
                return 0
            except Exception,ex:
                logger.info("Exception:{0}".format(ex))
        return 1

    def PushDeviceStatusList(self, info_list, current=None):
        pass
