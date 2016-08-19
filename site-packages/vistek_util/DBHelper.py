#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
@version: 0.0.1
@author: lee
@license: Apache Licence
@contact: shida23577@hotmail.com
@software: PyCharm Community Edition
@file: DBHelper.py
@time: 2016/6/7 15:25
"""
__title__ = ''
__version = ''
__build__ = 0x000
__author__ = 'lee'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 li shi da'

import sqlalchemy, traceback, DBTypes
import threading
from functools import partial
class SQLLiteHelper():
    def __init__(self, db_str):
        SQLLiteHelper.CreateDB(db_str)
        SQLLiteHelper.initDB()
    __DB__ = None
    __SESSION__ = None
    __MUTEX__ = threading.Lock()
    __INITMUTEX__ = threading.Lock()
    __INIT__ = False
    @staticmethod
    def CreateDB(db_str, show_flag=False):
        with SQLLiteHelper.__MUTEX__:
            if db_str is not None and SQLLiteHelper.__DB__ is None:
                SQLLiteHelper.__DB__ = sqlalchemy.create_engine(db_str, echo=show_flag)
            if SQLLiteHelper.__DB__ is not None and SQLLiteHelper.__SESSION__ is None:
                SQLLiteHelper.__SESSION__ = sqlalchemy.orm.sessionmaker(SQLLiteHelper.__DB__)
            return SQLLiteHelper.__DB__

    @staticmethod
    def initDB():
        with SQLLiteHelper.__INITMUTEX__:
            if SQLLiteHelper.__DB__ is not None and not SQLLiteHelper.__INIT__:
                DBTypes.TableBase.metadata.create_all(bind=SQLLiteHelper.__DB__)
                SQLLiteHelper.__INIT__ = True

    @staticmethod
    def dropDB():
        if SQLLiteHelper.__DB__ is not None:
            DBTypes.TableBase.metadata.drop_all(bind=SQLLiteHelper.__DB__)

    @staticmethod
    def GetSession():
        if SQLLiteHelper.__SESSION__ is not None:
            return SQLLiteHelper.__SESSION__()

    def add(self, content):
        try:
            session = SQLLiteHelper.GetSession()
            if session is not None:
                session.add(content)
                session.commit()
        except:
            if session is not None:
                session.rollback()
            traceback.print_exc()
        finally:
            session.close()

    def remove(self, content):
        try:
            session = SQLLiteHelper.GetSession()
            if session is not None and content is not None:
                session.delete(content)
                session.commit()
        except:
            if session is not None:
                session.rollback()
            traceback.print_exc()
        finally:
            session.close()

    def update(self, func, *args, **kwargs):
        try:
            session = SQLLiteHelper.GetSession()
            if session is not None and func is not None:
                session_func = partial(func, session)
                session_func(*args, **kwargs)
        except:
            if session is not None:
                session.rollback()
            traceback.print_exc()
        finally:
            session.close()
    def exe_cmd(self, func, *args, **kwargs):
        try:
            session = SQLLiteHelper.GetSession()
            if session is not None and func is not None:
                session_func = partial(func, session)
                return session_func(*args, **kwargs)
        except:
            if session is not None:
                session.rollback()
            traceback.print_exc()
        finally:
            session.close()
    def alter(self, content):
        pass


