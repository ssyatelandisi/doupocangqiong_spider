# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    create_engine,
    Table,
    MetaData,
    Index,
)
from sqlalchemy.orm import sessionmaker
from pymysql import cursors
import pymysql
import datetime
import re


class DoupocangqiongscrapyPipeline:
    def process_item(self, item, spider):
        return item


class ComicPipeline:
    def __init__(self):
        self.engine = create_engine("sqlite:///doupocangqiong.db")

    def open_spider(self, spider):
        self.metadata = MetaData(self.engine)
        self.doupocangqiong_comic = Table(
            # 表的名字:
            "doupocangqiong_comic",
            self.metadata,
            # 表的结构:
            Column("uid", Integer, primary_key=True, nullable=True),
            Column("title", String(1024), nullable=False),
            Column("href", String(1024), nullable=False),
            Column("page_link", String(1024), nullable=False),
            Column("image_url", String(1024), nullable=False),
            Column("datetime", DateTime, nullable=True, default=datetime.datetime.now),
            Index("ix_doupocangqiong_comic_title", "title"),
            Index("ix_doupocangqiong_comic_href", "href"),
            Index("ix_doupocangqiong_comic_page_link", "page_link"),
            sqlite_autoincrement=True,
        )
        # 创建表，存在就跳过
        self.metadata.create_all()
        DBSession = sessionmaker(self.engine)
        self.session = DBSession()

    def close_spider(self, spider):
        self.session.commit()
        self.session.close()

    def process_item(self, item, spider):
        self.session.execute(
            self.doupocangqiong_comic.insert().values(
                title=item["title"],
                href=item["href"],
                page_link=item["page_link"],
                image_url=item["image_url"],
            )
        )
        return item


def func(i: str):
    i = re.sub(r"\xa0+|\u3000+", "", i)
    i = re.sub(r"\r|\n+", r"\n", i)
    return i.strip()


