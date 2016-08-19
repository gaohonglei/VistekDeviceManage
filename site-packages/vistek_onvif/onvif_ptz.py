#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
@version: 0.0.1
@author: lee
@license: Apache Licence
@contact: shida23577@hotmail.com
@software: PyCharm
@file: onvif_ptz.py
@time: 2016/4/18 9:56
"""

from vistek_util import PTZParser
import onvif_global_value
import requests
import logging, logging.handlers
import time
import os
import traceback

SpaceType = {"pantiltposition":"http://www.onvif.org/ver10/tptz/PanTiltSpaces/PositionGenericSpace"\
    , "pantilttranslation":"http://www.onvif.org/ver10/tptz/PanTiltSpaces/TranslationGenericSpace"\
    , "pantiltvelocity":"http://www.onvif.org/ver10/tptz/PanTiltSpaces/VelocityGenericSpace"\
    , "pantiltspeed":"http://www.onvif.org/ver10/tptz/PanTiltSpaces/GenericSpeedSpace"\
    , "zoomvelocity":"http://www.onvif.org/ver10/tptz/ZoomSpaces/VelocityGenericSpace"}

file_name = "{0}-{1}.log".format(__name__, os.getpid())
file_path = os.path.join("log", str(os.getpid()))
try:
    if not os.path.exists(file_path):
        os.makedirs(file_path)
except:
    traceback.print_exc()
dest_file_name = os.path.join(file_path, file_name)
log_file = dest_file_name
log_level = logging.DEBUG

logger = logging.getLogger(file_name)
handler = logging.handlers.TimedRotatingFileHandler(log_file, when="D", interval=1)
formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(funcName)s:%(lineno)s]  [%(message)s]")

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(log_level)

try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET
class ONVIF_XML_Parser():
    def __init__(self, xml):
        if xml is not None:
            self._xml = xml
            if isinstance(xml, unicode):
                self._root_node = ET.fromstring(self._xml.encode("utf-8"))
            else:
                self._root_node = ET.fromstring(self._xml)
    def ptz_cmd_value(self):
        if self._root_node is not None:
            dev_id = self._root_node.get("deviceid")
            channel = self._root_node.get("channelindex")
            stream_type = self._root_node.get("streamtype")
            move_node = self._root_node.find("move")
            if move_node is not None:
                x = move_node.get("p")
                y = move_node.get("t")
                z = move_node.get("z")
                return (dev_id, channel, stream_type, x, y, z)
            stop_node = self._root_node.find("stop")
            if stop_node is not None:
                return (dev_id, channel, stream_type, 0, 0, 0, True)

class VOnvifPTZ():
    def __init__(self, dev_id, camera):
        self._device_id = dev_id
        self._ip = camera.host
        self._port = int(camera.port)
        self._user = camera.user
        self._pwd = camera.passwd
        self._media_service = camera.get_service("MEDIA")
        self._ptz_service = camera.get_service("PTZ")
        self._ptz_config = []
        if self._media_service is not None:
            profiles = self._media_service.GetProfiles()
            if profiles is not None:
                self._profiles = profiles
            ptz_tokens = set([profile.PTZConfiguration._token for profile in profiles if hasattr(profile, "PTZConfiguration")])
            for ptz_token in ptz_tokens:
                params = self._ptz_service.create_type("GetConfigurationOptions")
                params.ConfigurationToken = ptz_token
                options_config = self._ptz_service.GetConfigurationOptions(params)
                self._ptz_config.append(options_config)

    def _get_profile_token(self, channel, stream_type):
        for profile in self._profiles:
            if int(stream_type) == 0 and profile.Name == "mainStream":
                return profile._token
            elif int(stream_type) == 1 and profile.Name == "subStream":
                return profile._token
            elif int(stream_type) == 2 and profile.Name == "thirdStream":
                return profile._token
            else:
                continue
        return None

    def _get_ptz_config(self, channel, stream_type):
        if 1 == len(self._ptz_config):
            return self._ptz_config[0]
        else:
            raise "Not Implement"


    def _exe_ptz_cmd(self, channel, stream_type, x, y, z, stop=None, timeout = None):
        if self._ptz_service is not None:
            params = self._ptz_service.create_type("ContinuousMove")
            profile_token = self._get_profile_token(channel, stream_type)
            ptz_config = self._get_ptz_config(channel, stream_type)
            if profile_token is None:
                return False
            if stop is not None and stop:
                stop_param = self._ptz_service.create_type("Stop")
                stop_param.ProfileToken = profile_token
                try:
                    result = self._ptz_service.Stop(stop_param)
                    return True
                except:
                    return False
            params.ProfileToken = profile_token
            pantilt_speed_range = [(item.XRange, item.YRange) for item in ptz_config.Spaces.ContinuousPanTiltVelocitySpace if item.URI == SpaceType.get("pantiltvelocity")][0]
            zoom_speed_range = [(item.XRange) for item in ptz_config.Spaces.ContinuousZoomVelocitySpace if item.URI == SpaceType.get("zoomvelocity")][0]
            x_size = pantilt_speed_range[0].Max - pantilt_speed_range[0].Min
            y_size = pantilt_speed_range[1].Max - pantilt_speed_range[1].Min
            z_size = zoom_speed_range.Max - zoom_speed_range.Min
            params.Velocity.PanTilt._x = pantilt_speed_range[0].Min + x_size*((float(x)+1.0)/2)
            params.Velocity.PanTilt._y = pantilt_speed_range[1].Min + y_size*((float(y)+1.0)/2)
            params.Velocity.PanTilt._space = SpaceType.get("pantiltvelocity")
            # if z != 0.0:
            params.Velocity.Zoom._x = zoom_speed_range.Min + z_size*((float(z)+1.0)/2)
            params.Velocity.Zoom._space = SpaceType.get("zoomvelocity")
            if timeout is not None:
                params.Timeout = timeout
            result = self._ptz_service.ContinuousMove(params)
            print("result", result)


    def exe_ptz_cmd(self):
        if self._cmd is not None and self._ptz_cmd_urls is not None:
            (method, url) = str(self._ptz_cmd_urls[self._cmd]).split()
            result = self._exe_ptz_cmd(method, url, self._user, self._pwd, timeout=1)
            if not result:
                logger.error("ptz cmd failed!!")
            else:
                logger.debug("ptz cmd success.")

if __name__ == "__main__":
    import onvif
    from onvif import ONVIFCamera
    ip = "172.16.1.198"
    port = 80
    user_name = "admin"
    user_pwd = "admin123"
    wsdl_path = os.path.join(os.path.dirname(onvif.__file__), os.path.pardir, "wsdl")
    client = ONVIFCamera(ip, port, user_name, user_pwd, wsdl_path)
    ptz_obj = VOnvifPTZ("172.16.1.198", client)
    stop_xml = "<?xml version=\'1.0\'?><ptz deviceid=\"{0}\" channelindex=\"1\" streamtype=\"1\" userid=\"xxx\" userlevel=\"2\"><stop></stop></ptz>".format(ip)
    move_left_xml = "<?xml version=\'1.0\'?><ptz deviceid=\"{0}\" channelindex=\"1\" streamtype=\"1\" userid=\"xxx\" userlevel=\"2\"><move p=\"-0.25\" t=\"0.0\" z=\"0.0\"></move></ptz>".format(ip)
    move_right_xml = "<?xml version=\'1.0\'?><ptz deviceid=\"{0}\" channelindex=\"1\" streamtype=\"1\" userid=\"xxx\" userlevel=\"2\"><move p=\"0.25\" t=\"0.0\" z=\"0.0\"></move></ptz>".format(ip)
    move_up_xml = "<?xml version=\'1.0\'?><ptz deviceid=\"{0}\" channelindex=\"1\" streamtype=\"1\" userid=\"xxx\" userlevel=\"2\"><move p=\"0.0\" t=\"0.25\" z=\"0.0\"></move></ptz>".format(ip)
    move_down_xml = "<?xml version=\'1.0\'?><ptz deviceid=\"{0}\" channelindex=\"1\" streamtype=\"1\" userid=\"xxx\" userlevel=\"2\"><move p=\"0.0\" t=\"-0.25\" z=\"0.0\"></move></ptz>".format(ip)
    move_left_up_xml = "<?xml version=\'1.0\'?><ptz deviceid=\"{0}\" channelindex=\"1\" streamtype=\"1\" userid=\"xxx\" userlevel=\"2\"><move p=\"-0.25\" t=\"0.25\" z=\"0.0\"></move></ptz>".format(ip)
    move_left_down_xml = "<?xml version=\'1.0\'?><ptz deviceid=\"{0}\" channelindex=\"1\" streamtype=\"1\" userid=\"xxx\" userlevel=\"2\"><move p=\"-0.25\" t=\"-0.25\" z=\"0.0\"></move></ptz>".format(ip)
    move_right_up_xml = "<?xml version=\'1.0\'?><ptz deviceid=\"{0}\" channelindex=\"1\" streamtype=\"1\" userid=\"xxx\" userlevel=\"2\"><move p=\"0.25\" t=\"0.25\" z=\"0.0\"></move></ptz>".format(ip)
    move_right_down_xml = "<?xml version=\'1.0\'?><ptz deviceid=\"{0}\" channelindex=\"1\" streamtype=\"1\" userid=\"xxx\" userlevel=\"2\"><move p=\"0.25\" t=\"-0.25\" z=\"0.0\"></move></ptz>".format(ip)
    while 1:
        # 左
        move_left = ONVIF_XML_Parser(move_left_xml)
        move_stop = ONVIF_XML_Parser(stop_xml)
        ptz_obj._exe_ptz_cmd(*move_left.ptz_cmd_value()[1:])
        time.sleep(5)
        ptz_obj._exe_ptz_cmd(*move_stop.ptz_cmd_value()[1:])
        time.sleep(5)

        #右
        move_right = ONVIF_XML_Parser(move_right_xml)
        ptz_obj._exe_ptz_cmd(*move_right.ptz_cmd_value()[1:])
        time.sleep(5)
        ptz_obj._exe_ptz_cmd(*move_stop.ptz_cmd_value()[1:])
        time.sleep(5)

        #上
        move_up = ONVIF_XML_Parser(move_up_xml)
        ptz_obj._exe_ptz_cmd(*move_up.ptz_cmd_value()[1:])
        time.sleep(5)
        ptz_obj._exe_ptz_cmd(*move_stop.ptz_cmd_value()[1:])
        time.sleep(5)

        #下
        move_down = ONVIF_XML_Parser(move_down_xml)
        ptz_obj._exe_ptz_cmd(*move_down.ptz_cmd_value()[1:])
        time.sleep(5)
        ptz_obj._exe_ptz_cmd(*move_stop.ptz_cmd_value()[1:])
        time.sleep(5)

        #左上
        move_left_up = ONVIF_XML_Parser(move_left_up_xml)
        ptz_obj._exe_ptz_cmd(*move_left_up.ptz_cmd_value()[1:])
        time.sleep(5)
        ptz_obj._exe_ptz_cmd(*move_stop.ptz_cmd_value()[1:])
        time.sleep(5)

        #右下
        move_right_down = ONVIF_XML_Parser(move_right_down_xml)
        ptz_obj._exe_ptz_cmd(*move_right_down.ptz_cmd_value()[1:])
        time.sleep(5)
        ptz_obj._exe_ptz_cmd(*move_stop.ptz_cmd_value()[1:])
        time.sleep(5)

        #左下
        move_left_down = ONVIF_XML_Parser(move_left_down_xml)
        ptz_obj._exe_ptz_cmd(*move_left_down.ptz_cmd_value()[1:])
        time.sleep(5)
        ptz_obj._exe_ptz_cmd(*move_stop.ptz_cmd_value()[1:])
        time.sleep(5)

        #右上
        move_right_up = ONVIF_XML_Parser(move_right_up_xml)
        ptz_obj._exe_ptz_cmd(*move_right_up.ptz_cmd_value()[1:])
        time.sleep(5)
        ptz_obj._exe_ptz_cmd(*move_stop.ptz_cmd_value()[1:])
        time.sleep(5)

