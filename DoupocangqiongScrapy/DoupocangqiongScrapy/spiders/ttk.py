import scrapy
from ..items import NovelMysqlItem
import pymysql


class TTKSpider(scrapy.Spider):
    name = "ttk"
    allowed_domains = ["cn.ttkan.co"]
    # 定义设置，将优先于并覆盖项目设置
    custom_settings = {
        "ITEM_PIPELINES": {"DoupocangqiongScrapy.pipelines.NovelMysqlPipeline": 300}
    }

    def __init__(self, host, port, user, password, database):
        self.database = database
        self.conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset="utf8mb4",
        )
        self.cursor = self.conn.cursor()

    def start_requests(self):
        start_urls = ["https://cn.ttkan.co/novel/chapters/doupocangqiong-tiancantudou"]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    @classmethod
    def from_crawler(cls, crawler):
        host = crawler.settings.get("MYSQL_HOST")
        port = crawler.settings.get("MYSQL_PORT")
        user = crawler.settings.get("MYSQL_USER")
        password = crawler.settings.get("MYSQL_PASSWORD")
        database = crawler.settings.get("MYSQL_DATABASE")
        spider = super(TTKSpider, cls).from_crawler(
            crawler, host, port, user, password, database
        )
        return spider

    def parse(self, response):
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
        title_index = 1
        for i in response.xpath('//div[@class="full_chapters"]/div[1]/a[@href]'):
            href = response.urljoin(i.xpath("./@href").extract_first())
            title = i.xpath("./text()").extract_first().strip()
            if title in (
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
                title_index += 1
                continue
            self.cursor.execute(
                "select `href` from `doupocangqiong_novel` where `href`=%s", (href)
            )
            if self.cursor.fetchone():
                title_index += 1
                continue
            yield scrapy.Request(
                url=href,
                callback=lambda response, href=href, original_title=title, title_index=title_index: self.parse2(
                    response, href, original_title, title_index
                ),
            )
            title_index += 1

    def parse2(self, response, href, original_title, title_index):
        item = NovelMysqlItem()
        item["title_index"] = title_index
        item["original_title"] = original_title
        item["href"] = href
        item["page_link"] = response.url
        item["content"] = response.xpath('//div[@class="content"]/p/text()').extract()
        yield item
