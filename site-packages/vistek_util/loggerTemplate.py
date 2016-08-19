#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logbook, sys
from logbook import Logger, LoggerGroup


def getLogger(name, file_name):
    v_logger = Logger(name=name, level=logbook.DEBUG)
    file_handler = logbook.FileHandler(file_name, level=logbook.DEBUG, format_string="[{record.time:%Y-%m-%d %H:%M:%S}] [{record.level_name}] [{record.filename}:{record.lineno}] [{record.module}:{record.func_name}] [{record.message}]")
    stream_handler = logbook.StreamHandler(sys.stdout, level=logbook.DEBUG, format_string="[{record.time:%Y-%m-%d %H:%M:%S}] [{record.level_name}] [{record.filename}:{record.lineno}] [{record.module}:{record.func_name}] [{record.message}]", bubble=True)
    file_handler.push_application()
    stream_handler.push_application()
    return v_logger



if __name__ == "__main__":
    vlogger = getLogger(name="testdd", file_name="test1.log")
    out_str = "jfslf{0}{1}".format("djfsl", vlogger)
    vlogger.debug(out_str)
