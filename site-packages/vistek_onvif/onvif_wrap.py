#!/usr/bin/env python
# -*- coding:utf-8 -*-
import onvif, os, sys, collections, threading, time, logging, traceback,logging.handlers
from onvif import ONVIFCamera
import Vistek.Data as v_data
import eventlet
import onvif_global_value

try:
    import Queue
except:
    import queue as Queue
if not os.path.exists("log"):
    os.mkdir("log")

file_name = "{0}-{1}.log".format(__name__, os.getpid())
file_path = os.path.join("log", str(os.getpid()))
try:
    if not os.path.exists(file_path):
        os.makedirs(file_path)
except:
    traceback.print_exc()
log_file = os.path.join(file_path, file_name)
log_level = logging.DEBUG

logger = logging.getLogger(file_name)
handler = logging.handlers.TimedRotatingFileHandler(log_file, when="D", interval=1)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(funcName)s:%(lineno)s]  [%(message)s]")
logger.disabled = False
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(log_level)
import vistek_util.workTemplate as work_template
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET

Session = collections.namedtuple('Session','client ip port user pwd')
RemoteSession = collections.namedtuple('RemoteSession', 'device_id ip port user pwd wsdl_path')

is_start = False

def register_device(device_id, ip, port, user_name, user_pwd):
    global is_start
    register_success_dev_list = onvif_global_value.get_register_success_device_list()
    register_faile_dev_list = onvif_global_value.get_register_fail_device_list()
    status_queue = onvif_global_value.get_device_status_queue()
    register_xml_node = onvif_global_value.get_register_xml_node()
    dev_status_list = onvif_global_value.get_device_status_list()

    device_node = ET.SubElement(register_xml_node, "device")
    device_node.set("device_id", device_id)
    device_node.set("ip", ip)
    device_node.set("port", str(port))
    device_node.set("user", user_name)
    device_node.set("pwd", user_pwd)
    device_list = onvif_global_value.get_device_list()
    register_node = ET.Element('register')
    ip_node = ET.SubElement(register_node, 'ip')
    ip_node.text = ip
    session_node = ET.SubElement(register_node, 'session')
    if not device_list.has_key(device_id):
        if sys.platform == 'win32':
            wsdl_path = os.path.join(os.path.dirname(onvif.__file__), os.path.pardir, "wsdl")
            try:
                cache_location= os.path.dirname(onvif.__file__)
                client = ONVIFCamera(ip, port, user_name, user_pwd, wsdl_path\
                                     , cache_location=cache_location, cache_duration="d"\
                                     , no_cache=False)
                # client = ONVIFCamera(ip, port, user_name, user_pwd, wsdl_path)
                session = Session(client=client, ip=ip, port=port, user=user_name, pwd=user_pwd)
                device_list[device_id] = session
                if client is not None:
                    logger.info("register success id:{0} ip:{1}.".format(device_id, ip))
                    status_xml = get_device_status(device_id)
                    if status_xml is not None and isinstance(status_xml, tuple) and 0 < len(status_xml[0]):
                        status_queue.put(status_xml[0])
                    if device_id not in register_success_dev_list:
                        register_success_dev_list[device_id] = session
                    if device_id not in dev_status_list:
                        dev_status_list[device_id] = True
            except:
                logger.warn("register fail id:{0} ip:{1}".format(device_id, ip))
                # if device_id not in register_faile_dev_list:
                #     register_faile_dev_list[device_id] = session
                # if device_id not in dev_status_list:
                #     dev_status_list[device_id] = True
                traceback.print_exc()

        else:
            client = ONVIFCamera(ip, port, user_name, user_pwd)
        if not is_start:
            t = StartServerThread()
            t.start()
            push_thread = CheckStatusChangeThread()
            push_thread.start()
            is_start = True
        session_node.text = ip
    else:
        session_node.text = str(device_list.get(device_id).ip)
    ET.ElementTree(register_xml_node).write("onvif_device_lists.xml", encoding="UTF-8", method="xml")
    session_xml = ET.tostring(register_node, encoding='UTF-8', method='xml')
    return (session_xml, len(session_xml))

def un_register_device(device_id):
    device_list = onvif_global_value.get_device_list()
    device_status_list = onvif_global_value.get_device_status_list()
    if device_id in device_list:
        device_list.pop(device_id)
    if device_id in device_status_list:
        device_status_list.pop(device_id)

