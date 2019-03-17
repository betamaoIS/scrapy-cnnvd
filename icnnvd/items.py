# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
from icnnvd.settings import DB_CONFIG


class IcnnvdVulnInfo(declarative_base()):
    __tablename__ = DB_CONFIG['TABLENAME']
    url = Column(String(255))
    cnnvd = Column(String(127))
    name = Column(String(127))
    cve = Column(String(127), primary_key=True)
    grade = Column(String(31))
    vuln_type = Column(String(31))
    threat_type = Column(String(31))
    release_time = Column(String(31))
    update_time = Column(String(31))
    vuln_desc = Column(String(1023))
    vuln_bulletin = Column(String(1023))
    ref_urls = Column(String(1023))
    source = Column(String(255))
    vendor = Column(String(127))
    affected = Column(String(255))
    patch_url = Column(String(255))


class IcnnvdItem(scrapy.Item):
    url = scrapy.Field()  # 该条目cnnvd页面url
    cnnvd = scrapy.Field()
    name = scrapy.Field()  # 漏洞名称
    cve = scrapy.Field()
    grade = scrapy.Field()  # 危害等级
    vuln_type = scrapy.Field()  # 漏洞类型
    threat_type = scrapy.Field()  # 威胁类型：本地 远程等
    release_time = scrapy.Field()
    update_time = scrapy.Field()
    vuln_desc = scrapy.Field()  # 漏洞描述
    vuln_bulletin = scrapy.Field()  # 漏洞公告，关于最新进展
    ref_urls = scrapy.Field()  # 参考网址
    source = scrapy.Field()  # 漏洞来源
    vendor = scrapy.Field()  # 厂商
    affected = scrapy.Field()  # 受影响的对象
    patch_url = scrapy.Field()  # 补丁的地址 暂时为cnnvd的补丁页，以后视情况解析

    pass
