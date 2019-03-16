## 用法
本项目可在**Pthon2.7**下正常运行，其他版本未测试:
```
pip install scrapy  # 安装scrapy
git clone git@github.com:betamaoIS/scrapy-cnnvd.git      # 下载项目
cd scrapy-cnnvd # 切换到目录
scrapy crawl mycnnvd # 运行爬虫
```
![](demo.png)


## 输出
1. scrapy内置支持将数据输出为`JSON`,`SJON lines`,`CSV`,`XML`格式如下，详见官方手册。
```
scrapy crawl mycnnvd -o items.json
scrapy crawl mycnnvd -o items.csv
scrapy crawl mycnnvd -o items.xml
```
2. 本项目添加了对MYSQL的支持，首次运行需要配置：
+ 在`settings.py`里设置MYSQL数据库的连接参数
+ 创建数据表

    CREATE TABLE `cnnvd` (
      `url` varchar(255) DEFAULT NULL,
      `cnnvd` varchar(64) DEFAULT NULL,
      `name` varchar(255) DEFAULT NULL,
      `grade` varchar(32) DEFAULT NULL,
      `vuln_type` varchar(32) DEFAULT NULL,
      `threat_type` varchar(32) DEFAULT NULL,
      `release_time` varchar(16) DEFAULT NULL,
      `update_time` varchar(16) DEFAULT NULL,
      `vuln_desc` varchar(512) DEFAULT NULL,
      `vuln_bulletin` varchar(512) DEFAULT NULL,
      `ref_urls` varchar(512) DEFAULT NULL,
      `source` varchar(255) DEFAULT NULL,
      `vendor` varchar(255) DEFAULT NULL,
      `affected` varchar(255) DEFAULT NULL,
      `patch_url` varchar(255) DEFAULT NULL,
      PRIMARY KEY (`cnnvd`)
    )

## 设置
参见scrapy[官方文档](https://doc.scrapy.org/en/latest/topics/settings.html)

## 暂停与恢复
使用工作目录的方式可以将单个任务进程保存，即当爬虫被终止后，下次重新启动将从上次终止处继续爬取：
```
scrapy crawl mycnnvd -s JOBDIR=crawls/somespider-1
```

## TODO
[] 由于采样不多，xpath应该是有问题的，后续需要完善
