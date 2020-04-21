# -*- coding: utf-8 -*-


import pymongo
import time
from toutiao.items import ToutiaoItem, ToutiaoCommentItem

class MongoDBPipeline(object):
    """将item持久化到mongodb"""
    def __init__(self,mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[ToutiaoItem.collection].create_index([('id', pymongo.ASCENDING)])
        self.db[ToutiaoCommentItem.collection].create_index([('id', pymongo.ASCENDING)])

    def process_item(self, item, spider):

        self.collection = self.db[item.collection]

        if item.collection == 'toutiao_hot_news':
            self.collection.update({'title':item.get('title')},{'$set':item},True)
        if item.collection == 'comment_news':
            self.collection.update({'user_name':item.get('user_name'),'comment_text':item.get('comment_text')},{'$set':item},True)
        return item

    def close_spider(self, spider):
        self.client.close()


class TimePipeline(object):
    '''将ToutiaoCommentItem的时间戳改成"%Y-%m-%d %H:%M:%S"格式'''
    def process_item(self, item, spider):

        if item.collection == 'comment_news':

            timeStamp = int(item.get('time'))
            timeArray = time.localtime(timeStamp)
            new_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            item['time'] = new_time
        return item
