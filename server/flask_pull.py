#!/usr/bin/python2
# encoding:utf-8
from flask import Flask, request
import subprocess
import os
import argparse
import requests
import yaml
from json import loads, dumps
import threading

app = Flask(__name__)

project_path = os.path.dirname(__file__).split('server')[0]

# 解析参数
parser = argparse.ArgumentParser()
parser.add_argument('host')
parser.add_argument('port', type=int)
parser.add_argument('--trigger', default=0, type=int,
                    help='是否同步触发其它客户端，默认0(否)，待触发的客户端在本目录的client_info.txt配置')
args = parser.parse_args()


def get_new_code():
    # 进入到代码目录，拉取最新代码
    subprocess.call("cd %s && git checkout master" % project_path, shell=True)  # 切换master分支
    subprocess.call("cd %s && git checkout ." % project_path, shell=True)  # 撤销变更
    subprocess.call("cd %s && git fetch --all" % project_path, shell=True)  # 拉取代码
    subprocess.call("cd %s && git reset --hard origin/master" % project_path, shell=True)  # 强制回退
    subprocess.call("cd %s && git pull" % project_path, shell=True)  # 更新


def trigger_other_client(data):
    """同步触发其它客户端"""
    f = open(f'{project_path}/server/client_info.yaml', encoding='utf-8')
    y = yaml.load(f, yaml.FullLoader)
    project = data['repository']['name']
    for client in y['clients']:
        if project == 'ceshi' and 'api_test' in client:  # 当推送与待触发客户端同为接口自动化工程时触发
            requests.post(f'http://{client}', data=dumps(data))
        elif project == 'uitest' and 'ui_test' in client:  # 当推送与待触发客户端同为UI自动化工程时触发
            requests.get(f'http://{client}', data=dumps(data))
        else:
            pass


@app.route('/webhook/ui_test', methods=['GET', 'POST'])
def webhook():
    threading.Thread(target=get_new_code).start()  # 另起线程触发，无需等待结果
    # 同步触发其它客户端
    if args.trigger:
        json_data = loads(request.get_data())
        threading.Thread(target=trigger_other_client, args=[json_data])  # 另起线程触发，无需等待结果
    return 'success'


if __name__ == '__main__':
    app.run(host=args.host, port=args.port)
