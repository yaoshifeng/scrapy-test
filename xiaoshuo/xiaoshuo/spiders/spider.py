# -*- coding:utf-8 -*-
import scrapy, re
from enum import Enum, unique, IntEnum
from xiaoshuo.items import XiaoshuoItem


@unique
class Novel_Type(IntEnum):
    XUANHUAN =  1   #玄幻魔法
    WUXIA    =  2   #武侠修真
    CHUNAI   =  3   #纯爱耽美
    DUSHI    =  4   #都市言情
    ZHICHANG =  5   #职场校园
    CHUANYUE =  6   #穿越重生
    LISHI    =  7   #历史军事
    WANGYOU  =  8   #网游动漫
    KONGBU   =  9   #恐怖灵异
    KEHUAN   = 10   #科幻小说
    MEIWEN   = 11   #没问名著
    ...
    WEIZHI   =  0   #未知小说


@unique
class Novel_Info(IntEnum):
    BOOK_ID= 0      #书ID
    TYPE   = 1      #类型
    NAME   = 2      #书名
    SERI   = 3      #状态（连载，完本，太监）
    AUTHOR = 4      #作者名字
    UPDATE = 5      #书更新时间
    SUM    = 6      #简介
    ...


def getChannelTailUrl(type, page):
    return "/list/%s_%s.html" % (
        str(type),
        str(page)
    )


def getChannelTailUrl(book_offset):
    return "/book_%s.html" % (str(book_offset))


def getCatalogTailUrl(catalog_offset):
    return "/book/%s/%s.html" % (
        str(catalog_offset // 1000),
        str(catalog_offset)
    )


class spidernovel(scrapy.Spider):
    # 爬虫的名字
    name = "spidernovel"
    # 爬虫的作用
    allowed = ["quanshuwang.com"]
    # 爬取的主网站
    url = "http://www.quanshuwang.com"
    # 对应的 url = url + channel_tail_url
    # 第一个是类型频道码，第二个是对应类型的小说频道浏览页码
    channel_offset = [1, 1]
    channel_tail_url = getChannelTailUrl(channel_offset)
    # 对应的 url = url + book_tail_url
    # 类型频道url    **需要填补对应书码**
    book_offset = 0
    book_tail_url = getChannelTailUrl(book_offset)
    # 对应的url = url + catalog_tail_url
    # 书记的章节频道 **需要填补对应的书码**
    catalog_offset = 0
    catalog_tail_url = getCatalogTailUrl(catalog_offset)

    def start_requests(self):
        urls = [
            "http://www.quanshuwang.com/list/1_1.html",
            "http://www.quanshuwang.com/list/2_1.html",
            # "http://www.quanshiwang.com/list/3_1.html",
            # "http://www.quanshiwang.com/list/4_1.html",
            # "http://www.quanshiwang.com/list/5_1.html",
            # "http://www.quanshiwang.com/list/6_1.html",
            # "http://www.quanshiwang.com/list/7_1.html",
            # "http://www.quanshiwang.com/list/8_1.html",
            # "http://www.quanshiwang.com/list/9_1.html",
            # "http://www.quanshiwang.com/list/10_1.html",
            # "http://www.quanshiwang.com/list/11_1.html",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        url_list = response.xpath('//a[contains(@class, "l mr10")]/@href').extract()
        temp = re.search(r'(\d)_(\d)', response.url)
        self.channel_offset[0] = temp.group(1)
        self.channel_offset[1] = temp.group(2)
        for i in range(len(url_list)):
            yield scrapy.Request(self.url + str(self.channel_offset[1] + 1), callback=self.parse)
            # print(url_list[i])

    # def parse_
