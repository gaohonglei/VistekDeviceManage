# -*- coding=UTF-8 -*-

import os, sys, uuid, traceback, logging, threading, threadpool,time,logging.handlers
import socket,random,collections
# import Enum
try:
    import queue as Queue
except:
    import Queue
from ctypes import *
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET
import Vistek.Data as v_data
import Vistek.Device as v_device

##-----------------------------------------------begin 构造logger--------------------------
file_name = "{0}-{1}.log".format(__name__, os.getpid())
file_path = os.path.join("log", str(os.getpid()))
try:
    if not os.path.exists(file_path):
        os.makedirs(file_path)
except:
    traceback.print_exc()
log_file = os.path.join(file_path, file_name)
#log_level = logging.DEBUG
log_level = logging.INFO
logger = logging.getLogger(file_name)
handler = logging.handlers.TimedRotatingFileHandler(log_file, when="H", interval=5,backupCount=1)
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(funcName)s:%(lineno)s] [%(message)s]")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(log_level)
def enum(**enums):
    return type('Enum', (), enums)
ret_status = enum(	ret_GB28181_ERR = -1000,
	ret_ERR_INPUT_PARA = -999,
	ret_ERR_MALLOC = -998,
	ret_ERR_SIP = -997,
	ret_ERR_MSG_CREATE = -996 ,
	ret_ERR_MSG_GET_TIMEOUT = -995,
	ret_ERR_PARSE_XML_PARA = -994,
	ret_ERR_NOT_FIND_UAS = -993,
	ret_ERR_UAC_OFFLINE = -992,
	ret_ERR_BUF_TOO_SMALL = -991,
	ret_ERR_DEV_TOO_MUCH = -990,
	ret_OK = 0)
##-----------------------------------------------end 构造logger-----------------------
def  load_dll(dll_name = "vistek_sip_device"):
    if sys.platform == "win32":
        handle = WinDLL(dll_name)
    else:
        handle = CDLL(dll_name)
    return handle

