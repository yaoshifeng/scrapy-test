# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class XiaoshuoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # 小说类型
    noveltype = scrapy.Field()
    # 小说作者
    novelauthor = scrapy.Field()
    # 小说名字
    novelname = scrapy.Field()
    # 小说连载状态
    novelstatus = scrapy.Field()
    # 小说更新时间
    updatetime = scrapy.Field()
    # 小说简介
    novelsummary = scrapy.Field()
    # 小说链接
    novelurl = scrapy.Field()
    pass

class ChapterContentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # 章节名字
    novelchaptertitle = scrapy.Field()
    # 章节内容
    novelcontent = scrapy.Field()

