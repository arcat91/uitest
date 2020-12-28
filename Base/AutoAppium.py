from subprocess import Popen, PIPE
import os
from time import sleep
import shelve
from Base.BaseConfig import root_path

# 定义端口范围，目前定义了40个端口，可支持40个设备同时运行
appium_ports = range(4750, 4790)
chromedriver_ports = range(8050, 8090)
system_ports = range(8250, 8290)  # 官方推荐范围8200-8299
mjpeg_server_ports = range(9250, 9290)  # 该端口在uiautomator2时才使用，官方推荐范围9200-9299
# 查询端口使用命令
cmd = "netstat -ano|findstr :%d "


# 存储已预订的端口
class UsedPorts:
    def __init__(self):
        self.key = 'used_ports'
        if not self.read():  # 如果为空，则初始化为列表
            self.record([])

    def record(self, value):
        with shelve.open(f'{root_path}/config/used_ports', writeback=True) as f:
            f[self.key] = value

    def read(self):
        with shelve.open(f'{root_path}/config/used_ports', writeback=True) as f:
            result = f.get(self.key)
        print(f'shelve读取结果为{str(result)}')
        return result


class AutoAppium:
    def __init__(self, deviceSN_or_address, appium_server):
        self.deviceSN_or_address = deviceSN_or_address
        self.appium_server = appium_server
        self.up_ins = UsedPorts()

    # 获取空闲端口
    def get_idle_port(self, ports, desc=''):
        for port in ports:
            # 如果端口已被记录，跳过
            if port in self.up_ins.read():
                continue
            result = Popen(cmd % port, shell=True, stdout=PIPE).stdout.read()
            # 如果端口已被占用，跳过
            if result:
                print('端口使用查询结果')
                print(result)
                continue
            print('%s的当前可用端口是%d' % (desc, port))
            # 写入新数据
            new_record = self.up_ins.read()
            new_record.append(port)
            self.up_ins.record(new_record)
            print(f'当前已使用端口有:{str(self.up_ins.read())}')
            return port
        else:
            raise Exception('已无%s的空闲端口，请检查' % desc)

    # 获取空闲的appium端口
    def get_appium_port(self):
        return self.get_idle_port(appium_ports, 'appium')

    # 获取空闲的chromedriver端口
    def get_chromedriver_port(self):
        return self.get_idle_port(chromedriver_ports, 'chromedriver')

    # 获取空闲的systemPort
    def get_system_port(self):
        return self.get_idle_port(system_ports, 'systemPort')

    # 获取空闲的mjpegServerPort，该端口在uiautomator2时才使用
    def get_mjpeg_server_port(self):
        return self.get_idle_port(mjpeg_server_ports, 'mjpegServerPort')

    # 启动appium服务
    def start_appium(self):
        appium_port = self.get_appium_port()
        chromedriver_port = self.get_chromedriver_port()
        cmd = 'start appium -a %s -p %d --chromedriver-port %d -U "%s" --session-override' \
              % (self.appium_server, appium_port, chromedriver_port, self.deviceSN_or_address)
        if appium_port and chromedriver_port:
            print(cmd)
            os.system(cmd)
            sleep(3)
        return appium_port

    # 关闭appium服务
    def kill_server(self):
        for port in self.up_ins.read():
            result1 = Popen(cmd % port, shell=True, stdout=PIPE).stdout.readlines()
            print(result1)
            if result1:
                line = result1[0].split()
                pid = int(line[-1])
                result2 = Popen('taskkill /f /pid %d' % pid, shell=True, stdout=PIPE, encoding='gbk').stdout.read()
                print(result2)
        # 清空已记录的占用端口
        self.up_ins.record([])


if __name__ == '__main__':
    ins = AutoAppium('127.0.0.1:62001', 'localhost')
    ins.start_appium()
    # print(ins.get_system_port())
