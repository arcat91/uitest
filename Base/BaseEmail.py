# -*- coding: utf-8 -*-
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from Base.BaseLoggers import logger


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_mail(host='', port='', user='', password='', sender_name='', to_addr='', cc_addr='', subject='', content='',
              content_html='', attach_file='', attach_file_name=''):
    logger.info('正在发送报告')
    # 连接邮件服务器
    server = smtplib.SMTP_SSL(host, port)
    server.login(user, password)

    msg = MIMEMultipart()
    if content:
        msg.attach(MIMEText(content, 'plain', 'utf-8'))  # 邮件正文
    if content_html:
        msg.attach(MIMEText(open(content_html, encoding='utf-8').read(), 'html', 'utf-8'))  # 邮件正文，html格式
    msg.add_header('From', _format_addr('%s<%s>' % (sender_name, user)))  # 发送人
    msg.add_header('To', ','.join(to_addr))  # 收件人
    msg.add_header('Cc', ','.join(cc_addr))  # 抄送人
    msg.add_header('Subject', subject)  # 邮件主题
    # msg['Subject'] = Header(subject, 'utf-8').encode()
    if attach_file:
        # att2 = MIMEText(open(attach_file, encoding='utf-8').read(), 'base64', 'utf-8')
        att_f = MIMEApplication(open(attach_file, 'rb').read())
        att_f["Content-Type"] = 'application/octet-stream'
        # att_f["Content-Disposition"] = 'attachment; filename="report.zip"'
        att_f.add_header('Content-Disposition', 'attachment', filename=('gb2312', '', attach_file_name))
        msg.attach(att_f)

    server.sendmail(from_addr=user, to_addrs=to_addr + cc_addr, msg=msg.as_string())
    server.quit()
    logger.info('报告已发送')


if __name__ == '__main__':
    to_addr = "huangyj02@mingyuanyun.com"
    mail_host = "smtp.exmail.qq.com"
    mail_user = "yunliantest@mingyuanyun.com"
    mail_pass = "Ceshizu01"
    port = "465"
    header_msg = "UI自动化"
    html_file = r'D:\git_work\uitest\product\ydzj\report\overview.html'
    zip_file = r'D:\git_work\uitest\test.zip'
    send_mail(host=mail_host, port=port, user=mail_user, password=mail_pass, sender_name='发送人别名', to_addr=to_addr,
              subject=header_msg, content_html=html_file, attach_file=zip_file)
