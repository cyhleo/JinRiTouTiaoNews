# -*- coding: utf-8 -*-
import scrapy
import json
from toutiao_test.items import ToutiaoCommentItem
from toutiao_test.items import ToutiaoItem
from pyppeteer import launch
import asyncio
from scrapy import signals


class ToutiaotestSpider(scrapy.Spider):
    name = 'TouTiaoTest'
    allowed_domains = ['toutiao.com']
    # 今日头条网站首页
    start_url = 'https://www.toutiao.com/'
    # 具体每条新闻的详情页
    news_url = 'https://www.toutiao.com/a{}/'
    # 每条新闻的热门评论数据接口
    comment_url = 'https://www.toutiao.com/article/v2/tab_comments/?aid=24&app_name=toutiao-web&group_id={}&item_id={}&offset={}&count=5'

    def __init__(self,crawler, *args, **kwargs):
        super(ToutiaotestSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        asyncio.get_event_loop().run_until_complete(self.create_browser())
        self.crawler.signals.connect(self._spider_closed, signals.spider_closed)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    async def create_browser(self):
        # launch方法新建一个Browser 对象，然后将其赋值给browser
        self.browser = await launch({'headless': True,
                                'args': [
                                    '--disable-extensions',
                                    '--hide-scrollbars',
                                    '--disable-bundled-ppapi-flash',
                                    '--mute-audio',
                                    '--no-sandbox',
                                    '--disable-setuid-sandbox',
                                    '--disable-gpu',
                                    '--disable-infobars'
                                ],
                                })

    def start_requests(self):
        # Request.meta中pyppeteer_enable值为True，表示该请求对象使用下载器中间件NewsHotDownloaderMiddleware
        yield scrapy.Request(self.start_url,callback=self.parse,meta={'pyppeteer_enable':True})

    def parse(self, response):
        """获取每条新闻的id值，yield包含新闻详情url，以及热门评论数据接口url的请求对象"""
        # './news_id.txt'文件记录每条新闻的id值
        with open('./news_id.txt','r') as f:
            news_id_str = f.read().strip()
        if len(news_id_str):
            news_id_list = news_id_str.split('\n')
            self.logger.debug(len(news_id_list))
            for news_id in news_id_list:
                if news_id:
                    # 根据id值，可拼接每条新闻的详情页url
                    yield scrapy.Request(self.news_url.format(news_id),callback=self.parse_content,meta={'id':news_id})
                    # 根据id值，可拼接每条新闻的热门评论的数据接口url
                    yield scrapy.Request(self.comment_url.format(news_id, news_id, 0), callback=self.parse_comment,
                                         meta={'offset': 0, 'id': news_id}, dont_filter=True)

    def parse_content(self,response):
        """解析新闻的详情页，yield ToutiaoItem实例"""
        item = ToutiaoItem()

        # 新闻id
        id = response.meta.get('id')
        item['news_id'] = id

        # 新闻内容
        content_news = response.xpath('.').re_first(r'content: (.*?)\.slice\(6')
        content_str = self.shift_content_format(content_news)
        item['news_content'] = content_str

        # 新闻标题
        title = response.xpath('.').re_first(r'title: (.*?)\.slice\(6')
        item['title'] = title

        # 新闻来源
        source = response.xpath('.').re_first(r'authInfo: (.*?),')
        try:
            len_news_time = len(source)
        except:
            source = response.xpath('.').re_first(r'source: (.*?),')
        item['source'] = source

        # 新闻发布时间
        news_time = response.xpath('.').re_first(r'publishTime: (.*?),')
        try:
            len_news_time = len(news_time)
        except:
            news_time = response.xpath('.').re_first(r'time: (.*)')
        item['time'] = news_time

        # 新闻评论数
        comments_count = response.xpath('.').re_first(r'comments_count: (.*?),')
        item['comment_num'] = comments_count

        yield item

    def parse_comment(self, response):
        """解析新闻的热门评论，yield ToutiaoCommentItem实例，并yield包含下一页评论url的request对象"""
        json_data = json.loads(response.text)
        comment_list = json_data['data']

        if json_data['message'] == 'success' and len(comment_list):
            offset = response.meta.get('offset')
            offset += 5
            id = response.meta.get('id')

            for com in comment_list:
                item = ToutiaoCommentItem()
                item['news_id'] = id
                item['comment_text'] = com.get('comment').get('text')
                item['user_name'] = com.get('comment').get('user_name')
                item['time'] = com.get('comment').get('create_time')
                item['digg_count'] = com.get('comment').get('digg_count')
                yield item

            yield scrapy.Request(self.comment_url.format(id,id,offset),callback=self.parse_comment,meta={'offset':offset,'id':id},dont_filter=True)


    def shift_content_format(self,content_news):
        """
        转换新闻内容格式
        :param content_news:
        :return: 返回转换格式后的新闻内容
        """
        if isinstance(content_news, str):
            list_content = content_news.split('\\u003C\\u002Fp\\u003E\\u003Cp\\u003E')
            content_str = ''
            for l in list_content:
                if l.startswith('\'\"'):
                    l = l.replace('\'\"', '')
                if l.endswith('\"\''):
                    l = l.replace('\"\'', '')
                if '\\u003Cp\\u003E' in l:
                    l = l.replace('\\u003Cp\\u003E', '')
                elif '\\u003C\\u002Fp\\u003E' in l:
                    l = l.replace('\\u003C\\u002Fp\\u003E', '')
                elif l.startswith('\\u003Cstrong\\u003E') and l.endswith('\\u003C\\u002Fstrong\\u003E'):
                    l = l.replace('\\u003Cstrong\\u003E', '')
                    l = l.replace('\\u003C\\u002Fstrong\\u003E', '')
                    l = '小标题:' + l
                elif l.startswith('\\u003Cb\\u003E') and l.endswith('\\u003C\\u002Fb\\u003E'):
                    l = l.replace('\\u003Cb\\u003E', '')
                    l = l.replace('\\u003C\\u002Fb\\u003E', '')
                    l = '小标题:' + l

                if '\\u003C\\u002Fp\\u003E\\u003C' in l:
                    l = l.replace('\\u003C\\u002Fp\\u003E\\u003C', '\n')
                if '\\u003E' in l:
                    l = l.replace('\\u003E', '\n')
                if '\\u003C' in l:
                    l = l.replace('\\u003C', '')
                if '&amp;#34;' in l:
                    l = l.replace('&amp;#34;', '')
                if '\\u002Fstrong' in l:
                    l = l.replace('\\u002Fstrong', '')
                if 'strong' in l:
                    l = l.replace('strong', '')

                content_str = content_str + '\n' + l
        else:
            content_str = None
        return content_str


    async def _spider_closed(self):
        """spider关闭时，关闭pyppeteer的chromium浏览器"""
        self.logger.debug('brower quit')
        await self.browser.close()