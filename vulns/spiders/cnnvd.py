# -*- coding: utf-8 -*-
import requests
from vulns.items import CnnvdItem
import re
from scrapy import Spider, Request
from datetime import datetime
from vulns.settings import CNNVD_LATEST_LOG
import logging as log


class CnnvdSpider(Spider):
    name = 'cnnvd'
    allowed_domains = ['www.cnnvd.org.cn']
    index_url = 'http://www.cnnvd.org.cn'
    base_url = 'http://www.cnnvd.org.cn/web/vulnerability/querylist.tag?pageno='
    URL_PAT = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    NEXT_PAGE_PAT = re.compile(ur'queryld\(\'([\w/.?&=]+)\'\)">下一页 </a>')
    CNNVD_PAT = re.compile(r'CNNVD-\d+-\d+')
    current_latest_cnnvd = None
    delete_space_pattern = re.compile(r'\s')
    start_urls = ['http://www.cnnvd.org.cn/web/vulnerability/querylist.tag?pageno=']
    XPATH = {
        'name': '//div[@class="detail_xq w770"]/h2/text()',
        'cve': '//ul/li[3]/a[@rel]/text()',
        'grade': '//ul/li[2]/a[@style="color:#4095cc;cursor:pointer;"]/text()',
        'vuln_type': '//ul/li[4]/a[@style]/text()',
        'threat_type': '//ul/li[6]/a[@style]/text()',
        'release_time': '//ul/li[5]/a[@style]/text()',
        'update_time': '//ul/li[7]/a[@style]/text()',
        'source': '//*[@id="1"]/text()',
        'vendor': '/html/body/div[4]/div/div[1]/div[2]/ul/li[8]/text()',
        'vuln_desc': '//div[@class="d_ldjj"]/p/text()',
        'vuln_bulletin': '//div[@class="fl w770"]/div[4]/p/text()',
        'ref_urls': '//div[@class="d_ldjj m_t_20"]/p[@class="ckwz"]/text()',
        'affected': '//*[@id="ent"]/p/text()',
        'patch_url': '//*[@id="pat"]/li/div[1]/a/@href',
        'cnnvd': '/html/body/div[4]/div/div[1]/div[2]/ul/li[1]/span/text()'
    }

    def __init__(self):
        super(Spider, self).__init__()
        self._load_latest_log(CNNVD_LATEST_LOG)

    def _load_latest_log(self, file_path):
        data = ''
        try:
            with open(file_path, 'r') as f:
                data = f.read().strip()
        except Exception as e:
            self.log('load cnnvd latest log file failed: %s' % str(e), level=log.ERROR)
        if not data:
            self.latest_cnnvd = None
            self.latest_date = None
        else:
            date, cnnvd = data.split('<!>')
            self.latest_date = self._str_to_date(date)
            self.latest_cnnvd = cnnvd

    def _store_latest_log(self, data, file_path):
        try:
            with open(file_path, 'w') as f:
                f.write(data)
        except Exception as e:
            self.log('store bid latest log file failed: %s' % str(e), level=log.ERROR)

    def parse(self, response):
        # 处理每个条目
        node_list = response.xpath("//div[@class='list_list']/ul/li")
        for node in node_list:
            try:
                url = self.index_url + node.xpath("./div[1]/a/@href").extract()[0].strip()
            except IndexError:
                continue
            yield Request(url, callback=self.parse_item)
        # 处理下一页
        res = self.NEXT_PAGE_PAT.findall(response.text)
        if res:
            next_page_url = self.index_url + res[0]
            yield Request(next_page_url, callback=self.parse)

    def parse_item(self, response):
        item = CnnvdItem()
        XPATH = self.XPATH
        ext_s = self._extract_str_by_xpath
        for key in XPATH:
            if key == 'ref_urls':
                item[key] = ext_s(response, XPATH[key], self.URL_PAT, '<!>')
            elif key == 'release_time' or key == 'update_time':
                item[key] = self._str_to_date(ext_s(response, XPATH[key]))
            elif key == 'cnnvd':
                item[key] = ext_s(response, XPATH[key], self.CNNVD_PAT)
            else:
                item[key] = ext_s(response, XPATH[key])
        if item['patch_url']:
            item['patch_url'] = self.index_url + item['patch_url']
        #
        if not self.current_latest_cnnvd and item['cnnvd']:
            self.current_latest_cnnvd = item['cnnvd']
        # 当当前的cnnvd号与之前爬取的cnnvd号一样时，证明接下来的都是爬取过的，那么就结束爬虫
        if item['cnnvd'] == self.latest_cnnvd:
            self._store_latest_log('date<!>' + self.current_latest_cnnvd, CNNVD_LATEST_LOG)  # 存储最新的条目
            self.crawler.engine.close_spider(self, '[+] scrapy finished by log ')  # 结束爬虫，多线程问题影响不大
        yield item

    @staticmethod
    def _extract_str_by_xpath(response, xpath_str, pattern=None, sep=','):
        sel = response.xpath(xpath_str)
        ret = ''
        if pattern:
            data_list = sel.re(pattern)
            ret = sep.join(data_list)
        else:
            data_list = sel.extract()
            if isinstance(data_list, list):
                data_list = map(lambda x: x.strip(), data_list)  # 去掉多余的空格
                data_list = [_ for _ in data_list if _]  # 去掉空行
                ret = sep.join(data_list)  # 连接
            elif isinstance(data_list, str):
                data_list.strip()
        return ret

    def _str_to_date(self, str):
        """
        将cnnvd上的date转换为date类型数据
        :param str:
        :return:
        """
        if str:
            try:
                str = datetime.strptime(str, '%Y-%m-%d')
            except ValueError:
                self.log('[-] str_to_date error: ' + str, log.ERROR)
                str = ''
        return str
