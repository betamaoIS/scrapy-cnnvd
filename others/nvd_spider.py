# coding=utf-8
import re

from lxml import etree
from pprint import pprint
from StringIO import StringIO
import gzip
import requests
import json
import tempfile
import pymongo
from multiprocessing.dummy import Pool
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# 定义handler的输出格式
formatter = logging.Formatter(
    '[%(asctime)s] %(funcName)s [%(levelname)s] %(message)s'
)
ch.setFormatter(formatter)
# 给logger添加handle
logger.addHandler(ch)





def resolve_nvd_cve_items():
    """
    解析当前存在的cve json条目并返回一个字典，格式为：
        {
            "CVE-2009": {
                "data_url": "https://nvd.nist.gov/feeds/json/cve/1.0/nvdcve-1.0-2009.json.gz",
                "modify_time": "2019-08-09T04:47:23-04:00",
                "data_size": "2.36",
                "meta_url": "https://nvd.nist.gov/feeds/json/cve/1.0/nvdcve-1.0-2009.meta"
            }, .....
        }
    :return: dict
    """
    # 首先获取所有可下载的条目
    html = requests.get('https://nvd.nist.gov/vuln/data-feeds').text
    doc = etree.HTML(html)
    table_doc = doc.xpath('//*[@id="page-content"]/div[3]/div/table')[(-1)]  # 获取json table
    tbody_doc = table_doc.xpath('./tbody')[(-1)]
    items = {}
    for tr in tbody_doc:
        if tr.get('class') == 'xml-feed-desc-row':
            name = tr.getchildren()[0].text.strip()
            meta_url = tr.xpath('./td[3]/a/@href')[(-1)].strip()
            gz = tr.getnext()
            data_url = gz.xpath('./td[1]/a/@href')[-1].strip()
            data_size = gz.xpath('./td[2]/text()')[-1].strip()
            items[name] = {'data_url': data_url, 'data_size': data_size, 'meta_url': meta_url}
    # 接着遍历每一个条目获取最新修改时间
    last_modifytime_pat = re.compile('lastModifiedDate:(.+)')
    for name in items:
        url = items[name]['meta_url']
        try:
            logger.debug('open: ' + url)
            resp = requests.get(url)
            items[name]['modify_time'] = last_modifytime_pat.search(resp.text).group(1).strip()
        except Exception as e:
            logger.error(e)
            return {}
    return items


def main():
    # 获取本地版本信息
    RECORD_FILE = 'record.json'
    try:
        record = json.load(open(RECORD_FILE, 'r'))
    except Exception as e:
        logger.info(e)
        record = {}
        try:
            json.dump(record, open(RECORD_FILE, 'w'), indent=4)
        except Exception as e:
            logger.error(e)
            return

    # 建立数据库连接
    mongo_client = pymongo.MongoClient('mongodb://10.251.0.233:27017')
    mongo_db = mongo_client['vulns']['cve']
    # 获取cve词典
    cve_dic = resolve_nvd_cve_items()
    if not cve_dic:
        return
    # 比较需要升级的数据
    try:
        for name in cve_dic:
            if (name in record and record[name]['modify_time'] == cve_dic[name]['modify_time'] and
                    record[name]['has_down'] == True):  # 已经存在
                continue
            data_url = cve_dic[name]['data_url']
            size = cve_dic[name]['data_size']
            logger.info('开始下载数据： {} => {}MB'.format(data_url, size))
            resp = requests.get(data_url, timeout=60 * 20) # 下载数据，连国外速度慢，设置超时20分钟
            logger.info('数据下载完成：' + data_url)
            res = gzip.GzipFile(fileobj=StringIO(resp.content))  # 解压gz数据
            json_data = res.read()
            json_obj = json.loads(json_data)
            for cve in json_obj['CVE_Items']:
                mongo_db.update_one({"CVE_data_meta.ID": cve['cve']['CVE_data_meta']['ID']}, {'$set': cve['cve']},
                                    upsert=True)
            record[name] = cve_dic[name]
            record[name]['has_down'] = True
    except Exception as e:
        logger.error(e)
    finally:
        json.dump(record, open(RECORD_FILE, 'w'), indent=4)


if __name__ == '__main__':
    main()
