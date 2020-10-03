# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import re
import time
import os
import json
import platform
from urllib import parse
from scrapy import signals
from scrapy.http import HtmlResponse
from datetime import datetime
from HearthStoneSpider.settings import SQL_FULL_DATETIME, CHANGE_LANGUAGE
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from HearthStoneSpider.tools.crawl_xici_ip import GetIP


class HearthstonespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class HearthstonespiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class JSPageMiddleware(object):
    def __init__(self, crawler):
        super(JSPageMiddleware, self).__init__()
        path = os.path.join(crawler.settings.get('TOOLS_DIR', ''), "user_agent_0.1.11.json")
        self.ua = UserAgent(path=path)
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')
        self.set_cookie_flag = True
        self.cookie_path = os.path.join(crawler.settings.get('COOKIES_DIR', ''), "cookies.json")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if spider.name == 'HSArenaCards' and spider.local_update:
            BASE_DIR = os.path.dirname(os.path.realpath(__file__))
            file = 'arena_file.html'
            file_name = os.path.join(BASE_DIR, 'tools',  file)
            with open(file_name, 'r', encoding='UTF-8') as f:
                page_source = f.read()
            return HtmlResponse(
                url='127.0.0.1',
                body=page_source,
                encoding='utf-8',
                request=request
            )
        # 随机更换user-agent
        def get_ua():
            return getattr(self.ua, self.ua_type)
        request.headers.setdefault('User-Agent', get_ua())
        # request.headers.setdefault('referer', 'https://hsreplay.net/')
        print('get user-agent', request.headers.get('User-Agent'))
        if spider.name == 'HearthStone':
            return None
        if spider.name=='BestDeck' and 'http://47.98.187.217' in request.url:
            return None
        # script = '''
        # Object.defineProperty(navigator, 'webdriver', {
        #     get: () => undefined
        # })
        # '''
        # spider.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
        # 写入会员登录的cookie
        if self.set_cookie_flag and (hasattr(spider, 'addCookieFlag') and spider.addCookieFlag):
            spider.browser.delete_all_cookies()
            spider.browser.get(request.url)
            time.sleep(15)
            print('原始cookies:', spider.browser.get_cookies())
            with open(self.cookie_path, 'r') as f:
                listCookies = json.loads(f.read())
            for cookie in listCookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                spider.browser.add_cookie(cookie)
            time.sleep(15)
            print('新的cookies:', spider.browser.get_cookies())
            self.set_cookie_flag = False
            # if hasattr(spider, 'rankRange') and spider.rankRange:
            #     url = parse.urljoin(request.url, '#rankRange={}'.format(spider.rankRange))
            #     spider.browser.get(url)
            # else:
            #     spider.browser.get(request.url)
            spider.browser.refresh()
            # spider.browser.get(request.url)
            # if request.url == 'https://hsreplay.net/meta/#tab=archetypes':
            #     time.sleep(30)
            # else:
            #     time.sleep(15)
            time.sleep(15)
            pass
        else:
            spider.browser.get(request.url)
            if spider.name == 'HSBattlegrounds' or spider.name == 'HSTrending':
                time.sleep(25)
            elif spider.name == 'HSReport':
                time.sleep(15)
        # print('bbbbb')
        # hCaptcha = spider.browser.find_elements_by_css_selector('#hcaptcha_widget')
        # print('aaaaa', len(hCaptcha))
        # print(spider.browser.page_source)
        # if len(hCaptcha) > 0:
        #     hCaptcha[0].click()
        #     time.sleep(5)

        if spider.name == 'HSWinRate' and 'https://hsreplay.net/archetypes/' in request.url:
            try:
                WebDriverWait(spider.browser, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.deck-box .stats-table table tr td'))
                )
            except Exception as e:
                print('JSPageMiddleware异常1', spider.name, request.url)
                time.sleep(5)
        elif spider.name == 'HSArchetype' and 'https://hsreplay.net/archetypes/' in request.url:
            try:
                WebDriverWait(spider.browser, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.winrate-box .box-chart'))
                )
            except Exception as e:
                print('JSPageMiddleware异常2',e)
                time.sleep(5)
        elif (spider.name == 'HSWildDecks' or spider.name == 'HSDecks' or spider.name == 'BestDeck') \
             and re.match('https://hsreplay.net/decks/.*/', request.url):
            try:
                WebDriverWait(spider.browser, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'table.table-striped tbody tr td.winrate-cell'))
                )
                WebDriverWait(spider.browser, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '#overview .card-list-wrapper .card-list'))
                )
            except Exception as e:
                print('JSPageMiddleware异常3', spider.name, request.url)
                time.sleep(5)
        elif (spider.name == 'HSArchetype'):
            try:
                WebDriverWait(spider.browser, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.tab-list'))
                )
            except Exception as e:
                print('JSPageMiddleware异常4', spider.name, request.url)
                time.sleep(5)
        elif spider.name == 'HSBattlegrounds' and 'https://hsreplay.net/battlegrounds/heroes/' in request.url:
            try:
                WebDriverWait(spider.browser, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.ReactVirtualized__Grid__innerScrollContainer'))
                )
            except Exception as e:
                print('JSPageMiddleware异常4', spider.name, request.url)
                time.sleep(5)
        else:
            time.sleep(5)
        time.sleep(5)
        now = datetime.now().strftime(SQL_FULL_DATETIME)
        print('{0}访问:{1}'.format(now, request.url))
        return HtmlResponse(
            url=spider.browser.current_url,
            body=spider.browser.page_source,
            encoding='utf-8',
            request=request
        )

class RandomProxyMiddleware(object):
    def process_request(self, request, spider):
        if spider.name == 'HSWildDecks' or spider.name == 'HSDecks' or spider.name =='HSRanking' or spider.name == 'HSWinRate':
            get_ip = GetIP()
            request.meta['proxy'] = get_ip.get_random_ip()