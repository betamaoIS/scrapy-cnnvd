# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import icnnvd.settings as settings


# 导出到Mysql数据库
class IcnnvdPipeline(object):
    SQL_INSERT = u'''
        INSERT INTO `vulninfo`(`url`, `cnnvd`, `name`,\
        `grade`, `vuln_type`, `threat_type`, `release_time`,\
        `update_time`, `vuln_desc`, `vuln_bulletin`, `ref_urls`,\
        `source`, `vendor`, `affected`, `patch_url`)\
        VALUES('{url}','{cnnvd}','{name}','{grade}','{vuln_type}',\
        '{threat_type}','{release_time}','{update_time}','{vuln_desc}',\
        '{vuln_bulletin}','{ref_urls}','{source}','{vendor}','{affected}','{patch_url}')
    '''

    def __init__(self):
        self.db = pymysql.connect(
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            db=settings.MYSQL_DBNAME,
            port=settings.MYSQL_PORT,
            charset=settings.MYSQL_CHARSET,
            cursorclass=pymysql.cursors.DictCursor)

    def process_item(self, item, spider):
        cursor = self.db.cursor()
        key_values = dict(item)
        sql = self.SQL_INSERT.format(**key_values)
        cursor.execute(sql)  # 就假装这里没有注入漏洞
        self.db.commit()
        return item
