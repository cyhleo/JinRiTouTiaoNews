# -*- coding: utf-8 -*-

import scrapy

class ToutiaoItem(scrapy.Item):

    collection = 'toutiao_hot_news'

    # 新闻标题
    title = scrapy.Field()
    # 来源
    source = scrapy.Field()
    # 总评论数
    comment_num = scrapy.Field()
    # 发布时间
    time = scrapy.Field()
    # 新闻id
    news_id = scrapy.Field()
    # 新闻内容
    news_content = scrapy.Field()

class ToutiaoCommentItem(scrapy.Item):

    collection = 'comment_news'

    # 新闻id
    news_id = scrapy.Field()
    # 评论者的用户名
    user_name = scrapy.Field()
    # 评论时间
    time = scrapy.Field()
    # 点赞数
    digg_count = scrapy.Field()
    # 评论内容
    comment_text = scrapy.Field()