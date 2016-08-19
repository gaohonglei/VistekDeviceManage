#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
if sys.version_info < (3, 5):
    import device_process, device_center_client, device_dispatch_client, device_dispatch_server, device_dispatch_manager

    __all__ = ["device_process", "device_center_client", "device_dispatch_client", "device_dispatch_server", "device_dispatch_manager"]
else:
    from . import device_process, device_center_client, device_dispatch_client, device_dispatch_server, device_dispatch_manager
