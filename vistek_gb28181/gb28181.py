# --*-- coding=UTF-8 --*--
import vistek_util.PTZParser as PTZParser

from collections import defaultdict
from urlobject import URLObject
import inspect
import gb28181_wrap



class uri_parser():
    """uri parser"""
    def __init__(self, uri):
        """init function"""
        self.uri = URLObject(uri)
        self.params = self.uri.query.dict

    def user_name(self):
        return self.uri.username

    def password(self):
        return self.uri.password

    def ip(self):
        return self.uri.hostname

    def port(self):
        return self.uri.port

    def add_func_param(self, param):
        self.params.update(param)

    def func_name(self, name):
        query = self.uri.query.dict

        if query.has_key(name):
            return query[name]
        else:
            return ''

    def func_params(self, name):
        query = self.uri.query.dict
        if query[name] == 'register_device':
            self.add_func_param({'ip': self.uri.hostname})
            self.add_func_param({'port': self.uri.port})
            self.add_func_param({'user_name': self.uri.username})
            self.add_func_param({'user_pwd': self.uri.password})
        if self.params.has_key(name):
            self.params.pop(name)
        return self.params

def try_process_device(device):
    func = getattr(gb28181_wrap, "try_process_device")
    if func:
        out_data = func(device, timeout=5)
        return out_data
    else:
        return None

def request_cmd(device_id, uri, params):
    """device cmd"""
    res_data = list()
    func_lists = dir(gb28181_wrap)
    parser = uri_parser(uri)
    parser.add_func_param({'device_id': device_id})
    func_name = parser.func_name('func')
    if func_name in func_lists:
        cmd_func = getattr(gb28181_wrap, func_name)
        cmd_params = parser.func_params('func')
        params_lists = []
        need_args = inspect.getargspec(cmd_func).args
        for call_args in need_args:
            if cmd_params.has_key(call_args):
                params_lists.append(cmd_params.get(call_args))
        # logger.debug("cmd=%s args:%s args_value:%s", func_name, inspect.getargspec(cmd_func).args, params_lists)
        if func_name == 'register_device':
            out_data = cmd_func(device = params)
        else:
            out_data = cmd_func(**cmd_params)
        return out_data
    else:
        return ('', 0)