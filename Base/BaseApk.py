#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Guzb'

import re
from math import floor
import subprocess
import os
from Base.BaseLoggers import logger


class ApkInfo:
    """apk文件的读取信息"""
    def __init__(self, apk_path):
        self.apk_path = apk_path
        print(self.apk_path)
        p = subprocess.Popen("aapt dump badging %s" % self.apk_path, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True, encoding='utf-8')
        (output, err) = p.communicate()
        if err:
            print(err)
        if 'dump failed' in err or 'dump failed' in output:
            p = subprocess.Popen("aapt2 dump badging %s" % self.apk_path, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE, shell=True, encoding='utf-8')
            (output, err) = p.communicate()
        if err:
            print(err)
        self.base_info = output

    def get_size(self):
        """
        获取app的文件大小
        :return: str,单位M
        """
        print("\n=====get_size=========")
        size = floor(os.path.getsize(self.apk_path) / (1024 * 1000))
        size = str(size) + "M"
        print(size)
        return size

    def get_package_name(self):
        """
        获取包名
        :return: str
        """
        print("\n=====get_package_name=========")
        package_name = re.findall("package: name='(.*?)'", self.base_info)
        if not package_name:
            print('找不到')
        else:
            print(package_name)
        return package_name[0]

    def get_version_code(self):
        """
        获取版本码
        :return: str
        """
        print("\n=====get_version_code=========")
        version_code = re.findall("package:.*versionCode='(.*?)'", self.base_info)
        if not version_code:
            print('找不到')
        else:
            print(version_code)
        return version_code[0]

    def get_version_name(self):
        """
        获取版本号
        :return: str
        """
        print("\n=====get_version_name=========")
        version_name = re.findall("package:.*versionName='(.*?)'", self.base_info)
        if not version_name:
            print('找不到')
        else:
            print(version_name)
        return version_name[0]

    def get_app_name(self):
        """
        获取应用名称
        :return: str
        """
        print("\n=====get_app_name=========")
        t = self.base_info.split()
        for item in t:
            # print(item)
            match = re.compile(r"application-label:(\S+)").search(item)
            if match is not None:
                app_name = match.group(1)
                print(app_name)
                return app_name

    def get_activity(self):
        """
        获取启动类
        :return: str
        """
        print("\n=====get_activity=========")
        match = re.compile(r"launchable-activity: name=(\S+)").search(self.base_info)
        if match is not None:
            activity = match.group(1)
            print(activity)
            return activity


if __name__ == '__main__':
    app_pkg_path = r"D:\git_work\uiautotest\ydzj\app\ydzj_3.1.5_test.apk"
    apk_info = ApkInfo(app_pkg_path)
    apk_info.get_activity()
    apk_info.get_app_name()
    apk_info.get_package_name()
    apk_info.get_size()
    apk_info.get_version_code()
    apk_info.get_version_name()


