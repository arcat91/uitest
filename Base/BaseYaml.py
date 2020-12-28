#!/usr/bin/python
# -*- coding: utf-8 -*-
import yaml
from Base.BaseLoggers import logger


# 获取yaml文件信息，传入一个文件路径
def get_yaml(yaml_file):
    try:
        with open(yaml_file, encoding='utf-8') as f:
            x = yaml.load(f, Loader=yaml.FullLoader)
            return x
    except FileNotFoundError:
        print(u"找不到文件,路径是:\n %s" % yaml_file)
