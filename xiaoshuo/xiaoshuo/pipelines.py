# -*- coding: utf-8 -*-

# Define your item pipelines here
# If you have many piplelines, all should be init here
# and use IF to judge them
#
# DOUGUO Spider pipelines
# @author zhangjianfei
# @date 2017/04/13
# from mysqlUtils import dbhandle_insert_content
# from mysqlUtils import dbhandle_online
# from mysqlUtils import dbhandle_update_status

from xiaoshuo.items import XiaoshuoItem
from xiaoshuo.items import ChapterContentItem
from datetime import datetime
from hashlib import md5
import pymysql
import json


class JsonInfoPipeline(object):

    def __init__(self):
        self.filename = open("novel_info.json", "wb+")

    def process_item(self, item, spider):
        if type(item) is XiaoshuoItem:
            text = json.dumps(dict(item), ensure_ascii = False) + ",\n"
            self.filename.write(text.encode("utf-8"))
            return item

    def close_spider(self, spider):
        self.filename.close()


class JsonContentPipeline(object):

    def __init__(self):
        self.filename = open("novel_chapter.json", "wb+")

    def process_item(self, item, spider):
        if type(item) is ChapterContentItem:
            text = json.dumps(dict(item), ensure_ascii = False) + ",\n"
            self.filename.write(text.encode("utf-8"))
            return item

    def close_spider(self, spider):
        self.filename.close()


class DgPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool
    # process the data

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = pymysql.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        # if spider.name == "spidernovel":
        if type(item) is XiaoshuoItem:
            d = self.dbpool.runInteraction(self._do_upinsert_info, item, spider)
            d.addErrback(self._handle_error, item, spider)
            d.addBoth(lambda _: item)

        if type(item) is ChapterContentItem:
            d = self.dbpool.runInteraction(self._do_upinsert_chapter, item, spider)
            d.addErrback(self._handle_error, item, spider)
            d.addBoth(lambda _: item)
        pass

    def _do_upinsert_info(self, conn, item, spider):
        linkmd5id = self._get_linkmd5id(item)
        #print linkmd5id
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
        conn.execute("""
                select 1 from novelinfo where linkmd5id = %s
        """, (linkmd5id, ))
        ret = conn.fetchone()

        if ret:
            conn.execute("""
                update novelinfo set noveltype = %s, novelauthor = %s, novelname = %s, novelstatus = %s, updatetime = %s where linkmd5id = %s
            """, (item['noveltype'], item['novelauthor'], item['novelname'], item['novelstatus'], item['updatetime'], linkmd5id))

        else:
            conn.execute("""
                insert into novelinfo(id, noveltype, novelauthor, novelname, novelstatus, updated) 
                values(%s, %s, %s, %s, %s, %s)
            """, (linkmd5id, item['noveltype'], item['novelauthor'], item['novelname'], item['novelstatus'], now))

    def _do_upinsert_info(self, conn, item, spider):
        linkmd5id = self._get_linkmd5id(item)
        # print linkmd5id
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
        conn.execute("""
                        select 1 from chapterinfo where linkmd5id = %s
                """, (linkmd5id,))
        ret = conn.fetchone()

        if ret:
            conn.execute("""
                        update chapterinfo set novelchaptertitle = %s, novelcontent = %s where linkmd5id = %s
                    """, (
            item['novelchaptertitle'], item['novelcontent'], linkmd5id))

        else:
            conn.execute("""
                        insert into chapterinfo(id, novelchaptertitle, novelcontent) 
                        values(%s, %s, %s)
                    """, (
            linkmd5id, item['novelchaptertitle'], item['novelcontent']))

    #获取url的md5编码
    def _get_linkmd5id(self, item):
        #url进行md5处理，为避免重复采集设计
        return md5(item['link']).hexdigest()

    #异常处理
    # def _handle_error(self, failue, item, spider):
    #     log.err(failure)
