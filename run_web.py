#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytest
import os
from Base.BaseYaml import get_yaml
from Base.BaseConfig import dir_time, ConfigInfo, root_path
from Base.BaseDriver import WebInit
import argparse
import traceback
from random import randint

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('product', help='产品编码，如移动质检为ydzj，请与产品目录名称保持一致')
parser.add_argument('env', help='环境编码，如测试环境为test，请与产品目录的config.yaml的env参数保持一致')
parser.add_argument('--browser', help='浏览器类型，默认为chrome', default='chrome')
parser.add_argument('--testsuite', help='测试套文件，如testsuite.yaml，存放目录为./testcase/web，与-m只能同时存在一个')
parser.add_argument('-m', help='用例标记，与pytest -m用法一致，如-m mark1；支持多个标记，如-m "mark1 and mark2"，'
                               '与--testsuite只能同时存在一个', metavar='markers')
parser.add_argument('--dir', help='用例目录或用例文件，填写相对路径，起始目录为./产品目录/testcase/web，多个使用空格分隔，'
                                  '如--dir "xcjc clys/test_1.py"')
parser.add_argument('--reruns', help='失败重跑次数，默认为1', default=1, type=int)
parser.add_argument('--session', help='会话目录，保存报告的父级目录')
parser.add_argument('--headless', help='无头模式运行，暂时只支持chrome，默认为0（关闭）', default=0, type=int)
parser.add_argument('--window_size', help='指定浏览器分辨率，默认为"1920,1080"', default="1920,1080")
parser.add_argument('--max_window', help='窗口最大化，默认为1（开启）', default=1, type=int)
parser.add_argument('--imp', help='隐式等待时间，默认1秒', default=1, type=int)
args = parser.parse_args()
print(args)

config_info = ConfigInfo(args.product, args.env)
product_path = config_info.product_path
init_url = config_info.get_init_url()
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

    # 启动浏览器
    ins = WebInit(browser_name=args.browser, init_url=init_url)
    ins.start(headless=args.headless, window_size=args.window_size, maximize_window=args.max_window,
              implicitly_wait=args.imp)

    # pytest命令参数
    report_file = rf'{product_path}/report/{config_info.session_id}/{dir_time}/{report_name}.html'
    pytest_args = [rf'--html={report_file}', '--self-contained-html', f'--reruns={args.reruns}']

    # 使用testsuite.yaml定义的用例运行
    parent_case_dir = rf'{product_path}/testcase/web/'
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
    # 单个运行完成后，立即发送报告
    os.system(rf'start python {root_path}/send_report.py {args.product} {config_info.session_id}')
    input('\n运行结束，请按回车退出...')
