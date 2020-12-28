#!/usr/bin/python
# -*- coding: utf-8 -*-
import pymysql
from Base.BaseConfig import ConfigInfo
from Base.BaseLoggers import logger


class BaseDB:
    def __init__(self, db_host, db_port, db_user, db_pwd):
        try:
            self.conn = pymysql.Connect(
                host=db_host,  # 设置MYSQL地址
                port=int(db_port),  # 设置端口号
                user=db_user,  # 设置用户名
                passwd=db_pwd,  # 设置密码
                charset='utf8',  # 设置编码
                use_unicode=True
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            logger.error('数据库连接异常: ', e)

    def set_db(self, db_name):
        """选择数据库"""
        self.conn.select_db(db_name)

    def query(self, sql_string, row=0, col=0):
        logger.info('执行sql：%s' % sql_string)
        self.cursor.execute(sql_string)
        result = self.cursor.fetchall()
        logger.info(result)
        return result[row][col]

    def update(self, sql_string):
        logger.info('执行sql：%s' % sql_string)
        self.cursor.execute(sql_string)
        result = self.cursor.fetchall()
        logger.info(result)
        self.conn.commit()

    def close(self):
        self.conn.close()


class DbConn(BaseDB):
    def __init__(self, product, env, db_type='tenant'):
        config_info = ConfigInfo(product, env)
        db_host, db_port, db_user, db_pwd, db_name = config_info.get_mysql_link()
        BaseDB.__init__(self, db_host, db_port, db_user, db_pwd)
        if isinstance(db_name, dict):
            db_name = db_name[db_type]
        self.set_db(db_name)


if __name__ == '__main__':
    sql = "select * from q_process_acceptv2 limit 1"
    # with DbConn("ydzj", 'test') as p:
    #     print(p.query(sql))
    db = DbConn("ydzj", 'test')
    db.query('select id from q_bidsection limit 1')
