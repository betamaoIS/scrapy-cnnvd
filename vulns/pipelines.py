# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from vulns.items import BugtraqItem, CnnvdItem
import sqlalchemy
from vulns.settings import MYSQL_CONF, CNNVD_TABLE, BUGTRAQ_TABLE
from vulns.orms import CnnvdVuln, BugtraqVuln
# from scrapy import log
from vulns.items import BugtraqItem, CnnvdItem
import logging

logger = logging.getLogger(__name__)
MAX_CON_DUP_NUM = 48  # 最大连续重复的次数


class VulnsPipeline(object):
    def open_spider(self, spider):
        self.engine = sqlalchemy.create_engine(
            '{DRIVER}://{USER}:{PASSWD}@{HOST}:{PORT}'
            '/{DBNAME}?charset={CHARSET}'.format(**MYSQL_CONF)
        )
        self.SessionClass = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.sesssion = self.SessionClass()
        if CNNVD_TABLE not in self.engine.table_names():
            logger.info('[+] %s table not exist, create it!' % BUGTRAQ_TABLE)
            CnnvdVuln.metadata.create_all(self.engine)
        if BUGTRAQ_TABLE not in self.engine.table_names():
            logger.info('[+] %s table not exist, create it!' % BUGTRAQ_TABLE)
            BugtraqVuln.metadata.create_all(self.engine)

    def __init__(self):
        self.bid_con_dup_num = 0  # bid连续重复的次数
        self.cnnvd_con_dup_num = 0  # cnnvd连续重复的次数

    def close_spider(self, spider):
        self.sesssion.close()

    def process_item(self, item, spider):
        key_values = dict(item)
        if isinstance(item, BugtraqItem):
            if self.sesssion.query(BugtraqVuln).filter_by(bid=key_values['bid']).count() == 0:
                self.sesssion.add(BugtraqVuln(**key_values))
                self.bid_con_dup_num = 0
                try:
                    self.sesssion.commit()
                except sqlalchemy.InvalidRequestError, e:
                    self.sesssion.rollback()
                    logger.error('[-] found error' + e.message)
            else:
                self.bid_con_dup_num += 1
                if self.bid_con_dup_num == MAX_CON_DUP_NUM:
                    spider.crawler.engine.close_spider(spider, '[*] MAX DUP NUM FOUND!')
        elif isinstance(item, CnnvdItem):
            if self.sesssion.query(CnnvdVuln).filter_by(cnnvd=key_values['cnnvd']).count() == 0:
                self.sesssion.add(CnnvdVuln(**key_values))
                self.cnnvd_con_dup_num = 0
                try:
                    self.sesssion.commit()
                except sqlalchemy.InvalidRequestError, e:
                    self.sesssion.rollback()
                    logger.error('[-] found error' + e.message)
            else:
                self.cnnvd_con_dup_num += 1
                logger.info(item['cnnvd'])
                if self.cnnvd_con_dup_num == MAX_CON_DUP_NUM:
                    spider.crawler.engine.close_spider(spider, '[*] MAX DUP NUM FOUND!')
        return item
