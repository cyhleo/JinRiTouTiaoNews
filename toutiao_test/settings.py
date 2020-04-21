# -*- coding: utf-8 -*-


BOT_NAME = 'toutiao_test'

SPIDER_MODULES = ['toutiao_test.spiders']
NEWSPIDER_MODULE = 'toutiao_test.spiders'


# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# 设置并发数
CONCURRENT_REQUESTS = ''
CONCURRENT_REQUESTS_PER_DOMAIN = ''
CONCURRENT_REQUESTS_PER_IP = ''

# 禁用cookies
COOKIES_ENABLED = False

# 不使用telnet 控制台
TELNETCONSOLE_ENABLED = False

# 设置请求头
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en',
    'accept-encoding':'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'upgrade-insecure-requests':1,
    'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
}


# 设置下载器中间件
DOWNLOADER_MIDDLEWARES = {
   'toutiao_test.middlewares.NewsHotDownloaderMiddleware': 543,
   'toutiao_test.middlewares.RandomUserAgentDownloaderMiddleware': 600,
   'toutiao_test.middlewares.ProxyDownloaderMiddlerware': 610,
}


# 扩展设置
EXTENSIONS = {
    'toutiao_test.latencies.Latencies': 500,
}


# 设置设置吞吐量和延迟的时间间隔
LATENCIES_INTERVAL = 5


# 开启日志
LOG_ENABLED = True
LOG_ENCODING = 'utf-8'

#logger输出格式设置
LOG_FORMATTER = 'scrapy.logformatter.LogFormatter'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# 如果为True，则进程的所有标准输出（和错误）将重定向到日志。
LOG_STDOUT = False

# 显示的日志最低级别
LOG_LEVEL = 'INFO'

import datetime
t = datetime.datetime.now()
log_file_path = './log_{}_{}_{}_{}.log'.format(t.month,t.day,t.hour,t.minute)
# log磁盘保存地址
LOG_FILE = log_file_path

# 最小的下载延迟时间
DOWNLOAD_DELAY = 0.5

# 开启自动限速设置
AUTOTHROTTLE_ENABLED = True

# The initial download delay
AUTOTHROTTLE_START_DELAY = 5

# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60

# 发送到每一个服务器的并发请求数量
AUTOTHROTTLE_TARGET_CONCURRENCY = ''


# 是否开启调试模式，将显示收到的每个响应的统计信息，
# 以便观察到延迟发送请求的时间如何一步步被调整
AUTOTHROTTLE_DEBUG = False


# 设置 item pipelines
ITEM_PIPELINES = {
   'toutiao_test.pipelines.TimePipeline': 300,
   'toutiao_test.pipelines.MongoDBPipeline': 310,
}

# 持久化到mongodb数据库的设置
MONGO_URI = ''
MONGO_DB = ''

# 讯代理动态转发设置
SECRET = ''
ORDERNO = ''