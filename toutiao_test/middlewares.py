# -*- coding: utf-8 -*-


import asyncio
import re
from scrapy.http import HtmlResponse
import logging
import time
import hashlib
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)
class NewsHotDownloaderMiddleware(object):
    def __init__(self):
        self.file = open('./news_id.txt','a+')

    def process_request(self, request, spider):
        # 如果‘pyppeteer_enable’为True，执行该process_request方法，否则返回None，执行下一个process_request方法
        if request.meta.get('pyppeteer_enable'):
            asyncio.get_event_loop().run_until_complete(self.main(request,spider))

    async def main(self,request,spider):
        # Browser对象的newPage方法，相当于浏览器中新建了一个选项卡，创建了一个page对象
        page = await spider.browser.newPage()

        # 设置ua
        await page.setUserAgent(
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36')

        await page.goto(request.url)
        # 使用js 将window.navigator.webdriver设置为false
        await page.evaluate(
            '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')

        # 从response中提取出新闻的id值
        a_list = await page.xpath('.//li[@class="article-item"]/a')
        for a in a_list:
            news_link = await (await a.getProperty('href')).jsonValue()
            news_link_id = re.search(r'group/(\d+)/', news_link).group(1)
            self.file.write(news_link_id)
            self.file.write('\n')

        # range（）括号中的数字为下拉几次滚动条
        for p in range(1):
            await asyncio.sleep(4)
            # 将滚动条拉倒最底部
            await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
            # 从response中提取出新闻的id值
            a_list = await page.xpath('.//li[@class="article-item"]/a')
            for a in a_list:
                news_link = await (await a.getProperty('href')).jsonValue()
                news_link_id = re.search(r'group/(\d+)/', news_link).group(1)
                self.file.write(news_link_id)
                self.file.write('\n')
        # 获取页面的源码
        response_html = await page.content()
        # 返回HtmlResponse对象
        return HtmlResponse(url=request.url, request=request, body=response_html, encoding='utf8')



class ProxyDownloaderMiddlerware(object):
    '''使用讯代理的动态转发，随机获取代理'''
    def __init__(self, secret, orderno):
        self.secret = secret
        self.orderno = orderno

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            secret = crawler.settings.get('SECRET'),
            orderno = crawler.settings.get('ORDERNO')
        )

    def process_request(self, request, spider):
        timestamp = str(int(time.time()))
        string = "orderno=" + self.orderno + "," + "secret=" + self.secret + "," + "timestamp=" + timestamp
        string = string.encode()
        md5_string = hashlib.md5(string).hexdigest()
        sign = md5_string.upper()
        auth = "sign=" + sign + "&" + "orderno=" + self.orderno + "&" + "timestamp=" + timestamp

        request.meta['proxy'] = 'http://forward.xdaili.cn:80'
        request.headers["Proxy-Authorization"] = auth
        logger.debug('正在使用动态转发')

class RandomUserAgentDownloaderMiddleware(object):
    """使用fake_useragent库，随机获取UserAgent"""
    def process_request(self, spider, request):
        agent = UserAgent()
        user_agent = agent.chrome
        request.headers['User-Agent']=user_agent
        logger.debug('User-Agent:{}'.format(user_agent))

