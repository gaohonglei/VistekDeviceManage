#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
@version: 0.0.1
@author: lee
@license: Apache Licence
@contact: shida23577@hotmail.com
@software: PyCharm Community Edition
@file: DeviceWatchServiceI.py
@time: 2016/6/2 13:28
"""
__title__ = ''
__version = ''
__build__ = 0x000
__author__ = 'lee'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 li shi da'

import Vistek.Device as v_device
import eventlet, MySQLdb
from DBUtils.PooledDB import PooledDB
from MySQLdb.cursors import DictCursor
import DBHelper, DBTypes, datetime
class MySqlDbHelper():
    __pool = None
    __host = None
    __port = None
    __user = None
    __pwd = None
    __dbname = None
    def __init__(self, host, user, pwd, dbname, port = None, config_file=None):
        self._host, self._user, self._pwd, self._dbname  = host, user, pwd, dbname
        MySqlDbHelper.__host, MySqlDbHelper.__user, MySqlDbHelper.__pwd, MySqlDbHelper.__dbname = host, user, pwd, dbname
        if port is None:
            self._port = 3306
        else:
            self._port = port
        MySqlDbHelper.__port = self._port
        self._conn = MySqlDbHelper.__get_connect()
        if self._conn is not None:
            self._cursor = self._conn.cursor()

    @staticmethod
    def __get_connect():
        if MySqlDbHelper.__pool is None:
            # print("come here{0}{1}{2}{3}".format(MySqlDbHelper.__host, MySqlDbHelper.__port,MySqlDbHelper.__user,MySqlDbHelper.__pwd))
            __pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=30\
                                      , host=MySqlDbHelper.__host, port=MySqlDbHelper.__port\
                                      , user=MySqlDbHelper.__user, passwd=MySqlDbHelper.__pwd \
                                      , db=MySqlDbHelper.__dbname, use_unicode=False\
                                      , charset='utf8', cursorclass=DictCursor)
        return __pool.connection()

    def is_cmd_available(self, cmd):
        return True

    def exe_cmd(self, cmd):
        if self._conn is not None and self.is_cmd_available(cmd):
            # count = self._exe_handle.execute(cmd)
            count = self._cursor.execute(cmd)
            result_rows = []
            if 0 < count:
                #out = [row for row in self._cursor.fetchall()]
                result_rows.extend([row for row in self._cursor.fetchall()])
                #result_rows.extend([row for row in self._exe_handle.fetchall()])
            return (count, result_rows)
        return None

    def getAll(self,sql,param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        if count>0:
            result = self._cursor.fetchall()
        else:
            result = False
        return result

    def getOne(self,sql,param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        if count>0:
            result = self._cursor.fetchone()
        else:
            result = False
        return result

    def getMany(self,sql,num,param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        if count>0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        return result

    def insertOne(self,sql,value):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list
        @return: insertId 受影响的行数
        """
        self._cursor.execute(sql,value)
        return self.__getInsertId()

    def insertMany(self,sql,values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql,values)
        return count

    def __getInsertId(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        return result[0]['id']

    def __query(self,sql,param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        return count

    def update(self,sql,param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql,param)

    def delete(self,sql,param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql,param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self,option='commit'):
        """
        @summary: 结束事务
        """
        if option=='commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self,isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd==1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._conn.close()

class DeviceWatchServiceSqliteI(v_device.DeviceWatchService):
    def __init__(self, db_str):
        if db_str is not None:
            self._sqlite_helper = DBHelper.SQLLiteHelper(db_str)
        else:
            raise "db str is empty"

    def GetPhysicInfo(self, c):
        def selectPhysicInfo(session):
            result = session.execute("select deviceregisterinfo.serviceID\
            , deviceserverinfo.cpuCount\
            , deviceserverinfo.physicalCpuCount\
            , serviceloadinginfo.cpuUseRate\
            , deviceserverinfo.memSize\
            , serviceloadinginfo.useMemory\
            , serviceloadinginfo.availableMemory\
            , serviceloadinginfo.memUseRate\
            , deviceregisterinfo.registerSuccessCount\
            , deviceregisterinfo.registerFailCount\
            , deviceregisterinfo.registerSuccessDeviceList\
            , deviceregisterinfo.registerFailDeviceList\
            , serviceloadinginfo.create_time \
            from deviceregisterinfo, deviceserverinfo, serviceloadinginfo \
            where serviceloadinginfo.create_time > datetime('now','localtime','-1 minute') \
            and serviceloadinginfo.create_time <= datetime('now', 'localtime') \
            and (serviceloadinginfo.create_time) = datetime(deviceregisterinfo.create_time) \
            and (deviceregisterinfo.create_time) > datetime('now', 'localtime', '-1 minute') \
            and (deviceregisterinfo.create_time) <= datetime('now', 'localtime');")
            if result is not None:
                return result.fetchall()

        if hasattr(self, "_sqlite_helper") and self._sqlite_helper is not None:
            result = self._sqlite_helper.exe_cmd(selectPhysicInfo)
            print("result:", result)
            if result is not None and 0 < len(result):
                base_info_list = []
                for item in result:
                    base_info = v_device.BasePhyServiceInfo()
                    base_info.serviceID = item[0]
                    cpu_info = v_device.CpuInfo()
                    cpu_info.cpuUseRate = float(item[3])
                    cpu_info.cpuCount = int(item[1])
                    cpu_info.physicCpuCount = int(item[2])
                    if base_info.cpuinfovalue is None:
                        base_info.cpuinfovalue = cpu_info
                    mem_info = v_device.MemInfo()
                    mem_info.memSize = float(item[4])
                    mem_info.useMem = float(item[5])
                    mem_info.memUseRate = float(item[7])
                    mem_info.aviableMemSize = float(item[6])
                    if base_info.meminfovalue == None:
                        base_info.meminfovalue = mem_info
                    register_info = v_device.DeviceRegisterInfo()
                    register_info.registerSuccessCount = int(item[8])
                    register_info.registerFailCount = int(item[9])
                    register_info.registerSuccessDeviceList = str(item[10])
                    register_info.registerFailDeviceList = str(item[11])
                    if base_info.registerinfovalue is None:
                        base_info.registerinfovalue = register_info
                    base_info_list.append(base_info)
                return base_info_list
        return None


    def isDeviceServiceOk(self, c):
        status = v_device.ServiceStatus()
        #status.status = v_device.ServiceStatusType.vStatusOK
        status.status = v_device.ServiceStatusType.vStatusError
        if status.status != v_device.ServiceStatusType.vStatusOK:
            status.error_msg = "no device service running!!"
        else:
            status.error_msg = ""
        return status

    def GetServiceRunningInfo(self, c):
        return ""


class DeviceWatchServiceI(v_device.DeviceWatchService):
    def __init__(self, host, user, pwd, db):
        self._my_sql_helper = MySqlDbHelper(host, user, pwd, db)
        self._base_physic_info_cmd = "select deviceregisterinfo.serviceID\
, deviceserverinfo.cpuCount, deviceserverinfo.physicalCpuCount, serviceloadinginfo.cpuUseRate\
, deviceserverinfo.memSize, serviceloadinginfo.useMemory, serviceloadinginfo.availableMemory\
, serviceloadinginfo.memUseRate, deviceregisterinfo.registerSuccessCount\
, deviceregisterinfo.registerFailCount, deviceregisterinfo.registerSuccessDeviceList\
, deviceregisterinfo.registerFailDeviceList, serviceloadinginfo.create_time\
 from deviceregisterinfo, deviceserverinfo, serviceloadinginfo \
where serviceloadinginfo.create_time between now()-interval 60 second and now()\
 and unix_timestamp(serviceloadinginfo.create_time) = unix_timestamp(deviceregisterinfo.create_time)\
 and deviceregisterinfo.create_time between now()-interval 60 second and now();"
 # where unix_timestamp(serviceloadinginfo.create_time) > unix_timestamp(now()-130) and unix_timestamp(serviceloadinginfo.create_time) <= unix_timestamp(now())and unix_timestamp(deviceregisterinfo.create_time) > unix_timestamp(now()-130) and unix_timestamp(deviceregisterinfo.create_time) <= unix_timestamp(now());"

    def GetPhysicInfo(self, c):
        # func = getattr(self._my_sql_helper, "exe_cmd")
        # select_physic_cmd = ""
        # #eventlet.with_timeout()
        # if func is not None:
        #     waiter = eventlet.spawn(func, select_physic_cmd)
        #     waiter.link(GetPhysicInfoCallback)
        results = self._my_sql_helper.exe_cmd(self._base_physic_info_cmd)
        print("results:", results)
        if isinstance(results, tuple) and 0 < results[0]:
            base_info_list = []
            base_info = v_device.BasePhyServiceInfo()
            for item in results[1]:
                base_info.serviceID = item.get("serviceID")
                cpu_info = v_device.CpuInfo()
                cpu_info.cpuUseRate = float(item.get("cpuUseRate"))
                cpu_info.cpuCount = int(item.get("cpuCount"))
                cpu_info.physicCpuCount = int(item.get("physicalCpuCount"))
                if base_info.cpuinfovalue is None:
                    base_info.cpuinfovalue = cpu_info
                mem_info = v_device.MemInfo()
                mem_info.memSize = float(item.get("memSize"))
                mem_info.useMem = float(item.get("useMemory"))
                mem_info.memUseRate = float(item.get("memUseRate"))
                mem_info.aviableMemSize = float(item.get("availableMemory"))
                if base_info.meminfovalue == None:
                    base_info.meminfovalue = mem_info
                register_info = v_device.RegisterInfo()
                register_info.registerSuccessCount = int(item.get("registerSuccessCount"))
                register_info.registerFailCount = int(item.get("registerFailCount"))
                register_info.registerSuccessDeviceList = str(item.get("registerSuccessDeviceList "))
                register_info.registerFailDeviceList = str(item.get("registerFailDeviceList"))
                if base_info.registerinfovalue is None:
                    base_info.registerinfovalue = register_info
                base_info_list.append(base_info)
            return base_info_list
        return None


    def isDeviceServiceOk(self, c):
        status = v_device.ServiceStatus()
        #status.status = v_device.ServiceStatusType.vStatusOK
        status.status = v_device.ServiceStatusType.vStatusError
        if status.status != v_device.ServiceStatusType.vStatusOK:
            status.error_msg = "no device service running!!"
        else:
            status.error_msg = ""
        return status

    def GetServiceRunningInfo(self, c):
        return ""
