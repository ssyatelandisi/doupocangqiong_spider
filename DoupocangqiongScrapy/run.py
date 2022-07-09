from scrapy import cmdline

print("爬虫名称: novel, comic, ttk")
spider = input("输入爬虫名称：")
cmdline.execute(f"scrapy crawl {spider.strip()}".split(" "))