class NovelPipeline:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        ...

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get("MYSQL_HOST"),
            port=crawler.settings.get("MYSQL_PORT"),
            user=crawler.settings.get("MYSQL_ROOT"),
            password=crawler.settings.get("MYSQL_PASSWORD"),
            database=crawler.settings.get("MYSQL_DATABASE"),
        )

    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="123456",
            # database="doupocangqiong",
            cursorclass=cursors.DictCursor,  # 返回字典型数据游标
            charset="utf8mb4",
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE DATABASE IF NOT EXISTS `%s` DEFAULT CHARACTER SET utf8mb4"
            % (self.database,)
        )
        self.cursor.execute("USE `%s`" % (self.database,))
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `doupocangqiong_novel2` (
                `uid` int(11) NOT NULL AUTO_INCREMENT,
                `title_index` int(4) NOT NULL,
                `original_title` varchar(256) NOT NULL,
                `title` varchar(256) NOT NULL,
                `href` varchar(256) NOT NULL,
                `page_link` varchar(256) NOT NULL,
                `content` longtext DEFAULT NULL,
                `datetime` datetime DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`uid`),
                UNIQUE KEY `ix_doupocangqiong_novel2_page_link` (`page_link`),
                KEY `ix_doupocangqiong_novel2_original_title` (`original_title`),
                KEY `ix_doupocangqiong_novel2_href` (`href`),
                KEY `ix_doupocangqiong_novel2_title` (`title`),
                KEY `ix_doupocangqiong_novel2_title_index` (`title_index`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4"""
        )
        self.insert_sql = """
        INSERT INTO `doupocangqiong_novel2` (
            `title_index`,`original_title`,`title`,`href`,`page_link`,`content`
            ) 
        VALUES (
            %(title_index)s,%(original_title)s,%(title)s,%(href)s,%(page_link)s,%(content)s
            )
        """  # 此种后面参数为字典型

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("title") in (
            "两年三个月，五百三十万。",
            "新书大主宰已发。",
            "感言。",
            "萧玄魂天帝篇",
            "萧炎云韵篇",
            "新书已发~~~",
            "愿望终达成。",
            "最后的二十四小时！！！！",
            "收到起点的锦书，试用了下，效果很不错",
            "新书元尊已在起点上传，欢迎大家阅读。",
            "第一章 五帝破空",
            "今天晚上七点半，斗破在线大活动。",
            "《斗破苍穹：斗帝之路》手游·角色传记（上）",
            "《斗破苍穹：斗帝之路》手游·角色传记（下）",
        ):
            raise DropItem("无效内容")

        if adapter.get("original_title") == "第八十七 下杀手":
            adapter["original_title"] = "第八十七章 下杀手"
        elif adapter.get("original_title") == "第二层":
            adapter["original_title"] = "第四百四十八章 第二层"
        elif adapter.get("original_title") == "第一轮，开始！":
            adapter["original_title"] = "第三百零五章 第一轮，开始！"
        elif adapter.get("original_title") == "第一重：青莲变！":
            adapter["original_title"] = "第三百七十一章 第一重：青莲变！"
        elif adapter.get("original_title") == "第二轮":
            adapter["original_title"] = "第三百零八章 过于简单的第二轮"
        elif adapter.get("original_title") == "第三":
            adapter["original_title"] = "第七百八十七章 榜上第三！"
        elif adapter.get("original_title") == "VIP章节目录 第五百三十七章 第二...":
            adapter["original_title"] = "第五百三十七章 第二轮"
        elif adapter.get("original_title") == "第三层":
            adapter["original_title"] = "第一千三百三十一章 第三层"
        elif adapter.get("original_title") == "第一百一十七章 飞行斗技：鹰之翼...":
            adapter["original_title"] = "第一百一十七章 飞行斗技：鹰之翼"
        elif adapter.get("original_title") == "第一百二十二章 地阶斗技：焰分噬...":
            adapter["original_title"] = "第一百二十二章 地阶斗技：焰分噬浪尺！"
        elif adapter.get("original_title") == "第一百三十一章 神秘女人与六阶魔...":
            adapter["original_title"] = "第一百三十一章 神秘女人与六阶魔兽紫晶翼狮王"

        content = "\n".join(list(map(func, adapter.get("content"))))
        content = re.sub(r"\n+", r"\n", content)
        content = re.sub(r"全文字小說閱讀，盡在wap.16k16k.cn.文.學網", "", content)
        content = re.sub(r"全文字版小说，更新，更快，16k网，电脑站：16k手机站：wàp.16k支持，支持16k", "", content)
        content = re.sub(r"16k小说wap.16k整理", "", content)
        content = re.sub(r"小说整理发布于16k", "", content)
        content = re.sub(r"手机轻松：wap.16k整理", "", content)
        content = re.sub(r"手机访问：wap.16Κ.cn", "", content)
        content = re.sub(r"手机轻松：wàp.16k文字版首发", "", content)
        content = re.sub(r"本书转载16k网wudongqiankun'>", "", content)
        content = re.sub(r"手机访问：wàp.16k", "", content)
        content = re.sub(r"全文字版小说，更新，更快，16k网，电脑站：16k手机站：wàp.16k支持，支持16k", "", content)
        content = re.sub(r"请记住本书首发域名.*顶点小说手机版阅读网址：[\.\w]+", "", content)

        adapter["content"] = (
            content.replace(adapter.get("original_title"), "", 1)
            .replace(adapter.get("original_title").replace(" ", "\n"), "", 1)
            .strip()
            + "\n"
        )
        try:
            adapter[
                "title"
            ] = f"""{adapter.get("title_index"):>04} {adapter.get("original_title").split("章 ")[1]}"""
        except:
            print(adapter["original_title"])
            return

        try:
            self.cursor.execute(self.insert_sql, dict(adapter))
        except Exception as e:
            print(e)
            self.conn.rollback()
        else:
            self.conn.commit()

        return item


# MYSQL存储方案
class NovelMysqlPipeline:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        ...

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get("MYSQL_HOST"),
            port=crawler.settings.get("MYSQL_PORT"),
            user=crawler.settings.get("MYSQL_ROOT"),
            password=crawler.settings.get("MYSQL_PASSWORD"),
            database=crawler.settings.get("MYSQL_DATABASE"),
        )

    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="123456",
            # database="doupocangqiong",
            cursorclass=cursors.DictCursor,  # 返回字典型数据游标
            charset="utf8mb4",
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE DATABASE IF NOT EXISTS `%s` DEFAULT CHARACTER SET utf8mb4"
            % (self.database,)
        )
        self.cursor.execute("USE `%s`" % (self.database,))
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS `doupocangqiong_novel` (
                `uid` int(11) NOT NULL AUTO_INCREMENT,
                `title_index` int(4) NOT NULL,
                `original_title` varchar(256) NOT NULL,
                `title` varchar(256) NOT NULL,
                `href` varchar(256) NOT NULL,
                `page_link` varchar(256) NOT NULL,
                `content` longtext DEFAULT NULL,
                `datetime` datetime DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`uid`),
                UNIQUE KEY `ix_doupocangqiong_novel_page_link` (`page_link`),
                KEY `ix_doupocangqiong_novel_original_title` (`original_title`),
                KEY `ix_doupocangqiong_novel_href` (`href`),
                KEY `ix_doupocangqiong_novel_title` (`title`),
                KEY `ix_doupocangqiong_novel_title_index` (`title_index`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4"""
        )
        self.insert_sql = """
        INSERT INTO `doupocangqiong_novel` (
            `title_index`,`original_title`,`title`,`href`,`page_link`,`content`
            ) 
        VALUES (
            %(title_index)s,%(original_title)s,%(title)s,%(href)s,%(page_link)s,%(content)s
            )
        """  # 此种后面参数为字典型
        # self.insert_sql = (
        #     "INSERT INTO `doupocangqiong_novel` (`title`,`href`,`page_link`,`content`) VALUES (%s,%s,%s,%s)"  # 此种后面参数为元组或列表型
        # )

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("original_title") in (
            "两年三个月，五百三十万。",
            "新书大主宰已发。",
            "感言。",
            "萧玄魂天帝篇",
            "萧炎云韵篇",
            "新书已发~~~",
            "愿望终达成。",
            "最后的二十四小时！！！！",
            "收到起点的锦书，试用了下，效果很不错",
            "新书元尊已在起点上传，欢迎大家阅读。",
            "第一章 五帝破空",
            "今天晚上七点半，斗破在线大活动。",
            "《斗破苍穹：斗帝之路》手游·角色传记（上）",
            "《斗破苍穹：斗帝之路》手游·角色传记（下）",
        ):
            raise DropItem("无效内容")
        if adapter.get("original_title") == "第八十七 下杀手":
            adapter["original_title"] = "第八十七章 下杀手"
        content = "\n".join(list(map(func, adapter.get("content"))))
        content = re.sub(r"\n+", r"\n", content)
        adapter["content"] = (
            content.replace(adapter.get("original_title"), "", 1)
            .replace(adapter.get("original_title").replace(" ", "\n"), "", 1)
            .strip()
            + "\n"
        )
        adapter[
            "title"
        ] = f"""{adapter.get("title_index"):>04} {adapter.get("original_title").split("章 ")[1]}"""
        try:
            self.cursor.execute(self.insert_sql, dict(adapter))
        except Exception as e:
            print(e)
            self.conn.rollback()
        else:
            self.conn.commit()
        return item
