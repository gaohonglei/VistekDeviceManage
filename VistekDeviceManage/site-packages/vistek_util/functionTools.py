#!/usr/bin/env python
# -*- coding=utf-8 -*-

from threading import Thread
import time

class TimeoutException(Exception):
    pass
try:
    ThreadStop = Thread._Thread__stop
except:
    ThreadStop = Thread._stop

def timelimited(timeout):
    def decorator(function):
        def decorator2(*args,**kwargs):
            class TimeLimited(Thread):
                def __init__(self,_error= None,):
                    Thread.__init__(self)
                    self._error =  _error

                def run(self):
                    try:
                        self.result = function(*args,**kwargs)
                    except Exception as e:
                        self._error =e

                def _stop(self):
                    if self.isAlive():
                        ThreadStop(self)

            t = TimeLimited()
            t.start()
            t.join(timeout)

            if isinstance(t._error,TimeoutException):
                t._stop()
                return None
                #raise TimeoutException('timeout for %s' % (repr(function)))

            if t.isAlive():
                t._stop()
                return None
                #raise TimeoutException('timeout for %s' % (repr(function)))

            if t._error is None:
                return t.result

        return decorator2
    return decorator