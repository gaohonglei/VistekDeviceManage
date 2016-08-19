#!/usr/bin/env python
# -*- coding=utf-8 -*-
import Vistek.Device as v_device
import threading, sys, Ice, time


class SessionProxyPair:
    def __init__(self, p, s):
        self.proxy = p
        self.session = s

class SessionRefreshThread(threading.Thread):
    def __init__(self, logger, timeout, session):
        threading.Thread.__init__(self)
        self._logger = logger
        self._session = session
        self._timeout = timeout
        self._terminated = False
        self._cond = threading.Condition()

    def run(self):
        self._cond.acquire()
        try:
            while not self._terminated:
                self._cond.wait(self._timeout)
                if not self._terminated:
                    try:
                        self._session.refresh()
                    except Ice.LocalException as ex:
                        self._logger.warning("SessionRefreshThread: " + str(ex))
                        self._terminated = True
        finally:
            self._cond.release()

    def terminate(self):
        self._cond.acquire()
        try:
            self._terminated = True
            self._cond.notify()
        finally:
            self._cond.release()


class ReapThread(threading.Thread):
    """
    检测_sessions中超时的对话，并关闭
    """
    def __init__(self, time_out):
        threading.Thread.__init__(self)
        self._timeout = time_out
        self._terminated = False
        self._cond = threading.Condition()
        self._sessions = []#SessionProxyPair(proxy, session)

    def run(self):
        self._cond.acquire()
        try:
            while not self._terminated:
                self._cond.wait(1)
                if not self._terminated:
                    for p in self._sessions:
                        try:
                            #
                            # Session destruction may take time in a
                            # real-world example. Therefore the current time
                            # is computed for each iteration.
                            #
                            if (time.time() - p.session.timestamp()) > self._timeout:
                                print("cur:{0} old:{1}".format(time.time(), p.session.timestamp()))
                                name = p.session.getName()
                                #p.proxy.destroy()
                                print("time:", time.asctime(time.localtime(time.time())), "The session " + name + " has timed out.")
                                self._sessions.remove(p)
                        except Ice.ObjectNotExistException:
                            self._sessions.remove(p)
        finally:
            self._cond.release()

    def terminate(self):
        self._cond.acquire()
        try:
            self._terminated = True
            self._cond.notify()

            self._sessions = []
        finally:
            self._cond.release()

    def add(self, proxy, session):
        self._cond.acquire()
        try:
            self._sessions.append(SessionProxyPair(proxy, session))
        finally:
            self._cond.release()

class ClientThread(threading.Thread):
    def __init__(self, srvice, endpoints):
        threading.Thread.__init__(self)
        self._communicator = Ice.initialize(sys.argv)
        self._service = srvice
        self._endpoints = endpoints
        self._unique_str = str(self._service) + str(self._endpoints)
        self._session = None
        self._base_svc = None
        self._status_svc = None
    def session(self):
        return self._session

    def base_svc(self):
        return self._base_svc

    def status_svc(self):
        return self._status_svc

    def run(self):
        base = self._communicator.stringToProxy(self._unique_str)
        factory = v_device.SessionFactoryPrx.checkedCast(base)

        if not factory:
            print(sys.args[0] + ": invalid proxy")
            return 1
        name = 'DeviceService'
        self._session = factory.create(name)
        self._base_svc = self._session.create_device_service()
        self._status_svc = self._session.create_device_status_service()
        print("session:", self._session, type(self._session))
        #self._queue.put(self._session)
        self._communicator.waitForShutdown()
        #self._client.main(sys.argv, "", self._init_data)
