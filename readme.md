## 说明
本项目采用scrapy框架采集cnnvd网站漏洞，数据可以选择存储在json文件中或者MySQL数据库中。

## 用法
安装scrapy:
```
pip install scrapy  # 安装scrapy
git clone git@github.com:betamaoIS/scrapy-cnnvd.git      # 下载项目:
cd scrapy-cnnvd
scrapy crawl mycnnvd
```

## 设置
### 数据存储
默认使用json和MySQL存储：
json：数据被保存在当前目录 icnvvd_position.json
MySQL：需要先在settings.py里设置MySQL的账号和密码，第一次运行需要先创建表
### 其他设置
参见scrapy[官方文档](https://doc.scrapy.org/en/latest/topics/settings.html)

## 暂停与恢复
使用工作目录的方式可以将单个任务进程保存，即当爬虫被终止后，下次重新启动将从上次终止处继续爬取：
```
scrapy crawl mycnnvd -s JOBDIR=crawls/somespider-1
```