# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlalchemy
from icnnvd.settings import DB_CONFIG
from icnnvd.items import IcnnvdVulnInfo
from scrapy import log


class IcnnvdPipeline(object):
    def open_spider(self, spider):
        self.engine = sqlalchemy.create_engine(
                '{DRIVER}://{USER}:{PASSWD}@{HOST}:{PORT}'
                '/{DBNAME}?charset={CHARSET}'.format(**DB_CONFIG)
                )
        self.SessionClass = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.sesssion = self.SessionClass()
        if DB_CONFIG['TABLENAME'] not in self.engine.table_names():
            log.msg('no table, has created it!', level=log.INFO)
            IcnnvdVulnInfo.metadata.create_all(self.engine)

    def close_spider(self, spider):
        self.sesssion.close()

    def process_item(self, item, spider):
        key_values = dict(item)
        if not self.sesssion.query(IcnnvdVulnInfo).filter_by(cve=key_values['cve']).count():
            self.sesssion.add(IcnnvdVulnInfo(**key_values))
            try:
                self.sesssion.commit()
            except sqlalchemy.InvalidRequestError, e:
                self.sesssion.rollback()
                log.msg('found error' + e.message, level=log.ERROR)
        return item
