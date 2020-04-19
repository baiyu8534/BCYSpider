# -*- coding: utf-8 -*-
import scrapy
import json


class BcyspiderSpider(scrapy.Spider):
    name = 'bcySpider'
    # 坑爹 这个不能加 http
    allowed_domains = ['bcy.net']
    # 从0开始
    start_urls = ['http://bcy.net/apiv3/common/circleFeed?circle_id=1195&since=rec:{}']

    def start_requests(self):
        start_url = BcyspiderSpider.start_urls[0].format("0")
        print(start_url)
        yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response):
        json_str = response.text
        json_data = json.loads(json_str)
        for item_d in json_data["data"]["items"]:
            item_detail = item_d["item_detail"]
            tags = [tag_info["tag_name"] for tag_info in item_detail["post_tags"]]
            if "COS前COS后" in tags:
                continue
            if item_detail["type"] == "video":
                continue
            item = {}
            # 先判断要不要
            item["item_id"] = item_detail['item_id']
            item["user_name"] = item_detail['uname']
            item["tags"] = tags
            item["cos_info_name"] = item_detail['plain']
            item["cos_info_url"] = "https://bcy.net/item/detail" + item_detail['item_id']
            item["ctime"] = item_detail['ctime']
            # 去原始尺寸的头像图片
            item["uicon_img_url"] = item_detail['avatar'].split("~")[0] + "~noop.image"

            image_list = []
            for image in item_detail["image_list"]:
                image_info = {}
                image_info["fsize_img_url"] = image["path"]
                image_info["small_data_fsize_img"] = ""
                image_info["ssize_img_url"] = ""
                if "user" in image["path"]:
                    if ".com" in image["path"]:
                        image_info["small_data_fsize_img"] = "https://p1-bcy.byteimg.com/img/banciyuan" \
                                                             + image["path"].split(".com")[1] \
                                                             + "~noop.image"
                        image_info["ssize_img_url"] = "https://p1-bcy.byteimg.com/img/banciyuan" \
                                                  + image["path"].split(".com")[1] \
                                                  + "~tplv-banciyuan-w650.image"
                else:
                    if "com/banciyuan" in image["path"]:
                        image_info["small_data_fsize_img"] = "https://p1-bcy.byteimg.com/img/banciyuan" \
                                                             + image["path"].split("com/banciyuan")[1] \
                                                             + "~noop.image"
                        image_info["ssize_img_url"] = "https://p1-bcy.byteimg.com/img/banciyuan" \
                                                  + image["path"].split("com/banciyuan")[1] \
                                                  + "~tplv-banciyuan-w650.image"
                image_info["w"] = image["w"]
                image_info["h"] = image["h"]
                image_list.append(image_info)
            item["image_list"] = image_list
            yield item
        for i in range(1, 5):
            yield scrapy.Request(
                url=BcyspiderSpider.start_urls[0].format(str(i)),
                callback=self.parse
            )
