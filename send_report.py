from lxml.html import parse
# from lxml.html.soupparser import parse
import re
import sys
from Base.BaseConfig import root_path, ConfigInfo
from Base.BaseEmail import send_mail
from Base.BaseLoggers import logger
from Base.utils import create_dir
from zipfile import ZipFile, ZIP_DEFLATED
import os
import argparse


def catch_all_files(file_dirs, file_list, file_filter=''):
    ori_path = os.getcwd()
    if not isinstance(file_dirs, list):
        file_dirs = [file_dirs]
    for file_dir in file_dirs:
        os.chdir(file_dir)  # 进入指定目录
        path_list = os.listdir('.')
        for i in path_list:
            # cur_dir = os.getcwd()  # 获取当前目录
            # print('当前目录', cur_dir)
            abs_path = os.path.join(file_dir, i)
            if os.path.isdir(abs_path):  # 如果是目录，则进入目录
                catch_all_files(abs_path, file_list, file_filter)  # 递归遍历
            else:  # 如果是文件，拼接当前目录+文件名，添加到列表中
                # print('加入文件', abs_path)
                if file_filter not in abs_path:
                    continue
                file_list.append(abs_path)
    os.chdir(ori_path)
    return file_list


def zip_report(file_dirs, save_name):
    logger.info('正在压缩文件')
    logger.info(str(file_dirs))
    file_list = []
    file_list = catch_all_files(file_dirs, file_list)
    for i in file_list: print(i)
    z_file = ZipFile(save_name, 'w', compression=ZIP_DEFLATED)
    for i in file_list:
        # print(i)
        base_name = i.split('report')[1]
        z_file.write(i, arcname=base_name)
    z_file.close()
    logger.info('压缩完成')


# 创建概览报告
class CreateOverview:
    template_file = root_path + '/config/report_template.html'
    re_num = re.compile(r'\d+')
    pass_rate = 0

    def get_num(self, text):
        return int(re.findall(self.re_num, text)[0])

    def replace_num(self, text, num):
        return re.sub(self.re_num, num, text)

    def create_overview(self, title, h_files, save_file):
        logger.info('正在生成概览报告')
        # 提取结果文件的运行结果
        pass_num = skip_num = fail_num = error_num = xfailed_num = xpassed_num = rerun_num = total_num = 0
        case_result_elems = []
        if not isinstance(h_files, list):
            h_files = [h_files]
        for f in h_files:
            file2 = open(f, encoding="utf-8")
            r_file = parse(file2)
            # 提取结果文件的汇总数量
            pass_num += self.get_num(r_file.find('//*[@class="passed"]').text)
            skip_num += self.get_num(r_file.find('//*[@class="skipped"]').text)
            fail_num += self.get_num(r_file.find('//*[@class="failed"]').text)
            error_num += self.get_num(r_file.find('//*[@class="error"]').text)
            xfailed_num += self.get_num(r_file.find('//*[@class="xfailed"]').text)
            xpassed_num += self.get_num(r_file.find('//*[@class="xpassed"]').text)
            try:
                rerun_num += self.get_num(r_file.find('//*[@class="rerun"]').text)
            except:
                pass
            # 结果文件表格
            r_table_elem = r_file.find('//*[@id="results-table"]')
            # 遍历结果文件的所有用例结果，并加入到模板文件的表格中
            case_result_elems += r_table_elem.xpath('./tbody/tr[1]')
        # 统计通过率
        total_num = pass_num + skip_num + fail_num + error_num + xfailed_num + xpassed_num
        self.pass_rate = '{:.1%}'.format(pass_num / total_num)

        file1 = open(self.template_file, encoding="utf-8")
        t_file = parse(file1)

        # 将汇总数量填充到模板文件
        t_file.find('//*[@class="passed"]').text = self.replace_num(t_file.find('//*[@class="passed"]').text,
                                                                    str(pass_num))
        t_file.find('//*[@class="skipped"]').text = self.replace_num(t_file.find('//*[@class="skipped"]').text,
                                                                     str(skip_num))
        t_file.find('//*[@class="failed"]').text = self.replace_num(t_file.find('//*[@class="failed"]').text,
                                                                    str(fail_num))
        t_file.find('//*[@class="error"]').text = self.replace_num(t_file.find('//*[@class="error"]').text,
                                                                   str(error_num))
        t_file.find('//*[@class="xfailed"]').text = self.replace_num(t_file.find('//*[@class="xfailed"]').text,
                                                                     str(xfailed_num))
        t_file.find('//*[@class="xpassed"]').text = self.replace_num(t_file.find('//*[@class="xpassed"]').text,
                                                                     str(xpassed_num))
        try:
            t_file.find('//*[@class="rerun"]').text = self.replace_num(t_file.find('//*[@class="rerun"]').text,
                                                                       str(rerun_num))
        except:
            pass

        # 将用例结果填充到模板文件
        t_table_elem = t_file.find('//*[@id="results-table"]')
        for case_result in case_result_elems:
            t_table_elem.append(case_result)
        # 修改标题
        t_file.find('//h1').text = title
        # 文件写入
        t_file.write(save_file)
        print('已生成概览报告')


if __name__ == '__main__':
    try:
        # 找到对应产品刚跑完的报告
        parser = argparse.ArgumentParser()
        parser.add_argument('product', help='产品编码，如移动质检为ydzj，请与产品目录名称保持一致')
        parser.add_argument('parent_dir', help='报告父级目录名，填写相对路径，起始路径为./产品目录/report')
        args = parser.parse_args()
        product, parent_dir = args.product, args.parent_dir
        config_info = ConfigInfo(product=product)
        product_path = config_info.product_path
        session_report_dir = product_path + '/report/' + parent_dir
        f_list = []
        html_files = catch_all_files(session_report_dir, f_list, 'html')

        temp_dir = create_dir(product_path + '/report/temp/')
        temp_dir = create_dir(temp_dir + parent_dir)
        # 通过报告生成概览报告
        overview_file = temp_dir + '/overview.html'
        overview_ins = CreateOverview()
        overview_ins.create_overview(config_info.get_report_name(), html_files, overview_file)
        # 计算
        pass_rate = overview_ins.pass_rate

        # 生成报告压缩文件
        attach_file_name = '详细报告附件.zip'
        report_zip = temp_dir + attach_file_name
        zip_report(session_report_dir, report_zip)

        # 发送邮件
        email_info = config_info.get_email_info()
        send_mail(host=email_info['host'], port=email_info['port'], user=email_info['user'],
                  password=email_info['password'],
                  sender_name='UI自动化测试', to_addr=email_info['to_addr'], cc_addr=email_info['cc_addr'],
                  subject=email_info['subject'] + ',通过率:%s' % pass_rate,
                  content_html=overview_file, attach_file=report_zip, attach_file_name=attach_file_name)
    except Exception as e:
        print(e)
    input('\n运行结束，请按回车退出...')