class v_gb28181:
    def __init__(self, device, device_status_queue = None, device_queue = None,device_url_queue = None):
        global g_DllHandle
        self.handle = g_DllHandle
        self.ConnID = None
        self._device = device
        # self._device_status_queue = Queue.Queue()
        # self._device_queue = Queue.Queue()
        # self._device_url_queue = Queue.Queue()
        self._device_status_queue = device_status_queue
        self._device_queue = device_queue
        self._device_url_queue = device_url_queue
        self._chl_list = dict()
        self._init_channel_list()
        self.defaultPara ={'RegValidity':"3600",'HeartBeatInter':"60",'HeartBeatCount':"3"}
        #self.gb_uac_login_server()
    def _init_channel_list(self):
        if self._device.ChannelList is None:
            return
        for Channel in self._device.ChannelList:
            logger.info("channel info :{0}".format(Channel))
            self._chl_list[Channel.ExtensionID] = Channel.ChannelIndex
            logger.info("_channel_list :{0}".format(self._chl_list))
    def gb_uac_login_server(self):
        if self.handle is None:
            logger.warning("vistek_sip_device handle is null")
            return False
        loginXml= self.createLoginXML()
        xml = create_string_buffer(1024)
        length =len(loginXml)
        xml.value = loginXml
        try:
            ret = self.handle.gb_uac_login_server(xml,5)
            if int(ret) < 0:
                logger.error("gb_uac_login_server failed. error_code:{0},IP:{1}, DeviceID:{2},connID:{3}".format(ret,self._device.IP, self._device.DeviceID,self.ConnID))
                return False
            else:
                self.ConnID=ret
                logger.info("gb_uac_login_server success. code:{0},IP:{1}, DeviceID:{2},connID:{3}".format(ret,self._device.IP, self._device.DeviceID,self.ConnID))
            return True
        except Exception,ex:
            return False
    @property
    def IP(self):
        return self._device.IP

    def createLoginXML(self):
        try:
            UsaPara = ET.Element("UasPara")
            ServerID = ET.SubElement(UsaPara,"ServerId")
            ServerID.text = self._device.Code
            ServerDomain = ET.SubElement(UsaPara, "ServerDomain")
            ServerDomain.text = "3401000000"
            ServerIp= ET.SubElement(UsaPara, "ServerIp")
            ServerIp.text = self._device.IP
            ServerPort = ET.SubElement(UsaPara, "ServerPort")
            ServerPort.text = str(self._device.Port)
            UserName = ET.SubElement(UsaPara, "UserName")
            UserName.text = self._device.Username
            PassWord = ET.SubElement(UsaPara, "PassWord")
            PassWord.text = self._device.Password
            LocalId = ET.SubElement(UsaPara, "LocalId")
            # LocalId.text = self._device.ExtensionID
            LocalId.text = self._device.Username
            RegValidity = ET.SubElement(UsaPara, "RegValidity")
            RegValidity.text = self.defaultPara["RegValidity"]
            HeartBeatInter = ET.SubElement(UsaPara, "HeartBeatInter")
            HeartBeatInter.text = self.defaultPara["HeartBeatInter"]
            HeartBeatCount = ET.SubElement(UsaPara, "HeartBeatCount")
            HeartBeatCount.text = self.defaultPara["HeartBeatCount"]
            xml = ET.tostring(UsaPara, encoding="UTF-8", method="xml")
            logger.info("createXML-XML:{0}".format(xml))
            return xml
        except:
            traceback.print_exc()
            return None
    def paraDeviceListXML(self,xml):
        try:
            deviceList = dict()
            logger.info("paraDeviceListXML:{0}".format(xml))
            # uxml = xml.decode("gb2312").encode("utf-8")
            # uxml.replace("GB2312","UTF-8")
            DeviceList = ET.fromstring(xml)
            for item in DeviceList.iter("Item"):
                device = dict()
                device["DeviceID"] = item.find("DeviceID").text
                Name = item.find("Name")
                if Name is None:
                    device["Name"] = item.find("DeviceID").text
                else:
                    device["Name"] = Name.text

                Manufacturer = item.find("Manufacturer")
                if Manufacturer is None:
                    device["Manufacturer"] = ""
                else:
                    device["Manufacturer"] = Manufacturer.text

                IPAddress = item.find("IPAddress")
                if IPAddress is None:
                    device["IPAddress"] = ""
                else:
                    device["IPAddress"] = IPAddress.text

                device["Status"] = item.find("Status").text
                DeviceId = item.find("DeviceID").text
                deviceList[DeviceId] = device
            logger.info("paraDeviceListXML-device:{0}".format(deviceList))
            return deviceList
        except:
            traceback.print_exc()
            return None
    def pushDeviceStatusToQueue(self,device_list):
        if device_list is not None:
            status_list = ET.Element("device_status_list")
            for deviceID,device in device_list.items():
                device_status_node = ET.SubElement(status_list,"device_status")
                device_status_node.set('ip', self._device.IP)
                device_status_node.set('port', str(self._device.Port))
                device_status_node.set('device_id', self._device.DeviceID)
                device_status_node.set('status_id', "{0}:{1}".format(self._device.DeviceID, str(self._chl_list[deviceID])))
                device_status_node.set('channelID', deviceID)
                device_status_node.set("channel",str(self._chl_list[deviceID]))
                device_status_node.set('error_node', str(0))
                if device["Status"] == "ON":
                    device_status_node.text = "true"
                else:
                    device_status_node.text = "false"
            xml = ET.tostring(status_list,encoding="UTF-8",method="xml")
            self._device_status_queue.put(xml)

    def pushChangedChannelToQueue(self,channel_list):
        ChannelList = list()
        for channelID,channel in channel_list.items():
            DeviceVideoChannel = v_data.DmDeviceVideoChannel()
            DeviceVideoChannel.DeviceID = self._device.DeviceID
            DeviceVideoChannel.ChannelIndex = self._chl_list[channelID]
            DeviceVideoChannel.ExtensionID = channelID
            DeviceVideoChannel.SystemID = self._device.SystemID #此处和权限有关，以后可能会修改
            DeviceVideoChannel.Name = channel["Name"].encode("utf-8")
            ChannelList.append(DeviceVideoChannel)
        if self._device.ChannelList:
            self._device.ChannelList.extend(ChannelList)
        else:
            self._device.ChannelList = ChannelList
        self._device.Status = 0
        self._device_queue.put(self._device)
        logger.info("push device to UpdateDeviceList:{0}".format(self._device))
    def pushStreamUrlToQueue(self,channel_list):
        DeviceChannelInfoList = list()
        try:
            for channelID,channel in channel_list.items():
                ChannelInfo = v_device.DeviceChannelInfo()
                ChannelInfo.deviceID = self._device.DeviceID
                ChannelInfo.username = self._device.Username
                ChannelInfo.password = self._device.Password
                ChannelInfo.channel = self._chl_list[channelID]
                ChannelInfo.thirdparty = False
                streamInfo = v_device.DeviceStreamInfo()
                streamInfo.deviceID = self._device.DeviceID
                streamInfo.channel = self._chl_list[channelID]
                streamInfo.stream = 0
                ChannelInfo.streamList = [streamInfo]
                url = "sip://{0}:{1}@{2}:{3}/serverID={4}&deviceID={5}&localID={6}&regValidity={7}HeartBeateInter={8}&HeartBeatCount={9}".format(
                                                                                                        self._device.Username\
                                                                                                        ,self._device.Password\
                                                                                                        ,self._device.IP\
                                                                                                        ,str(self._device.Port)\
                                                                                                        ,self._device.Code\
                                                                                                        ,channelID\
                                                                                                        ,self._device.Username\
                                                                                                        ,self.defaultPara["RegValidity"]\
                                                                                                        ,self.defaultPara["HeartBeatInter"]\
                                                                                                        ,self.defaultPara["HeartBeatCount"])
                streamInfo.uri = url
                DeviceChannelInfoList.append(ChannelInfo)
        #    print(DeviceChannelInfoList)
            self._device_url_queue.put(DeviceChannelInfoList)
            logger.info("push device stream url :{0}".format(DeviceChannelInfoList))
        except Exception,ex:
            traceback.print_exc()
    def checkChannelChanged(self,device_list):
        if device_list is not None:
            addChannel = list(set(device_list.keys()) - set(self._chl_list.keys()))
            delChannel = list(set(self._chl_list.keys()) - set(device_list.keys()))
            MaxIndex = len(self._chl_list)
            ChangedDeviceChannel = {}
            for Channel in addChannel:
                self._chl_list[Channel] = MaxIndex
                MaxIndex = MaxIndex + 1
                ChangedDeviceChannel[Channel] = device_list[Channel]
            if len(ChangedDeviceChannel) > 0:
                self.pushChangedChannelToQueue(ChangedDeviceChannel)
                self.pushStreamUrlToQueue(ChangedDeviceChannel)

    def get_device_list(self):
        if self.ConnID >= 0:
            device_status = dict()
            #从gb28181 平台获取设备列表
            countExtend = 1
            while True:
                capacity = 1024 * 1024 * 4 * countExtend
                xml_str = create_string_buffer(capacity)
                ret = self.handle.gb_uac_get_device_list(self.ConnID,xml_str,capacity,20)
                if ret == ret_status.ret_OK:
                    device_list = self.paraDeviceListXML(str(xml_str.value))
                    self.checkChannelChanged(device_list)
                    self.pushDeviceStatusToQueue(device_list)
                    return (ret_status.ret_OK,self._device.DeviceID)
                elif ret == ret_status.ret_ERR_BUF_TOO_SMALL:
                    countExtend += 1
                    continue
                else:
                    logger.error("gb_uac_get_device_list return code:{0},IP:{1}, DeviceID:{2},connID:{3}".format(ret,self._device.IP, self._device.DeviceID,self.ConnID))
                    return (ret,self._device.DeviceID)


