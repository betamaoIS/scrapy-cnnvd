# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VulnsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CnnvdItem(scrapy.Item):
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

class BugtraqItem(scrapy.Item):
    bid = scrapy.Field()
    name = scrapy.Field()
    vuln_class = scrapy.Field()
    cve = scrapy.Field()
    is_remote = scrapy.Field()
    is_local = scrapy.Field()
    publish_date = scrapy.Field()
    update_date = scrapy.Field()
    credit = scrapy.Field()
    effection = scrapy.Field()
    exclude_effection = scrapy.Field()
