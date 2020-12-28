#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import os.path
import socket
import logging
import logging.handlers
from Base.utils import singleton


@singleton
class JFMlogging(object):
    logger = logging.getLogger()

    def __init__(self):
        host_name = socket.gethostname()
        logging_msg_format = f'[%(asctime)s] [%(levelname)s] [{host_name}] [%(module)s.py - line:%(lineno)d] %(message)s'
        self.logger.setLevel(logging.INFO)

        log_path = 'logs'  # 日志存放目录
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        log_file = os.path.join(log_path, 'system.log')

        # 日志记录到文件
        file_handler = logging.handlers.TimedRotatingFileHandler(log_file, 'midnight', 1)
        file_handler.setFormatter(logging.Formatter(logging_msg_format))
        self.logger.addHandler(file_handler)

        # 日志输出到命令行
        logging.raiseExceptions = False  # 关闭记录方法的异常提示
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(logging_msg_format))
        self.logger.addHandler(stream_handler)

    def getloger(self):
        return self.logger


logger = JFMlogging().getloger()
