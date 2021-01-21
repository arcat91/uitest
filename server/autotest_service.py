from flask import Flask, request
import os
import re
from urllib.parse import unquote
from threading import Thread
from hashlib import sha1
from json import loads
import requests

app = Flask(__name__)
cur_dir = os.path.dirname(__file__).split('server')[0]


@app.route('/')
def test():
    return '连接正常'


def handle_args(result):
    if 'cmd' not in result:
        raise Exception('请传入cmd参数')
    else:
        return result['cmd']


# 执行UI自动化命令
@app.route('/ui_test/run', methods=['Post'])
def run_test():
    result = request.form
    try:
        cmd = handle_args(result)
    except Exception as e:
        return str(e)
    print(cmd)
    cmd = unquote(cmd)
    print(cmd)
    valid_re_list = [r'run_.*\.py', r'batch_run_.*\.py']
    for valid_re in valid_re_list:
        if re.findall(valid_re, cmd):
            cmd = re.sub('python ', f'python {cur_dir}', cmd)  # 执行命令加入路径
            print(cmd)
            Thread(target=lambda: os.system('start ' + cmd)).start()
            return '命令已下发'
    else:
        return '不支持该命令，请重新输入(当前仅支持%s)' % str(valid_re_list)


if __name__ == '__main__':
    app.run(host='172.18.0.118', port=5003)
