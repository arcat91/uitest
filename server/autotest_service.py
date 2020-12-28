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


# 根据参数生成签名(公共组使用)
# 1、将待签名参数按照 ASCII 码顺序从小到大排序（字典序排序）
# 2、按照 URL params 的格式（key1=value1&key2=value2&key3=value3）拼接成一个字符串 beforeSignStr，不需要对字符串进行 URL 转义
# 3、对字符串 beforeSignStr 进行 sha1 加密得到签名 signature
@app.route('/gen_signature', methods=['Post'])
def gen_signature():
    data = request.get_data()
    data = loads(data)
    print(data)
    dict_data = dict(data)
    extract_keys = list(dict_data.keys())
    sort_keys = sorted(extract_keys)
    str_list = []
    for key in sort_keys:
        str_list.append(f'{key}=' + str(dict_data[key]))
    con_str = '&'.join(str_list)
    sha = sha1(con_str.encode('utf-8'))
    encrypts = sha.hexdigest()
    return str(encrypts)


# 将运维平台的信息转发
@app.route('/save_content', methods=['Post'])
def save_mail_content():
    args_content = request.form
    print(args_content)
    requests.post(url='http://10.8.60.114:5001/save_content', data=args_content)
    return '保存成功'


# 将运维平台的信息转发
@app.route('/release_success', methods=['Post'])
def release_trigger():
    args_content = request.form
    print(args_content)
    requests.post(url='http://10.8.60.114:5001/release_success', data=args_content)
    return '保存成功'


if __name__ == '__main__':
    app.run(host='172.18.0.118', port=5003)