def get_stream_url(device_id, channel=None):
    device_list = onvif_global_value.get_device_list()
    urls = ET.Element('stream_url_lists')
    urls_xml = ""
    if not device_list.has_key(device_id ):
        urls_xml = ET.tostring(urls, encoding='UTF-8', method='xml')
        logger.warning("device_id:{0} get_stream_url failed, dev_id not exists.".format(str(device_id)))
        return (urls_xml, len(urls_xml))
    else:
        session = device_list.get(device_id)
        media_capability_name ='Media'
        request = session.client.devicemgmt.create_type("GetCapabilities")
        request.Category=media_capability_name
        media_info = session.client.devicemgmt.GetCapabilities(request)
        #media_info = session.client.devicemgmt.GetCapabilities({'Categroy':media_capability_name})
        if media_info.Media.StreamingCapabilities.RTP_RTSP_TCP or media_info.Media.StreamingCapabilities.RTP_TCP:
            #media_service = session.client.create_media_service()
            media_service = session.client.get_service(media_capability_name)
            profiles = media_service.GetProfiles()
            #video_sources = media_service.GetVideoSources()
            for profile in profiles:
                media_params = media_service.create_type("GetStreamUri")
                media_params.ProfileToken = profile._token
                media_params.StreamSetup.Stream.value = "RTP-Unicast"
                media_params.StreamSetup.Transport.Protocol.value = "RTSP"
                stream_url = media_service.GetStreamUri(media_params)
                url_node  = ET.SubElement(urls,'stream_url')
                url_node.text = stream_url.Uri
        urls_xml = ET.tostring(urls, encoding='UTF-8', method='xml')
        logger.info("device_id:{0} get_stream_url success, value:{1}.".format(str(device_id), str(urls_xml)))
    return (urls_xml, len(urls_xml))

def get_device_status(device_id, channel=None):
    device_list = onvif_global_value.get_device_list()
    device_status = ET.Element('device_status')
    if not device_list.has_key(device_id) :
        logger.error("device:{0} not register.".format(device_id))
        return ("", 0)
    else:
        remote_session = device_list.get(device_id)
        client = None
        client = remote_session.client
        time = client.devicemgmt.GetSystemDateAndTime()
        if time is not None:
            device_status.text = str(True)
        else:
            device_status.text = str(False)
        device_status.set('ip', remote_session.ip)
        device_status.set('port', str(remote_session.port))
        device_status.set('device_id', str(device_id))
        logger.info("dev_id:{0} ip:{1} get status success".format(device_id, str(remote_session.ip)))
    status_xml = ET.tostring(device_status, encoding='UTF-8', method='xml')
    return (status_xml, len(status_xml))

def get_event_service(device_id):
    global device_list
    device_status = ET.Element('device_status')
    if device_id in device_list:
        event_service = device_list[device_id].client.create_events_service()
        #properties = event_service.GetEventProperties()
        params = {'InitialTerminationTime':'PT20s'}
        wrap = event_service.CreatePullPointSubscription(params)
        #print('event service:', event_service,'func:',dir(event_service), 'wrap:', wrap, 'type:', type(wrap))
        #print('is instance', isinstance(wrap,PullPointSubscription))
        pull_params = {'Timeout':'PT30s', 'MessageLimit':2}
        msg = wrap.SubscriptionReference.PullMessages(pull_params)
        #print('msg:', msg)

def ptz(device_id, cmd, *args, **kwargs):
    dev_lists = onvif_global_value.get_device_list()
    if device_id in dev_lists:
        session_info = dev_lists.get(device_id)
        ptz_name = "PTZ"
        request = session_info.client.devicemgmt.create_type("GetCapabilities")
        request.Category = ptz_name
        try:
            ret = session_info.client.devicemgmt.GetCapabilities(request)
        except:
            traceback.print_exc()

def start_check_all_staus():
    global device_lists
    global device_status_lists
    logger.info("onvif start check all device status")
    device_status_manager = work_template.WorkerManager(10, 5)
    while True:
        for device_id, login_info in device_list.items():
            device_status_manager.add_job(get_device_status, device_id)
        device_status_manager.wait_for_complete()
        out_queue = onvif_global_value.get_device_status_queue()
        while not device_status_manager.result_queue_empty():
            out_str = device_status_manager.get_result()
            if 1 > len(out_str[0]):
                continue
            device_status_node = ET.fromstring(out_str[0])
            dev_node_id = device_status_node.get('device_id')
            logger.info("onvif status change queue size:{0}".format(out_queue.qsize()))
            if device_status_list.has_key(dev_node_id ) and device_status_node.text != str(device_status_list.get(dev_node_id)):
                out_queue.put(out_str)
        time.sleep(5)

def start_get_all_status_by_eventlet():
    task_pool = eventlet.GreenPool()
    device_list = onvif_global_value.get_device_list()
    cur_status_queue = onvif_global_value.get_cur_status_queue()
    while True:
        begin_time = time.time()
        results = task_pool.imap(get_device_status, device_list.keys())
        task_pool.waitall()
        end_time = time.time()
        print("total get all status time:{0}".format(end_time - begin_time))
        insert_list = []
        for result in results:
            insert_list.append(result)
        cur_status_queue.put(insert_list)
        time.sleep(5)

class StartServerThread(threading.Thread):
    def run(self):
        #start_check_all_staus()
        start_get_all_status_by_eventlet()

