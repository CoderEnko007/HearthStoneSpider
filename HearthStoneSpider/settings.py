# -*- coding: utf-8 -*-

# Scrapy settings for HearthStoneSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import os

BOT_NAME = 'HearthStoneSpider'

SPIDER_MODULES = ['HearthStoneSpider.spiders']
NEWSPIDER_MODULE = 'HearthStoneSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'HearthStoneSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'HearthStoneSpider.middlewares.HearthstonespiderSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'HearthStoneSpider.middlewares.HearthstonespiderDownloaderMiddleware': 543,
   'HearthStoneSpider.middlewares.RandomProxyMiddleware': 540,
   'HearthStoneSpider.middlewares.JSPageMiddleware': 543,
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'HearthStoneSpider.pipelines.CardImagesPipeline': 1,
   'HearthStoneSpider.pipelines.MysqlTwistedPipeline': 2,
   # 'HearthStoneSpider.pipelines.JsonExporterPipeline': 1,
}
IMAGES_URLS_FIELD = 'img' # 配置下载图片的地址
project_dir = os.path.abspath(os.path.dirname(__file__))
IMAGES_STORE = os.path.join(project_dir, "images") # 配置图片存储的位置
ARENA_FILES = os.path.join(project_dir, "arenaFiles")
TOOLS_DIR = os.path.join(project_dir, "tools")
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
# MYSQL_HOST = '127.0.0.1'
MYSQL_HOST = '47.98.187.217'
MYSQL_DBNAME = 'hearthstonestation'
MYSQL_USER = 'root'
MYSQL_PWD = '666666'
# MYSQL_PWD = ''

SQL_DATETIME_FORMAT = "%Y-%m-%d"
SQL_FULL_DATETIME = "%Y-%m-%d %H:%M:%S"

COMMANDS_MODULE = 'HearthStoneSpider.commands'

RANDOM_UA_TYPE = 'random'