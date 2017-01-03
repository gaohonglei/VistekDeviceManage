import sys
if sys.version_info < (3, 5):
    import gb28181, gb28181_wrap
    from gb28181 import request_cmd,try_process_device
    from gb28181_wrap import getStreamUrlQueue,getStatusQueue,getChannelChangeQueue
    __all__ =["hikvision", "hikvision_wrap"]