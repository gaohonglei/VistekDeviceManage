#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
@version: 0.0.1
@author: lee
@license: Apache Licence
@contact: shida23577@hotmail.com
@software: PyCharm Community Edition
@file: device_callback.py
@time: 2016/4/8 9:58
"""

import math
try:
    import Queue
except:
    import queue as Queue
def enum(**enums):
    return type('Enum', (), enums)
V_PTZ_XML_NODE_NAME = enum(V_PTZ_MOVE_NODE_NAME = "move", V_PTZ_STOP_NODE_NAME = "stop",
                           V_PTZ_IRIS_OPEN_NODE_NAME="PTZIrisOpen", V_PTZ_IRIS_CLOSE_NODE_NAME="PTZIrisClose",
                           V_PTZ_FOCUSFORWARD_NODE_NAME="PTZFocusForward", V_PTZ_FOCUSBACKWARD_NODE_NAME="PTZFocusBackward",
                           V_PTZ_ZOOMIN_NODE_NAME="PTZZoomIn", V_PTZ_ZOOMOUT_NODE_NAME="PTZZoomOut",
                           V_PTZ_PRESETADD_NODE_NAME="PTZPresetAdd", V_PTZ_PRESETREMOVE_NODE_NAME="PTZPresetRemove",
                           V_PTZ_PRESETGOTO_NODE_NAME="PTZPresetGoto", V_PTZ_LIGHT_NODE_NAME="LIGHT",
                           V_PTZ_SWIPER_NODE_NAME="SWIPER", V_PTZ_HEATER_NODE_NAME="HEATER")
V_PTZ_CMD = enum(V_PTZ_NONE=-1, V_PTZ_UP=0, V_PTZ_DOWN=1, V_PTZ_LEFT=2, V_PTZ_RIGHT=3, V_PTZ_LEFT_UP=4, V_PTZ_LEFT_DOWN=5,
                 V_PTZ_RIGHT_UP=6, V_PTZ_RIGHT_DOWN=7, V_PTZ_ZOOM_IN=8, V_PTZ_ZOOM_OUT=9, V_PTZ_FOCUS_FAR=10,
                 V_PTZ_FOUCE_NEAR=11, V_PTZ_PRESET_ADD=12, V_PTZ_PRESET_DEL=13, V_PTZ_PRSET_GOTO=14, V_PTZ_LIGHT=15,
                 V_PTZ_SWIPER=16, V_PTZ_HEATER=17, V_PTZ_IRIS_OPEN=18, V_PTZ_IRIS_CLOSE=19, V_PTZ_STOP=20)
V_PTZ_XML_ATTR_NAME = enum(V_PTZ_DEV_ID_ATTR_NAME = "deviceid", V_PTZ_DEV_CHANNEL_INDEX_ATTR_NAME = "channelindex",
                           V_PTZ_USER_ID_ATTR_NAME = "userid", V_PTZ_USER_LEVEL_ATTR_NAME = "userlevel")
import Vistek.Device as v_device
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET
class deviceCallBackI(v_device.DeviceCallback):
    def __init__(self):
        self._cmd_queue = Queue.Queue()
        self._ptz_sender = None
        self._device_change_sender = None
    def MessageReceived(self, msg, c):
        print("receive-msg:{0}".format(msg))
        if msg and 0 < len(msg.body):
            #ret, cmd = self._parsePtzMsg(msg.body)
            if self._ptz_sender is not None:
                self._cmd_queue.put(msg)
                self._ptz_sender(msg)
                print("comehere")
                #self._ptz_sender()

    def DeviceChangedNotify(self, device, changetype, c):
       if self._device_change_sender is not None:
           self._device_change_sender(device, changetype)

    def DeviceVideoChannelChangedNotify(self, channel, changetype, c):
        if self._device_change_sender is not None:
            self._device_change_sender(channel, changetype)

    def subscribe_ptz_cmd(self, callback):
        self._ptz_sender = callback

    def subscribe_device_change(self, callback):
        self._device_change_sender = callback

    @property
    def cmdQueue(self):
        return self._cmd_queue

    def DuplexMessageReceived(self, msg, c):
        pass

    def _parsePtzMsg(self, msg):
        """
        parse ptz cmd msg.
        :param msg:
        """
        if isinstance(msg, str):
            root_node = ET.fromstring(msg)
            if root_node is not None:
                dev_id_attr = root_node.get(V_PTZ_XML_ATTR_NAME.V_PTZ_DEV_ID_ATTR_NAME)
                dev_channel_attr = root_node.get(V_PTZ_XML_ATTR_NAME.V_PTZ_DEV_CHANNEL_INDEX_ATTR_NAME)
                user_id_attr = root_node.get(V_PTZ_XML_ATTR_NAME.V_PTZ_USER_ID_ATTR_NAME)
                user_level_attr = root_node.get(V_PTZ_XML_ATTR_NAME.V_PTZ_USER_LEVEL_ATTR_NAME)
                def same_func(name, cmd_name):
                    cmd_node = root_node.find(name)
                    cmd = getattr(self, cmd_name)
                    if cmd:
                        cmd(cmd_node)
                    else:
                        return None

                move_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_MOVE_NODE_NAME, "__parse_move")
                if move_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(move_param)
                    self._ptz_sender(*move_param)
                    return move_param
                stop_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_STOP_NODE_NAME, "__parse_stop")
                if stop_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(stop_param)
                    self._ptz_sender(*move_param)
                    return stop_param
                iris_open_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_IRIS_OPEN_NODE_NAME, "__parse_iris_open")
                if iris_open_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(iris_open_param)
                    self._ptz_sender(*move_param)
                    return iris_open_param
                iris_close_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_IRIS_CLOSE_NODE_NAME, "__parse_iris_close")
                if iris_close_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(iris_close_param)
                    self._ptz_sender(*move_param)
                    return iris_close_param
                focus_far_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_FOCUSFORWARD_NODE_NAME, "__parse_focus_far" )
                if focus_far_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(focus_far_param)
                    self._ptz_sender(*move_param)
                    return focus_far_param
                focus_near_pararm = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_FOCUSBACKWARD_NODE_NAME, "__parse_focus_near")
                if focus_near_pararm is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(focus_near_pararm)
                    self._ptz_sender(*move_param)
                    return focus_near_pararm
                zoom_in_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_ZOOMIN_NODE_NAME, "__parse_zoom_in")
                if zoom_in_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(zoom_in_param)
                    self._ptz_sender(*move_param)
                    return zoom_in_param
                zoom_out_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_ZOOMOUT_NODE_NAME, "__parse_zoom_out")
                if zoom_out_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(zoom_out_param)
                    self._ptz_sender(*move_param)
                    return zoom_out_param
                preset_add_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_PRESETADD_NODE_NAME, "__parse_preset_add")
                if preset_add_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(preset_add_param)
                    self._ptz_sender(*move_param)
                    return preset_add_param
                preset_del_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_PRESETREMOVE_NODE_NAME, "__parse_preset_del")
                if preset_del_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(preset_del_param)
                    self._ptz_sender(*move_param)
                    return preset_del_param
                preset_goto_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_PRESETGOTO_NODE_NAME, "__parse_preset_goto")
                if preset_goto_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(preset_goto_param)
                    self._ptz_sender(*move_param)
                    return preset_goto_param
                light_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_LIGHT_NODE_NAME, "__parse_light")
                if light_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(light_param)
                    self._ptz_sender(*move_param)
                    return light_param
                swiper_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_SWIPER_NODE_NAME, "__parse_swiper")
                if swiper_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(swiper_param)
                    self._ptz_sender(*move_param)
                    return swiper_param
                heater_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_HEATER_NODE_NAME, "__parse_heater")
                if heater_param is not None and self._ptz_sender is not None:
                    self._cmd_queue.put(heater_param)
                    self._ptz_sender(*move_param)
                    return heater_param
            else:
                return (False, V_PTZ_NONE)
        else:
            return (False, V_PTZ_NONE)

    def __parse_move(self, move_node):
        if move_node is None:
            return None
        else:
            p_attr = move_node.get("p")
            t_attr = move_node.get("t")
            z_attr = move_node.get("z")
            ptz_move_cmd = None
            ptz_move_speed = None
            if p_attr*t_attr == 0:
                if 0 == p_attr and  0 !=  t_attr:
                    if 0 < t_attr:
                        ptz_move_cmd = V_PTZ_CMD.V_PTZ_UP
                    else:
                        ptz_move_cmd = V_PTZ_CMD.V_PTZ_DOWN
                    ptz_move_speed = math.fabs(t_attr)
                elif 0 == t_attr and 0 != p_attr:
                    if 0 < p_attr:
                        ptz_move_cmd = V_PTZ_CMD.V_PTZ_RIGHT
                    else:
                        ptz_move_cmd = V_PTZ_CMD.V_PTZ_LEFT
                    ptz_move_speed = math.fabs(p_attr)
                else:
                    ptz_move_cmd = V_PTZ_CMD.V_PTZ_NONE
            else:
               if 0 < p_attr and 0 < t_attr:
                   ptz_move_cmd = V_PTZ_CMD.V_PTZ_RIGHT_UP
               elif 0 < p_attr and 0 > t_attr:
                   ptz_move_cmd = V_PTZ_CMD.V_PTZ_RIGHT_DOWN
               elif 0 > p_attr and 0 < t_attr:
                   ptz_move_cmd = V_PTZ_CMD.V_PTZ_LEFTUP
               elif 0 > p_attr and 0 > t_attr:
                   ptz_move_cmd = V_PTZ_CMD.V_PTZ_LEFTDOWN
               ptz_move_speed = min(math.fabs(p_attr), math.fabs(t_attr))
            return (ptz_move_cmd, ptz_move_speed)

    def __parse_stop(self, stop_node):
        if stop_node is None:
            return None
        else:
            ptz_stop_cmd = V_PTZ_CMD.V_PTZ_STOP
        return (ptz_stop_cmd)

    def __parse_iris_open(self, iris_open_node):
        if iris_open_node is None:
            return None
        else:
            value_attr = iris_open_node.get("value")
            ptz_iris_cmd = V_PTZ_CMD.V_PTZ_IRIS_OPEN
            ptz_iris_speed = math.fabs(value_attr)
            return (ptz_iris_cmd, ptz_iris_speed)

    def __parse_iris_close(self, iris_close_node):
        if iris_close_node is None:
            return None
        else:
            value_attr = iris_close_node.get("value")
            ptz_iris_cmd = V_PTZ_CMD.V_PTZ_IRIS_OPEN
            ptz_iris_speed = math.fabs(value_attr)
            return (ptz_iris_cmd, ptz_iris_speed)

    def __parse_focus_far(self, focus_far_node):
        if focus_far_node is None:
            return None
        else:
            value_attr = focus_far_node.get("value")
            focus_cmd = V_PTZ_CMD.V_PTZ_FOCUS_FAR
            focus_speed = math.fabs(value_attr)
            return (focus_cmd, focus_speed)

    def __parse_focus_near(self, focus_near_node):
        if focus_near_node is None:
            return None
        else:
            value_attr = focus_near_node.get("value")
            focus_cmd = V_PTZ_CMD.V_PTZ_FOCUS_FAR
            focus_speed = math.fabs(value_attr)
            return (focus_cmd, focus_speed)

    def __parse_zoom_in(self, zoom_in_node):
        if zoom_in_node is None:
            return None
        else:
            value_attr = zoom_in_node.get("value")
            zoom_cmd = V_PTZ_CMD.V_PTZ_ZOOM_IN
            zoom_speed = math.fabs(value_attr)
            return (zoom_cmd, zoom_speed)

    def __parse_zoom_out(self, zoom_out_node):
        if zoom_out_node is None:
            return None
        else:
            value_attr = zoom_out_node.get("value")
            zoom_cmd = V_PTZ_CMD.V_PTZ_ZOOM_IN
            zoom_speed = math.fabs(value_attr)
            return (zoom_cmd, zoom_speed)

    def __parse_preset_add(self, preset_add_node):
        if preset_add_node is None:
            return None
        else:
            preset = preset_add_node.get("value")
            preset_cmd = V_PTZ_CMD.V_PTZ_PRESET_ADD
            preset_add_index = math.fabs(int(preset))
            return (preset_cmd, preset_add_index)

    def __parse_preset_del(self, preset_del_node):
        if preset_del_node is None:
            return None
        else:
            preset = preset_del_node.get("value")
            preset_cmd = V_PTZ_CMD.V_PTZ_PRESET_ADD
            preset_del_index = math.fabs(int(preset))
            return (preset_cmd, preset_del_index)

    def __parse_preset_goto(self, preset_goto_node):
        if preset_goto_node is None:
            return None
        else:
            preset = preset_goto_node.get("value")
            preset_cmd = V_PTZ_CMD.V_PTZ_PRESET_ADD
            preset_goto_index = math.fabs(int(preset))
            return (preset_cmd, preset_goto_index)

    def __parse_light(self, light_node):
        pass

    def __parse_swiper(self, swiper_node):
        pass

    def __parse_heater(self, heater_node):
        pass

