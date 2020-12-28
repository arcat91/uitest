# -*- coding: utf-8 -*-
import os
import re
import subprocess
from time import sleep
from requests import get
from Base.BaseApk import ApkInfo
from Base.BaseLoggers import logger
from Base.utils import loop_accept_alert
from threading import Thread


def adb_command(device, cmd, result_to_lines=True):
    exc_cmd = 'adb -s %s %s' % (device, cmd)
    print(exc_cmd)
    if result_to_lines:
        result = subprocess.Popen(exc_cmd, shell=True,
                                  stdout=subprocess.PIPE).stdout.readlines()
        result_list = []
        if len(result) == 1:
            return result[0].decode().rstrip()
        else:
            for i in result:
                result_list.append(i.decode().rstrip())
            return result_list
    else:
        result = subprocess.Popen(exc_cmd, shell=True,
                                  stdout=subprocess.PIPE).stdout.read()
        return result.decode()


# 获取手机信息
def get_phone_info(device):
    """获取设备信息，key=[release, model, brand, device]
    :param device:连接的设备SN或IP地址
    :return: dict
    """
    result = dict(release=adb_command(device, 'shell getprop ro.build.version.release'),
                  model=adb_command(device, 'shell getprop ro.product.model'),
                  brand=adb_command(device, 'shell getprop ro.product.device'),
                  device=adb_command(device, 'shell getprop ro.product.device'),
                  platform_version=adb_command(device, 'shell getprop ro.build.version.sdk'))
    return result


# 获取最大运行内存
def get_men_total(device):
    cmd = "adb -s " + device + " shell cat /proc/meminfo"
    get_cmd = os.popen(cmd).readlines()
    men_total = 0
    men_total_str = "MemTotal"
    for line in get_cmd:
        if line.find(men_total_str) >= 0:
            men_total = line[len(men_total_str) + 1:].replace("kB", "").strip()
            break
    return int(men_total)


# 获取几核cpu
def get_cpu_kel(device):
    cmd = "adb -s " + device + " shell cat /proc/cpuinfo"
    get_cmd = os.popen(cmd).readlines()
    find_str = "processor"
    int_cpu = 0
    for line in get_cmd:
        if line.find(find_str) >= 0:
            int_cpu += 1
    return str(int_cpu) + "核"


# 获取手机分辨率
def get_app_pix(device):
    result = os.popen("adb -s " + device + " shell wm size", "r")
    size = result.readline().split("Physical size:")[1].strip().split('x')
    width = int(size[0])
    height = int(size[1])
    return {'width': width, 'height': height}


def get_webview(device, package, activity):
    """
    从正在运行的webview中，找到需要的webview
    :param device: 设备sn
    :param package: 包名
    :param activity: 启动名
    :return:
    """
    # 启动app
    cmd = 'adb -s %s shell "am start %s/%s"' % (device, package, activity)
    os.popen(cmd)
    sleep(3)
    # 获取webview
    cmd = 'adb -s %s shell "cat /proc/net/unix | grep -a webview"' % device
    result = os.popen(cmd).readlines()
    webview_list = []
    for line in result:
        line = line.strip()
        if line:
            webview_list.append(line.split('@')[1])
    return webview_list


def get_webview_version(device, package, activity):
    """根据获取的webview，依次开启本地监听
    :param device: 设备sn
    :param package: 包名
    :param activity: 启动名
    :return:
    """
    webview_list = get_webview(device, package, activity)
    port = 5000
    port_list = []
    for webview in webview_list:
        adb_command(device, 'forward tcp:%d localabstract:%s' % (port, webview))
        port_list.append(port)
        port = port + 1
    # 向本地监听依次发送请求，根据包名确定哪个是需要的webview，然后获取对应的webview版本
    for port in port_list:
        json_response = get('http://localhost:%d/json/version' % port).json()
        print(json_response)
        if json_response['Android-Package'] == package:
            webview_version = re.findall(r'Chrome/(\d{2})', json_response['Browser'])[0]
            print('检测到当前设备的webview版本为%s' % webview_version)
            return webview_version


def install_app(driver, device, app_pkg):
    # 手机是否已安装app，未安装则直接安装
    apk = ApkInfo(app_pkg)
    pkg_name = apk.get_package_name()
    installed_pkg = adb_command(device, 'shell pm list package', False)
    if pkg_name not in installed_pkg:
        logger.info('app未安装，正在安装')
        Thread(target=loop_accept_alert, args=[driver]).start()  # 启动多线程处理弹框
        adb_command(device, 'install --no-streaming %s' % app_pkg)
        logger.info('app安装完成')
        return
    # 已安装与待安装的app版本号是否一致，不一致则卸载重装
    new_version = apk.get_version_code()
    old_version = re.findall(r'versionCode=(\d+)', adb_command(device, 'shell dumpsys package %s' % pkg_name, False))[0]
    logger.info('新版本号:%s 旧版本号:%s' % (new_version, old_version))
    if new_version != old_version:
        logger.info('app版本号不一致，卸载重装')
        adb_command(device, 'uninstall %s' % pkg_name)
        Thread(target=loop_accept_alert, args=[driver]).start()  # 启动多线程处理弹框
        adb_command(device, 'install --no-streaming %s' % app_pkg)
        logger.info('app安装完成')
        return
    logger.info('app已安装，无需安装')


if __name__ == "__main__":
    # get_phone_info("192.168.3.33:6666")
    # get_phone_info('A10EBMM2D722')
    # print(get_app_pix('emulator-5554'))
    # print(get_webview('A10EBMM2D722'))
    # print(get_webview_version('A10EBMM2D722', 'com.mysoft.checkqualitytest'))
    # get_webview_version('734bde2e', 'com.mysoft.checkqualitytest', 'com.mysoft.core.activity.DaemonActivity')
    # get_webview_version('A10EBMM2D722', 'com.mysoft.checkqualitytest', 'com.mysoft.core.activity.DaemonActivity')
    print(get_phone_info('8811e5e1'))
