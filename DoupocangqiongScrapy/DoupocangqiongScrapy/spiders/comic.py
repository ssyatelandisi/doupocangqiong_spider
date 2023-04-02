import scrapy
import datetime
from ..items import ComicItem
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    Index,
)


class ComicSpider(scrapy.Spider):
    name = "comic"
    allowed_domains = ["cn.baozimh.com"]
    start_urls = ["https://cn.baozimh.com/comic/doupocangqiong-zhiyindongman_c"]
    # 定义设置，将优先于并覆盖项目设置
    custom_settings = {
        "ITEM_PIPELINES": {"DoupocangqiongScrapy.pipelines.ComicPipeline": 300}
    }

    def __init__(self, name=None, **kwargs):
        self.engine = create_engine("sqlite:///doupocangqiong.db")
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

    def parse(self, response):
        for i in response.xpath(
            '//div[@id="chapter-items" or @id="chapters_other_list"]/*/a[@href]'
        ):
            href = response.urljoin(i.xpath("./@href").extract_first())
            title = i.xpath("./*/span/text()").extract_first().strip()
            if self.engine.execute(
                "select href from doupocangqiong_comic where href=:href",
                **{"href": href}
            ).fetchall():
                continue
            yield scrapy.Request(
                url=href,
                callback=lambda response, href=href, title=title: self.parse2(
                    response, href, title
                ),
            )

    def parse2(self, response, href, title):
        item = ComicItem()
        item["title"] = title
        item["href"] = href
        item["page_link"] = response.url
        for i in response.xpath("//noscript/img[@src and @alt]/@src").extract():
            item["image_url"] = response.urljoin(i)
            yield item
