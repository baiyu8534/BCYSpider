# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
from pymongo import MongoClient
import redis
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import re

client = MongoClient("localhost", 27017)
collection = client["BCY"]["BCY_cos_image_v2"]


def reset_file_path(file_path):
    r_file_path = re.sub('[\/:*?"<>|]', '-', file_path)  # 去掉非法字符
    return r_file_path


class DeleteRepeatDataPipeline(object):
    def __init__(self):
        self.ids = set()
        self.redis_conn = redis.Redis(host='localhost', port=6379, db=0)
        self.redis_ids_key = "ids"

    def process_item(self, item, spider):
        added = self.redis_conn.sadd(spider.name + ":" + str(self.redis_ids_key), item["item_id"])
        if added != 1:
            item.clear()
        return item


class BcyscrapyspiderPipeline(object):
    def process_item(self, item, spider):
        if len(item) != 0:
            item["catch_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            collection.insert(dict(item))
            print("保存-->>" + item["cos_info_name"])
            # print('保存到mongodb里了')
        return item


class DownloadSmallSizeImage(ImagesPipeline):
    def get_media_requests(self, item, info):
        # 这个方法是在发送下载请求之前调用的，其实这个方法本身就是去发送下载请求的
        tags = item["tags"]
        if len(tags) > 2:
            tags_str = "-".join(tags[:3])
        else:
            tags_str = "-".join(tags)
        dir_name = item["user_name"] + "-" + tags_str + item["item_id"]
        return [Request(x["ssize_img_url"], meta={'dir_name': dir_name}) for x in item["image_list"] if
                x["ssize_img_url"] != ""]

    def file_path(self, request, response=None, info=None):
        # 这个方法是在图片将要被存储的时候调用，来获取这个图片存储的路径
        dir_name = request.meta['dir_name']
        if ".jpg" in request.url.split('/')[-1].split('~')[0]:
            file_name = request.url.split('/')[-1].split('~')[0].split('.jpg')[0]
        else:
            file_name = request.url.split('/')[-1].split('~')[0]
        image_path = dir_name + "/" + file_name + ".jpg"
        return image_path


class DownloadFullSizeImage(ImagesPipeline):
    def get_media_requests(self, item, info):
        # 这个方法是在发送下载请求之前调用的，其实这个方法本身就是去发送下载请求的
        tags = item["tags"]
        if len(tags) > 2:
            tags_str = "-".join(tags[:3])
        else:
            tags_str = "-".join(tags)
        dir_name = item["user_name"] + "-" + tags_str + item["item_id"]
        return [Request(x["fsize_img_url"], meta={'dir_name': dir_name}) for x in item["image_list"] if
                x["ssize_img_url"] != ""]

    def file_path(self, request, response=None, info=None):
        # 这个方法是在图片将要被存储的时候调用，来获取这个图片存储的路径
        dir_name = request.meta['dir_name']
        if ".jpg" in request.url.split('/')[-1].split('~')[0]:
            file_name = request.url.split('/')[-1].split('~')[0].split('.jpg')[0]
        else:
            file_name = request.url.split('/')[-1].split('~')[0]
        image_path = dir_name + "/" + file_name + ".jpg"
        image_path = reset_file_path(image_path)
        return image_path
