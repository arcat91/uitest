import os
from time import sleep
from threading import Thread
import shelve
from Base.BaseConfig import ConfigInfo, root_path, dir_time
from Base.BaseYaml import get_yaml
import argparse
from random import randint
from Base.AutoAppium import AutoAppium
from traceback import print_exc

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('product', help='产品编码，如移动质检为ydzj，请与产品目录名称保持一致')
parser.add_argument('env', help='环境编码，如测试环境为test，请与产品目录的config.yaml的env参数保持一致')
parser.add_argument('--start_appium', help='是否自动开启appium服务，默认为否', default=0, type=int)
parser.add_argument('--reset', help='是否重置app，默认1（是）', default=1, type=int)
parser.add_argument('--reinstall', help='是否重新安装app，默认0（否）', default=0, type=int)
parser.add_argument('--imp', help='隐式等待时间，默认1秒', default=1, type=int)

args_p = parser.parse_args()
print(args_p)
product = args_p.product
env = args_p.env
start_appium = args_p.start_appium
# 获取批量运行配置信息
config_info = ConfigInfo(product, env)
args_file = get_yaml(config_info.product_path + '/config/batch_run_app.yaml')
reruns = int(args_file['reruns'])
run_args = args_file['run_args']
# 会话id
session_id = f'{dir_time}_{randint(10, 99)}'


# 启动方法
def run(device, run_mode, mode_args):
    cmd = rf'start python {root_path}/run_app.py {product} {env} {device} {run_mode} "{mode_args}" --session {session_id} ' \
        rf'--batch 1 --reruns {reruns} --start_appium {start_appium} --reset {args_p.reset} --reinstall {args_p.reinstall} ' \
        rf'--imp {args_p.imp}'
    print(cmd)
    os.system(cmd)


# 监听各线程是否运行完成
def watching_dog(expect_num, timeout, interval):
    expect_num = int(expect_num)
    # 初始化完成标记和完成数量
    with shelve.open(filename=config_info.my_db) as file_db:
        file_db['finish_mark'] = 0
        file_db['finish_num'] = 0
    # 循环判断是否完成
    for i in range(timeout // interval):
        try:
            with shelve.open(filename=config_info.my_db) as file_db:
                print('已完成%d/%d' % (file_db['finish_num'], expect_num))
                if expect_num == file_db['finish_num']:
                    file_db['finish_mark'] = 1
                    return True
                else:
                    sleep(interval)
                    continue
        except:
            print_exc()
            sleep(interval)
    else:
        print('执行超时，退出')


# 监听完成时的操作
def teardown(expect_num, timeout, interval):
    if watching_dog(expect_num, timeout, interval):
        # 发送邮件
        os.system('start python %s/send_report.py %s %s' % (root_path, product, session_id))
        # 如果是自动开启的appium服务，结束后自动关闭
        if start_appium:
            AutoAppium('', '').kill_server()


# 多线程启动
Thread(target=teardown, args=[len(run_args), 7200, 30]).start()
t_list = []
for args in run_args:
    t_list.append(Thread(target=run, args=[i for i in args]))
for j in t_list:
    j.start()
    sleep(30)