class v_gb28181_manager:
    def __init__(self, tp_thd_count = 6):
        #print("_________init__________manager")
        self._objects = dict()#key: deviceID value: gb28181_instance
        self._faild_objects = dict() #登录失败 instance
        self.check_status_change_thd = threading.Thread(target=v_gb28181_manager._do_check_status_change, name="check_status_change_thd",args=(self,))
        self.device_main_thd = threading.Thread(target= v_gb28181_manager._do_loop_main,name = "do_loop_main",args=(self,))
        self.relogin_device_thd = threading.Thread(target=v_gb28181_manager.relogin_device,name="relogin_device",args=(self,))
        self._device_status_queue = Queue.Queue()
        self._need_push_device_status_queue = need_push_device_status_queue
        self._device_url_queue = device_url_queue
        self._device_queue = device_queue
        #self._change_device_status_queue = Queue.Queue()
        self.channel_status = dict()
        self.normal = True
        #self.gb_uac_init()
        self.start()

    def start(self):
        self.gb_uac_init()
        if self.device_main_thd:
            self.device_main_thd.start()
        if self.check_status_change_thd:
            self.check_status_change_thd.start()
        if self.relogin_device_thd:
            self.relogin_device_thd.start()
    def gb_uac_init(self):
        ip = socket.gethostbyname(socket.gethostname())
        #port = random.randint(20000,50000)
        port = 22226
        #拼凑user_agent xml
        user_agent=""
        ret = g_DllHandle.gb_uac_init("",ip,port)
        if ret == 0:
            self.gb28181_inited = True
        else:
            logger.error("gb_uac_init return code:{0}".format(ret))
            self.gb28181_inited = False
    def try_process_device(self,device):
        ip = device.IP
        port = device.Port
        username = device.Username
        password = device.Password
        device_id = device.DeviceID
        gb28181 = v_gb28181(device)
        try:
            if gb28181.gb_uac_login_server():
                result = gb28181.handle.gb_uac_get_status(gb28181.ConnID)
                device_list = gb28181.get_device_list()
                if result == 1:
                    logger.info(
                        "try_process_device success. deviceID:{0} IP:{1} Port: {2} username: {3} password: {4}".format(
                            device_id, ip, \
                            port, username, \
                            password))
                    return (device_id, True, 8, "gb28181")
                else:
                    logger.error(
                        "try_process_device-gb_uac_get_status failed, ec: {0}. deviceID:{1} IP:{2} Port: {3} " \
                        "username: {4} password: {5}".format(result, device_id, ip, port, username, password))
                    return (device_id, False, 0, "")
            else:
                return (device_id, False, 0, "")
        except Exception, ex:
            logger.error(
                "try_process_device exception. deviceID:{0} IP:{1} Port: {2} username: {3} password: {4}.   desc: {5}".format(
                    device_id, ip, port,
                    username, password, ex))
            return (device_id, False, 0, "")
    def loop_main_callback(self,request,result):
        logger.info("loop main callback :deviceid:{0},red:{1}".format(result[1],result[0]))
        if result[0] < 0:
            deviceID=result[1]
            device = self._objects[deviceID]
            self._objects.pop(deviceID)
            self._faild_objects[deviceID]= device
    def _do_loop_main(self):
        pool_size = 8
        pool = threadpool.ThreadPool(pool_size)
        while self.normal:
            task_list = list()
            for k, ins in self._objects.items():
                task_list.extend(threadpool.makeRequests(v_gb28181.get_device_list,[((ins,),{})],self.loop_main_callback))
            map(pool.putRequest,task_list)
            pool.wait()
            time.sleep(30)
    def relogin_device(self):
        while self.normal:
            for deviceID,object in self._faild_objects.items():
                result = object.gb_uac_login_server()
                #print(result)
                if result:
                    if not self._objects.has_key(deviceID):
                        self._objects[deviceID] = object
                        self._faild_objects.pop(deviceID)
                        logger.info("relogin deviceID:{0} IP:{1} success!!".format(deviceID,object.IP))
            time.sleep(2)

    def _do_check_status_change(self):
        while self.normal:
            try:
                device_status = self._device_status_queue.get(timeout= 5)
                device_status_nodes = ET.fromstring(device_status)
                logger.info(device_status)
                for status_node in device_status_nodes.iterfind("device_status"):
                    channelID = status_node.get("channelID")
                    status = status_node.text
                    if not self.channel_status.has_key(channelID):
                        #第一次，统一推一次
                        self.channel_status[channelID] = status
                        node = ET.tostring(status_node,encoding="UTF-8", method="xml")
                        self._need_push_device_status_queue.put(node)
                        logger.info("push device status :{0}".format(node))
                    else:
                        #检测和上一次得状态是否改变，改变则推状态，否则不推
                        if status != self.channel_status[channelID]:
                            self.channel_status[channelID] = status
                            node = ET.tostring(status_node, encoding="UTF-8", method="xml")
                            self._need_push_device_status_queue.put(node)
                            logger.info("push device status :{0}".format(node))
                time.sleep(5)
            except Exception,ex:
                time.sleep(5)



    def get_change_device_status_queue(self):
        return self._change_device_status_queue

    def get_device_queue(self):
        return self._device_list

    def new_28181instance(self, device):
        if not self._objects.has_key(device.DeviceID):
            gb = v_gb28181(device, self._device_status_queue, self._device_queue,self._device_url_queue)

            flag = gb.gb_uac_login_server()
            if flag:
                self._objects[device.DeviceID] = gb
                #print(1)
                logger.info("register deviceID:{0} IP:{1} success instance count:{2}".format(device.DeviceID, device.IP,
                                                                                             len(self._objects)))
            else:
                #print(2)
                if not self._faild_objects.has_key(device.DeviceID):
                    self._faild_objects[device.DeviceID] = gb
                logger.info("register deviceID:{0} IP:{1} faild instance count:{2}".format(device.DeviceID, device.IP,
                                                                                             len(self._faild_objects)))


    def del_28181instance(self, device_id):
        logger.info("del_28181instance".format(device_id))
        if self._objects.has_key(device_id):
            self._objects.pop(device_id)
            logger.info("unregister from object..deviceID:{0}success".format(device_id))
        if self._faild_objects.has_key(device_id):
            self._faild_objects.pop(device_id)
            logger.info("unregister from faild device list..deviceID:{0} success".format(device_id, device.IP))

