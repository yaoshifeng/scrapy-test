# -*- coding:utf-8 -*-
import scrapy, re
from enum import unique, IntEnum
from xiaoshuo.items import XiaoshuoItem, ChapterContentItem

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


# 对应channel_offset的位置
offset_enum = \
{
    "type": 0,
    "page": 1,
}


def getChannelTailUrl(type, page):
    return "/list/%s_%s.html" % (
        str(type),
        str(page)
    )


def getBookTailUrl(book_offset):
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
    channel_tail_url = getChannelTailUrl(channel_offset[offset_enum['type']], channel_offset[offset_enum['page']])
    # 对应的 url = url + book_tail_url
    # 类型频道url    **需要填补对应书码**
    book_offset = 0
    book_tail_url = getBookTailUrl(book_offset)
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
            yield scrapy.Request(url=url, callback=self.listParse)

    def listParse(self, response):
        # 现获取该类型最大页码的url字符串
        maxpage = response.xpath('//a[contains(@class, "last")]/@href').extract()[0]

        # 正则表达式从该字符串中提取url(group[0]:整个字符串,[1]往后是括号提取的信息,按顺序+1递增)
        maxpage = re.search("[0-9]{1,2}_([0-9]{1,4}).html", maxpage).group(1)
        # print("type:", type(maxpage), "page:", maxpage)

        # 拼接并遍历对应小说类型网页的url:http://www.quanshuwang.com/list/1_(1~999).html
        for self.channel_offset[offset_enum['page']] in range(1, int(maxpage)):
            self.channel_offset[offset_enum['type']] = \
                re.search(r'list/([0-9]{1,2})_[0-9]{1,4}.html', response.url).group(1)
            # print("channel_type(int):", self.channel_offset[offset_enum['type']])

            # 带入得到对应url的尾部:url + /list/1_1.html
            self.channel_tail_url = \
                getChannelTailUrl(
                    self.channel_offset[offset_enum['type']],
                    self.channel_offset[offset_enum['page']]
                )
            yield scrapy.Request(url=self.url + self.channel_tail_url, callback=self.channelParse)

    def channelParse(self, response):
        url_list = response.xpath('//a[contains(@class, "l mr10")]/@href').extract()

        # 得到改网页所有的小说浏览url:
        for i in url_list:
            # print("i:", i)

            # 获取对应书的图书编码:/book_(123456).html
            book_offset = re.search(r'/book_(.*).html', i)[1]
            # print("book_offset:", book_offset)

            self.book_tail_url = getBookTailUrl(book_offset)
            yield scrapy.Request(url=self.url + self.book_tail_url, callback=self.bookParse)

    def bookParse(self, response):

        item = XiaoshuoItem()
        # 小说类型
        item['noveltype'] = response.xpath('//meta[contains(@property, "og:novel:category")]/@content').extract()[0]
        # 小说作者
        item['novelauthor'] = response.xpath('//meta[contains(@property, "og:novel:author")]/@content').extract()[0]
        # 小说名字
        item['novelname'] = response.xpath('//meta[contains(@property, "og:novel:book_name")]/@content').extract()[0]
        # 小说连载状态
        item['novelstatus'] = response.xpath('//meta[contains(@property, "og:novel:status")]/@content').extract()[0]
        # 小说更新时间
        item['updatetime'] = response.xpath('//meta[contains(@property, "og:novel:update_time")]/@content').extract()[0]
        # 小说简介
        item['novelsummary'] = "".join(response.xpath('//div[contains(@id, "waa")]/text()').extract())
        # 小说链接
        item['novelurl'] = response.xpath('//a[contains(@class, "reader")]/@href').extract()[0]

        book_url = response.xpath('//a[contains(@class, "reader")]/@href').extract()[0]

        yield scrapy.Request(url=book_url, callback=self.chapterListParser)

    def chapterListParser(self, response):
        list = response.xpath('//div[contains(@class, "clearfix dirconone")]/li/a/@href').extract()
        for chapter_url in list:
            yield scrapy.Request(url=chapter_url, callback=self.chapterContentParser)
        # pass

    def chapterContentParser(self, response):
        item = ChapterContentItem()
        item['novelchaptertitle'] = response.xpath('//strong[contains(@class, "l jieqi_title")]/text()').extract()[0]
        item['novelcontent'] = "".join(response.xpath('//div[contains(@id, "content")]/text()').extract())

