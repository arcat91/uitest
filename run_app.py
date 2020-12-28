#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytest
import os
import argparse
from Base.BaseYaml import get_yaml
from Base.BaseConfig import dir_time, ConfigInfo, DeviceInfo, root_path
from Base.BaseDriver import AppInit
import shelve
from Base.AutoAppium import AutoAppium
import traceback
from random import randint

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('product', help='产品编码，如移动质检为ydzj，请与产品目录名称保持一致')
parser.add_argument('env', help='环境编码，如测试环境为test，请与产品目录的config.yaml的env参数保持一致')
parser.add_argument('device', help='设备别名，如魅族手机为meizu，请确保./config/devices.yaml已配置该设备信息')
parser.add_argument('--testsuite', help='测试套文件，如testsuite.yaml，存放目录为./testcase/app，与-m只能同时存在一个')
parser.add_argument('-m', help='用例标记，与pytest -m用法一致，如-m mark1；支持多个标记，如-m "mark1 and mark2"，'
                               '与--testsuite只能同时存在一个', metavar='markers')
parser.add_argument('--dir', help='用例目录或用例文件，填写相对路径，起始目录为./产品目录/testcase/app，多个使用空格分隔，'
                                  '如--dir "xcjc clys/test_1.py"')
parser.add_argument('--reruns', help='失败重跑次数，默认为1次', default=1, type=int)
parser.add_argument('--session', help='会话目录，保存报告的父级目录')
parser.add_argument('--batch', help='是否批量运行，默认为0（否）', default=0, type=int)
parser.add_argument('--reset', help='是否重置app，默认1（是）', default=1, type=int)
parser.add_argument('--reinstall', help='是否重新安装app，默认0（否）', default=0, type=int)
parser.add_argument('--start_appium', help='是否自动开启appium服务，默认为0（否）', default=0, type=int)
parser.add_argument('--imp', help='隐式等待时间，默认1秒', default=1, type=int)
args = parser.parse_args()
print(args)

config_info = ConfigInfo(args.product, args.env)  # 注意是单例实例化
product_path = config_info.product_path
app = config_info.get_app()
report_name = config_info.get_report_name()
# 会话目录，不指定时自动生成
if args.session:
    config_info.session_id = args.session
else:
    config_info.session_id = f'{dir_time}_{randint(10, 99)}'

try:
    # 项目
    if not os.path.exists(product_path):
        raise Exception('找不到该路径：%s' % product_path)

    # 设备
    device_info = DeviceInfo().device_info

    # appium连接手机
    ins = AppInit(args.device, app)
    ins.start(reset=args.reset, reinstall=args.reinstall, start_appium=args.start_appium,
              implicitly_wait=args.imp)

    # pytest命令参数
    report_file = rf'{product_path}/report/{config_info.session_id}/{dir_time}/{report_name}.html'
    pytest_args = [rf'--html={report_file}', '--self-contained-html', f'--reruns={args.reruns}']

    # 使用testsuite.yaml定义的用例运行
    parent_case_dir = rf'{product_path}/testcase/app/'
    if args.testsuite:
        suite_path = f'{parent_case_dir}{args.testsuite}'
        for testcase in get_yaml(suite_path)['testcase']:
            if isinstance(testcase, list):
                testcase = testcase[0]
            pytest_args.append(parent_case_dir + testcase)  # 加入用例参数
    # 指定用例目录或用例文件运行
    elif args.dir:
        dir_list = args.dir.split(' ')
        for d in dir_list:
            each_case_dir = parent_case_dir + d
            pytest_args.append(each_case_dir)
    # 不定义testsuite和dir，使用默认目录运行
    else:
        pytest_args.append(parent_case_dir)
    # 添加用例标记
    if args.m:
        pytest_args.append(f'-m {args.m}')
    # 运行
    print(pytest_args)
    pytest.main(pytest_args)
except:
    traceback.print_exc()
finally:
    if args.batch:
        # 批量运行完成时，完成数量+1，用于batch_run_app.py判断批量运行是否完成
        with shelve.open(config_info.my_db, writeback=True) as file_db:
            file_db['finish_num'] += 1
    else:
        # 单个运行完成后，立即发送报告
        os.system(rf'start python {root_path}/send_report.py {args.product} {config_info.session_id}')
        # 如果是自动开启的appium服务，结束后自动关闭
        if args.start_appium:
            AutoAppium('', '').kill_server()
        pass
    input('\n运行结束，请按回车退出...')
