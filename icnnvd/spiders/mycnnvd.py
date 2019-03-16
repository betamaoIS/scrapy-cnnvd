# -*- coding: utf-8 -*-
import scrapy
import re
import requests
from icnnvd.items import IcnnvdItem


class MycnnvdSpider(scrapy.Spider):
    name = 'mycnnvd'
    allowed_domains = ['www.cnnvd.org.cn']
    index_url = "http://www.cnnvd.org.cn"
    baseURL = "http://www.cnnvd.org.cn/web/vulnerability/querylist.tag?pageno="
    offset = 0
    end = 0
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    delete_space_pattern = re.compile(r'\s')
    start_urls = [baseURL+str(offset)]

    def __init__(self):
        super(scrapy.Spider, self).__init__()
        resp = requests.get(self.baseURL)
        sel = scrapy.selector.Selector(resp)
        js = sel.xpath('/html/body/div[4]/div/div[1]/div/div[3]/a[9]/@onclick')
        obj = re.findall(r'pageno=(\d+)&', js.extract()[0])
        self.end = int(obj[0]) if obj else 0

    def parse(self, response):
        node_list = response.xpath("//div[@class='list_list']/ul/li")
        for node in node_list:
            item = IcnnvdItem()
            item['url'] = self.index_url + node.xpath("./div[1]/a/@href").extract()[0]
            item['cnnvd'] = node.xpath("./div[1]/p/a/text()").extract()[0]
            yield scrapy.Request(item['url'], meta={'item': item}, callback=self.detail_parse)
        if self.offset < self.end:
            self.offset += 1
            url = self.baseURL + str(self.offset)
            yield scrapy.Request(url, callback=self.parse)

    def detail_parse(self, response):
        # 接受上一级的爬去数据
        item = response.meta['item']
        xpaths = {
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
            'patch_url': '//*[@id="pat"]/li/div[1]/a/@href'
        }
        ext_s = self._extract_str_by_xpath
        for key in xpaths:
            if key == 'ref_urls':
                item[key] = ext_s(response, xpaths[key], self.url_pattern, '###')
            else:
                item[key] = ext_s(response, xpaths[key])
        if item['patch_url']:
            item['patch_url'] = self.index_url + item['patch_url']
        yield item

    def _extract_str_by_xpath(self, response, xpath_str, pattern=None, connector=''):
        sel = response.xpath(xpath_str)
        if pattern:
            data_list = sel.re(pattern)
        else:
            data_list = sel.extract()
            data_list = map(lambda x: x.strip(), data_list)
        return connector.join(data_list).replace('\'', r'\'')
