#!/usr/bin/env python
# -*- coding=utf-8 -*-

"""
@version: 0.0.1
@author: lee
@license: Apache Licence
@contact: shida23577@hotmail.com
@software: PyCharm Community Edition
@file: PTZParser.py
@time: 2016/4/12 9:56
"""
import traceback, math
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET
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
                 V_PTZ_FOCUS_NEAR=11, V_PTZ_PRESET_ADD=12, V_PTZ_PRESET_DEL=13, V_PTZ_PRESET_GOTO=14, V_PTZ_LIGHT=15,
                 V_PTZ_SWIPER=16, V_PTZ_HEATER=17, V_PTZ_IRIS_OPEN=18, V_PTZ_IRIS_CLOSE=19, V_PTZ_STOP=20)
V_PTZ_XML_ATTR_NAME = enum(V_PTZ_DEV_ID_ATTR_NAME = "deviceid", V_PTZ_DEV_CHANNEL_INDEX_ATTR_NAME = "channelindex",
                           V_PTZ_USER_ID_ATTR_NAME = "userid", V_PTZ_USER_LEVEL_ATTR_NAME = "userlevel")
class ptzParser():
    """
    """
    def __init__(self, content):
        """
        :param content:str ptz_cmd xml content.
        :rtype: None
        """
        self._xml = content
        #self._ptz_cmd = self._parsePtzMsg(self._xml)
        self.ptz_cmd = self._parsePtzMsg(self._xml)

    @property
    def ptz_cmd(self):
        if self._ptz_cmd is not None:
            return self._ptz_cmd
        else:
            return None
    @ptz_cmd.setter
    def ptz_cmd(self, cmd):
        self._ptz_cmd = cmd
    def _parsePtzMsg(self, msg):
        """
        parse ptz cmd msg.
        :param msg:
        :return (device_id, device_channel, PTZ_CMD, params)
        :rtype tuple
        """
        #msg = self._xml
        try:
            if msg is not None and isinstance(msg, str):
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
                            return cmd(cmd_node)
                        else:
                            return None
                    ptz_param = None
                    base_param = (dev_id_attr, dev_channel_attr)
                    move_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_MOVE_NODE_NAME, "_parse_move")
                    if move_param is not None:
                        return (base_param + move_param)
                    stop_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_STOP_NODE_NAME, "_parse_stop")
                    if stop_param is not None:
                        return (base_param + stop_param)
                    iris_open_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_IRIS_OPEN_NODE_NAME, "_parse_iris_open")
                    if iris_open_param is not None:
                        return (base_param + iris_open_param)
                    iris_close_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_IRIS_CLOSE_NODE_NAME, "_parse_iris_close")
                    if iris_close_param is not None:
                        return (base_param + iris_close_param)
                    focus_far_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_FOCUSFORWARD_NODE_NAME, "_parse_focus_far" )
                    if focus_far_param is not None:
                        return (base_param + focus_far_param)
                    focus_near_pararm = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_FOCUSBACKWARD_NODE_NAME, "_parse_focus_near")
                    if focus_near_pararm is not None:
                        return (base_param + focus_near_pararm)
                    zoom_in_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_ZOOMIN_NODE_NAME, "_parse_zoom_in")
                    if zoom_in_param is not None:
                        return (base_param + zoom_in_param)
                    zoom_out_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_ZOOMOUT_NODE_NAME, "_parse_zoom_out")
                    if zoom_out_param is not None:
                        return (base_param + zoom_out_param)
                    preset_add_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_PRESETADD_NODE_NAME, "_parse_preset_add")
                    if preset_add_param is not None:
                        return (base_param + preset_add_param)
                    preset_del_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_PRESETREMOVE_NODE_NAME, "_parse_preset_del")
                    if preset_del_param is not None:
                        return (base_param + preset_del_param)
                    preset_goto_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_PRESETGOTO_NODE_NAME, "_parse_preset_goto")
                    if preset_goto_param is not None:
                        return (base_param + preset_goto_param)
                    light_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_LIGHT_NODE_NAME, "_parse_light")
                    if light_param is not None:
                        return (base_param + light_param)
                    swiper_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_SWIPER_NODE_NAME, "_parse_swiper")
                    if swiper_param is not None:
                        return (base_param + swiper_param)
                    heater_param = same_func(V_PTZ_XML_NODE_NAME.V_PTZ_HEATER_NODE_NAME, "_parse_heater")
                    if heater_param is not None:
                        return (base_param + heater_param)
                else:
                    return (False, V_PTZ_NONE)
            else:
                return (False, V_PTZ_NONE)
        except:
            traceback.print_exc()


    def _parse_move(self, move_node):
        if move_node is None:
            return None
        else:
            p_attr = float(move_node.get("p"))
            t_attr = float(move_node.get("t"))
            z_attr = float(move_node.get("z"))
            ptz_move_cmd = None
            ptz_move_speed = None

            if p_attr == 0 and 0 == t_attr and 0 == z_attr:
                ptz_move_cmd = V_PTZ_CMD.V_PTZ_NONE
                return (ptz_move_cmd, ptz_move_speed)
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
                    ptz_move_cmd = V_PTZ_CMD.V_PTZ_LEFT_UP
                elif 0 > p_attr and 0 > t_attr:
                    ptz_move_cmd = V_PTZ_CMD.V_PTZ_LEFT_DOWN
                ptz_move_speed = min(math.fabs(p_attr), math.fabs(t_attr))

            if p_attr == 0 and 0 == t_attr:
                ptz_move_speed = math.fabs(z_attr)
                if 0 < z_attr:
                    ptz_move_cmd = V_PTZ_CMD.V_PTZ_ZOOM_IN
                else:
                    ptz_move_cmd = V_PTZ_CMD.V_PTZ_ZOOM_OUT
            return (ptz_move_cmd, ptz_move_speed)

    def _parse_stop(self, stop_node):
        if stop_node is None:
            return None
        else:
            ptz_stop_cmd = V_PTZ_CMD.V_PTZ_STOP
        return (ptz_stop_cmd,)

    def _parse_iris_open(self, iris_open_node):
        if iris_open_node is None:
            return None
        else:
            value_attr = float(iris_open_node.get("value"))
            ptz_iris_cmd = V_PTZ_CMD.V_PTZ_IRIS_OPEN
            ptz_iris_speed = math.fabs(value_attr)
            return (ptz_iris_cmd, ptz_iris_speed)

    def _parse_iris_close(self, iris_close_node):
        if iris_close_node is None:
            return None
        else:
            value_attr = float(iris_close_node.get("value"))
            ptz_iris_cmd = V_PTZ_CMD.V_PTZ_IRIS_CLOSE
            ptz_iris_speed = math.fabs(value_attr)
            return (ptz_iris_cmd, ptz_iris_speed)

    def _parse_focus_far(self, focus_far_node):
        if focus_far_node is None:
            return None
        else:
            value_attr = float(focus_far_node.get("value"))
            focus_cmd = V_PTZ_CMD.V_PTZ_FOCUS_FAR
            focus_speed = math.fabs(value_attr)
            return (focus_cmd, focus_speed)

    def _parse_focus_near(self, focus_near_node):
        if focus_near_node is None:
            return None
        else:
            value_attr = float(focus_near_node.get("value"))
            focus_cmd = V_PTZ_CMD.V_PTZ_FOCUS_NEAR
            focus_speed = math.fabs(value_attr)
            return (focus_cmd, focus_speed)

    def _parse_zoom_in(self, zoom_in_node):
        if zoom_in_node is None:
            return None
        else:
            value_attr = float(zoom_in_node.get("value"))
            zoom_cmd = V_PTZ_CMD.V_PTZ_ZOOM_IN
            zoom_speed = math.fabs(value_attr)
            return (zoom_cmd, zoom_speed)

    def _parse_zoom_out(self, zoom_out_node):
        if zoom_out_node is None:
            return None
        else:
            value_attr = float(zoom_out_node.get("value"))
            zoom_cmd = V_PTZ_CMD.V_PTZ_ZOOM_OUT
            zoom_speed = math.fabs(value_attr)
            return (zoom_cmd, zoom_speed)

    def _parse_preset_add(self, preset_add_node):
        if preset_add_node is None:
            return None
        else:
            preset = preset_add_node.get("value")
            preset_cmd = V_PTZ_CMD.V_PTZ_PRESET_ADD
            preset_add_index = math.fabs(int(preset))
            return (preset_cmd, preset_add_index)

    def _parse_preset_del(self, preset_del_node):
        if preset_del_node is None:
            return None
        else:
            preset = preset_del_node.get("value")
            preset_cmd = V_PTZ_CMD.V_PTZ_PRESET_DEL
            preset_del_index = math.fabs(int(preset))
            return (preset_cmd, preset_del_index)

    def _parse_preset_goto(self, preset_goto_node):
        if preset_goto_node is None:
            return None
        else:
            preset = preset_goto_node.get("value")
            preset_cmd = V_PTZ_CMD.V_PTZ_PRESET_GOTO
            preset_goto_index = math.fabs(int(preset))
            return (preset_cmd, preset_goto_index)

    def _parse_light(self, light_node):
        pass

    def _parse_swiper(self, swiper_node):
        pass

    def _parse_heater(self, heater_node):
        pass

"""
<ptz>
	 <move p="1" t="1" z="1">
	 <stop>
	 <PTZIrisOpen value="0.5"/>
	 <PTZIrisClose value="0.5"/>
	 <PTZFocusForward value="0.5"/>
	 <PTZFocusBackward value="0.5"/>
	 <PTZZoomIn value="0.5"/>
	 <PTZZoomOut value="0.5"/>

	 <PTZPresetAdd value="0"/>
	 <PTZPresetRemove value="0"/>
	 <PTZPresetGoto value="0"/>
	 <LIGHT value="0"/>
	 <SWIPER value="1"/>
	 <HEATER value="0"/>
</ptz>
"""
if __name__ == "__main__":
    move_xml = "<ptz> <move p=\"1\" t=\"1\" z=\"0.0\"> </ptz>"
    ptzParser(move_xml)
