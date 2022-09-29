# 斗破苍穹爬虫

scrapy 和 aiohttp 两种方案的斗破苍穹爬虫

## scrapy 版本

### 安装依赖环境

`pip install scrapy, sqlalchemy`

### 创建项目

`scrapy startproject DoupocangqiongScrapy`

### 创建爬虫

`scrapy genspider comic https://cn.baozimh.com/comic/doupocangqiong-zhiyindongman_c`

`scrapy genspider novel https://www.ddyueshu.com/1_1600/`

### 编辑 middlewares

`middlewares.py`

1. 添加 user-agent 随机范围列表
2. 添加随机头部 ip
3. 添加 proxy 代理【可选】

### 激活 middlewares

`settings.py`

开启 DOWNLOADER_MIDDLEWARES 项

> `"DoupocangqiongScrapy.middlewares.DoupocangqiongscrapyDownloaderMiddleware": 543,`

### 编辑 items

`items.py`

定义 ComitItem,NovelItem 两个类和类成员

### 编辑 pipelines

`pipelines.py`

定义 ComicPipeline, NovelPipeline 两个类，配置好各自的数据库、数据清洗和数据库入库

### 激活 pipelines

`settings.py`

开启 ITEM_PIPELINES 项

> `# "DoupocangqiongScrapy.pipelines.ComicPipeline": 300, # 仅爬取漫画`

> `# "DoupocangqiongScrapy.pipelines.NovelPipeline": 300, # 仅爬取小说`

依据爬虫名称选择开启，也可以在 `spiders` 中添加 `custom_settings` 开启

### 编辑 `spider`

`comic.py`

`novel.py`

### 创建 run 启动文件

`run.py`

导入 scrapy 中的 cmdline，使用 execute 运行爬虫

## aiohttp 版本

### 安装依赖环境

`pip install aiohttp, lxml, sqlalchemy`

### 编辑爬虫文件

`comic.py`

`novel.py`