def check_status_change_one(status_xml):
    status_queue = onvif_global_value.get_device_status_queue()
    device_status_lists = onvif_global_value.get_device_status_list()
    if isinstance(status_xml, tuple) and 0 < len(status_xml[0]):
        device_status_list_node = ET.fromstring(status_xml[0])
        if device_status_list_node is not None:
            for device_status_node in device_status_list_node.iterfind("device_status"):
                dev_status_id = device_status_node.get('status_id')
                cur_status = str(device_status_node.text)
                if dev_status_id in device_status_lists and str(device_status_node.text) != str(device_status_lists.get(dev_status_id)):
                    node_str = ET.tostring(device_status_node, encoding="UTF-8", method="xml")
                    status_queue.put(node_str)
                    logger.info("status change:{0}".format(node_str))
                    device_status_lists[dev_status_id] = cur_status

def check_status_change():
    cur_status_queue = onvif_global_value.get_cur_status_queue()
    task_pool = eventlet.GreenPool()
    while True:
        if not cur_status_queue.empty():
            begin_time = time.time()
            all_cur_status = cur_status_queue.get()
            for item in all_cur_status:
                task_pool.spawn(check_status_change_one, item)
            task_pool.waitall()
            end_time = time.time()
            print("total check change time:{0}".format(end_time - begin_time))
        time.sleep(0.01)

class CheckStatusChangeThread(threading.Thread):
    def run(self):
        check_status_change()

def try_get_device_info(device):
    try:
        client = None
        if sys.platform == 'win32':
            wsdl_path = os.path.join(os.path.dirname(onvif.__file__), os.path.pardir, "wsdl")
            client = ONVIFCamera(device.IP, device.Port, device.Username, device.Password, wsdl_path)
        #out_data = client.devicemgmt.GetDeviceInformation()
        media_svc = client.get_service("Media")
        channel_list = []
        if media_svc is not None:
            # video_sources = media_svc.GetVideoSources()
            profiles = media_svc.GetProfiles()
            channel_list = []
            source_token = []
            for profile in profiles:
                source_token.append(profile.VideoSourceConfiguration._token)
            unique_source_token = set(source_token)
            for index, token in enumerate(unique_source_token):
                channel = v_data.DmDeviceVideoChannel()
                if device.DeviceID is not None:
                    channel.DeviceID = device.DeviceID
                channel.Name = "{0}-{1}".format(device.IP, index)
                channel.ChannelIndex = index
                channel_list.append(channel)
            if not device.ChannelList:
                device.ChannelList = channel_list
            if profiles is not None:
                return (device.DeviceID, True, 2, "onvif")
                logger.info("try device success id:{0} ip:{1} pid:{2} threadid:{3}.".format(device.DeviceID\
                                                                                            , device.IP\
                                                                                            , os.getpid()\
                                                                                            , threading.currentThread().ident))
        logger.error("try device id:{0} ip:{1} pid:{2} threadid:{3} fail!!!".format(device.DeviceID\
                                                                                    , device.IP\
                                                                                    , os.getpid()\
                                                                                    , threading.currentThread().ident))
        return (device.DeviceID, False, 0, None)
    except:
        logger.error("try device id:{0} ip:{1} pid:{2} threadid:{3} exception fail!!!".format(device.DeviceID \
                                                                                    , device.IP \
                                                                                    , os.getpid() \
                                                                                    , threading.currentThread().ident))
        return (device.DeviceID, False, 0, None)
    finally:
        del client

# def try_get_device_info(device_id, ip, port, user, pwd):
#         try:
#             client = None
#             if sys.platform == 'win32':
#                 wsdl_path = os.path.join(os.path.dirname(onvif.__file__), os.path.pardir, "wsdl")
#                 client = ONVIFCamera(ip, port, user, pwd, wsdl_path)
#             out_data = client.devicemgmt.GetDeviceInformation()
#             if out_data:
#                 return (device_id, True, 2, str(out_data.Manufacturer).lower())
#             else:
#                 return (device_id, False, 0, None)
#         except:
#             traceback.print_exc()
#             return (device_id, False, 0, None)


def test_nvr():
    # camera_ip = "221.2.91.54"
    # out = register_device(camera_ip, camera_ip, 80, 'admin', 'admin12345')
    # print('out:', out, 'type:', type(out))
    # out = get_stream_url(camera_ip)
    camera_ip = "140.246.230.64"
    out = register_device(camera_ip, camera_ip, 80, 'admin', '12345')
    print('out:', out, 'type:', type(out))
    out = get_stream_url(camera_ip)

def test_ipc():
    begin_time = time.time()
    camera_ip = "172.16.1.191"
    out = register_device(camera_ip, camera_ip, 80, 'admin', '12345')
    print('out:', out, 'type:', type(out))
    out = get_stream_url(camera_ip)
    end_time = time.time()
    print("total time:{0}".format((end_time-begin_time)))
if __name__ == '__main__':
    # try_get_device_info("172.16.2.190", "172.16.2.190", 85, "888888", "888888")
    # test_nvr()
    logging.getLogger("suds.client").setLevel(level=logging.DEBUG)
    test_ipc()
    while 1:
        time.sleep(1)


