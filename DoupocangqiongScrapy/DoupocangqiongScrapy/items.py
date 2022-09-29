# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoupocangqiongscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ComitItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()  # 章节标题
    href = scrapy.Field()  # 章节超链接地址
    page_link = scrapy.Field()  # 相应页面地址
    image_url = scrapy.Field()  # 漫画图片地址
    datetime = scrapy.Field()  # 添加时间


class NovelItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()  # 章节标题
    original_title = scrapy.Field()  # 原始章节标题
    title_index = scrapy.Field()
    href = scrapy.Field()  # 章节超链接地址
    page_link = scrapy.Field()  # 相应页面地址
    content = scrapy.Field()  # 小说内容
    datetime = scrapy.Field()  # 添加时间


class NovelMysqlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()  # 章节标题
    original_title = scrapy.Field()  # 原始章节标题
    title_index = scrapy.Field()
    href = scrapy.Field()  # 章节超链接地址
    page_link = scrapy.Field()  # 相应页面地址
    content = scrapy.Field()  # 小说内容
    datetime = scrapy.Field()  # 添加时间