gb28181_manager_instance = None
g_DllHandle = None
lock = threading.Lock()
is_start = False
#获取状态
need_push_device_status_queue=Queue.Queue()
def getStatusQueue():
    global need_push_device_status_queue
    return need_push_device_status_queue
#获取设备通道改变
def try_process_device(device,timeout = 5):
    global gb28181_manager_instance
    gb28181_manager_instance.normal = False
    return gb28181_manager_instance.try_process_device(device)
device_queue = Queue.Queue()
def getChannelChangeQueue():
    global device_queue
    return device_queue
device_url_queue = Queue.Queue()
def getStreamUrlQueue():
    global device_url_queue
    return device_url_queue
def register_device(device):
    global gb28181_manager_instance
    global g_DllHandle
    global is_start
    lock.acquire()
    if not is_start:
        g_DllHandle = load_dll(dll_name=os.path.abspath(os.path.join(os.path.dirname(__file__), 'gb28181sdk')))
        gb28181_manager_instance = v_gb28181_manager()
        is_start = True
    lock.release()
    gb28181_manager_instance.new_28181instance(device)
def unregister_device(device_id):
    logger.info("unregister_device:{0}".format(device_id))
    gb28181_manager_instance.del_28181instance(device_id)
def test_wrap():
    init_data = v_b2bua_init_data()
    init_data.serverID = "xxxxxxxxxxxxxxxxxxxxx"
    init_data.serverDomain = "ddddddddddddddddddddd"
    sw = v_sip_device_wrap(init_data)
    while True:
        device_list = sw.get_device_list()
        print("device_list size: {0}".format(len(device_list)))

if __name__ == '__main__':
#     if __debug__:
#         test_wrap()
    device = v_data.DmDevice()
    device.IP = "172.16.10.90"
    device.Port = 5060
    device.Code = "34010000002000000001"
    device.ExtensionID = "34010000002000000001"
    #device.DeviceId = "34010000002000000002"
    device.Username = "34013100002000000002"
    device.Password = "12345678"
    device.DeviceID = "c492a972-85ee-4730-bc7b-ce7929203a6a"
    #print(try_process_device(device))
    #manage = v_gb28181_manager()
    register_device(device)
    # raw_input()