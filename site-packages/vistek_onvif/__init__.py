#!/usr/bin/env python

import sys

if sys.version_info < (3, 5):
    import onvif_wrap
    from vonvif import request_cmd, getStatusQueue, try_process_device, getCurrentDeviceInfo

    __all__ =["vonvif", "onvif_wrap"]
else:
    from . import onvif_wrap
    from .vonvif import request_cmd, getStatusQueue, try_process_device
