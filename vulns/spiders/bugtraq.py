# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import logging as log
from vulns.items import BugtraqItem
from datetime import datetime
from vulns.settings import BUGTRAQ_LATEST_LOG


class BugtraqSpider(scrapy.Spider):
    name = 'bugtraq'
    allowed_domains = ['www.securityfocus.com']
    base_url = 'https://www.securityfocus.com'
    start_urls = [
        'https://www.securityfocus.com/cgi-bin/index.cgi?o=0&l=100&c=12&op=display_list&vendor=&version=&title=&CVE=']
    current_latest_bid = None

    def __init__(self, **kwargs):
        """
        初始化部分载入上次扫描的记录，避免每次更新爬取全部数据。
        :param kwargs:
        """
        super(BugtraqSpider, self).__init__(**kwargs)
        self._load_latest_log(BUGTRAQ_LATEST_LOG)

    def _load_latest_log(self, file_path):
        data = ''
        try:
            with open(file_path, 'r') as f:
                data = f.read().strip()
        except Exception as e:
            self.log('load bid latest log file failed: %s' % str(e), level=log.ERROR)
        if not data:
            self.latest_bid = None
            self.latest_date = None
        else:
            date, bid = data.split('<!>')
            self.latest_date = self._str_to_date(date)
            self.latest_bid = bid

    def _store_latest_log(self, data, file_path):
        try:
            with open(file_path, 'w') as f:
                f.write(data)
        except Exception as e:
            self.log('store bid latest log file failed: %s' % str(e), level=log.ERROR)

    def parse(self, response):
        # 爬取本页数据
        urls = response.xpath('//*[@id="article_list"]/div[2]/a/text()').extract()
        for i, detail_url in enumerate(urls):
            detail_url = detail_url.replace('http://', 'https://')  # 判断
            bid = detail_url[34:]
            if i == 0 and not self.current_latest_bid:
                self.current_latest_bid = bid
            if bid == self.latest_bid:
                self._store_latest_log('data<!>' + self.current_latest_bid)
                self.crawler.engine.close_spider(self, 'scan finished by latest bid!')
            yield Request(detail_url, callback=self.paras_item)
        # 解析爬取下一页
        next_page = None
        page_node = response.xpath('//*/span[@class="pages"]')[0]
        if 'Next >' == page_node.xpath('./a/text()')[-1].extract():
            next_page = page_node.xpath('./a/@href')[-1].extract()
        if next_page:
            next_page_url = self.base_url + next_page
            yield Request(next_page_url, callback=self.parse)

    def paras_item(self, response):
        bugtraq_item = BugtraqItem()
        title = response.xpath('//*[@id="vulnerability"]/span/text()').extract()[0]
        bugtraq_item['name'] = title
        for row in response.xpath('//*[@id="vulnerability"]/table/tr'):
            lable = row.xpath('./td[1]/span/text()').extract()
            if not lable:
                continue
            lable = lable[0].strip()
            data = row.xpath('./td[2]/text()').extract()
            if isinstance(data, list):
                data = map(lambda s: s.strip(), data)  # 去掉多余的空格
                data = [_ for _ in data if _]  # 去掉空行
                print data
                data = ','.join(data)  # 合并数据
            elif isinstance(data, str):
                pass
            else:
                self.log('[-] err  '+ data, log.ERROR)
            if lable == 'Bugtraq ID:':
                bugtraq_item['bid'] = int(data)
            elif lable == 'Class:':
                bugtraq_item['vuln_class'] = data
            elif lable == 'CVE:':
                bugtraq_item['cve'] = data
            elif lable == 'Remote:':
                bugtraq_item['is_remote'] = True if data == 'Yes' else False
            elif lable == 'Local:':
                bugtraq_item['is_local'] = True if data == 'Yes' else False
            elif lable == 'Published:':
                bugtraq_item['publish_date'] = self._str_to_date(data)
            elif lable == 'Updated:':
                bugtraq_item['update_date'] = self._str_to_date(data)
            elif lable == 'Credit:':
                bugtraq_item['credit'] = data
            elif lable == 'Vulnerable:':
                bugtraq_item['effection'] = data
            elif lable == 'Not Vulnerable:':
                bugtraq_item['exclude_effection'] = data
            else:
                self.log('found undefined lable: %s' % lable, level=log.INFO)
        yield bugtraq_item

    def _str_to_date(self, str):
        if str:
            try:
                str = datetime.strptime(str, '%b %d %Y %H:%M%p')
            except ValueError as e:
                self.log('date resolve err, origin str: %s' % str, level=log.ERROR)
        else:
            str = None
        return str
