import time
import re
import aiohttp
import asyncio
import random
import datetime
import logging
from urllib.parse import urljoin
from lxml import etree
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

logging.getLogger().setLevel(logging.INFO)
engine = create_engine("sqlite:///doupocangqiong.db")
metadata = MetaData()
doupocangqiong_novel = Table(
    # 表的名字:
    "doupocangqiong_novel",
    metadata,
    # 表的结构:
    Column("uid", Integer, primary_key=True, nullable=True),
    Column("title", String(1024), nullable=False, index=True),
    Column("href", String(1024), nullable=False, index=True),
    Column("page_link", String(1024), nullable=False, index=True, unique=True),
    Column("content", Text, nullable=False),
    Column("datetime", DateTime, nullable=True, default=datetime.datetime.now),
    sqlite_autoincrement=True,
)
# 创建表，存在就跳过
metadata.create_all(engine)


ua_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19577",
    "Mozilla/5.0 (X11) AppleWebKit/62.41 (KHTML, like Gecko) Edge/17.10859 Safari/452.6",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931",
    "Chrome (AppleWebKit/537.1; Chrome50.0; Windows NT 6.3) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.9200",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (X11; Linux ppc64le; rv:75.0) Gecko/20100101 Firefox/75.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/75.0",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:75.0) Gecko/20100101 Firefox/75.0",
    "Mozilla/5.0 (X11; Linux; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/73.0",
    "Mozilla/5.0 (X11; OpenBSD i386; rv:72.0) Gecko/20100101 Firefox/72.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:71.0) Gecko/20100101 Firefox/71.0",
    "Mozilla/5.0 (Macintosh; U; Mac OS X 10_6_1; en-US) AppleWebKit/530.5 (KHTML, like Gecko) Chrome/ Safari/530.5",
    "Mozilla/5.0 (Macintosh; U; Mac OS X 10_5_7; en-US) AppleWebKit/530.5 (KHTML, like Gecko) Chrome/ Safari/530.5",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-US) AppleWebKit/530.9 (KHTML, like Gecko) Chrome/ Safari/530.9",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-US) AppleWebKit/530.6 (KHTML, like Gecko) Chrome/ Safari/530.6",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-US) AppleWebKit/530.5 (KHTML, like Gecko) Chrome/ Safari/530.5",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2866.71 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2820.59 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2762.73 Safari/537.3",
]

sem = asyncio.Semaphore(16)


def func(i: str):
    i = re.sub(r"\xa0+|\u3000+", "", i)
    return re.sub(r"\r+|(\r\n)+", r"\n", i)


async def fetch2(
    db_session: sessionmaker, session: aiohttp.ClientSession, url: str, title: str
):
    ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    try:
        async with session.get(
            url,
            headers={
                "Accept-Encoding": "gzip, br, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,ko;q=0.5,zh-TW;q=0.4,und;q=0.3,ru;q=0.2",
                "User-Agent": random.choice(ua_list),
                "x-forwarded-for": ip,
                "X-Remote-IP": ip,
                "X-Real-IP": ip,
                "X-Originating-IP": ip,
            },
            proxy="http://127.0.0.1:10808",
        ) as resp:
            content_list = etree.HTML(await resp.text()).xpath(
                '//div[@id="content"]/text()'
            )
            content = "\n".join(list(map(func, content_list)))
            content = re.sub(r"\n+", r"\n", content)
            content = (
                re.sub(r"请记住本书首发域名.*顶点小说手机版阅读网址：[\.\w]+", "", content)
                .replace(title, "", 1)
                .replace(title.replace(" ", "\n"), "", 1)
                .strip()
                + "\n"
            )
            db_session.execute(
                doupocangqiong_novel.insert().values(
                    title=title,
                    href=url,
                    page_link=str(resp.url),
                    content=content,
                )
            )
            db_session.commit()
        await asyncio.sleep(random.randint(50, 200) / 100)
    except Exception as e:
        logging.info(e)
        logging.info(url + "请求失败")


async def fetch(url: str):
    async with sem:
        db_session = sessionmaker(engine)()
        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit_per_host=16),
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "Accept-Encoding": "gzip, br, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,ko;q=0.5,zh-TW;q=0.4,und;q=0.3,ru;q=0.2",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
                },
            ) as session:
                async with session.get(
                    url,
                    proxy="http://127.0.0.1:10808",
                ) as resp:
                    tasks = list()
                    for i in etree.HTML(await resp.text()).xpath(
                        '//*[@id="list"]/dl/dt[2]/following-sibling::dd/a[@href]'
                    ):
                        href = urljoin(str(resp.url), i.xpath("./@href")[0])
                        title = i.xpath("./text()")[0].strip()
                        title == "第五百三十七章 第二轮" if title == "VIP章节目录 第五百三十七章 第二..." else title
                        if (
                            db_session.query(doupocangqiong_novel.c.href)
                            .filter(doupocangqiong_novel.c.href == href)
                            .first()
                        ):
                            continue
                        elif title in (
                            "新书大主宰已发。",
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
                            continue
                        else:
                            tasks.append(
                                asyncio.create_task(
                                    fetch2(db_session, session, href, title)
                                )
                            )
                    if tasks:
                        print(f"{len(tasks)}个任务")
                        await asyncio.wait(tasks)
                        db_session.commit()
                        db_session.close()
                    else:
                        db_session.close()
                        return
        except Exception as e:
            logging.info(e)
            logging.info(url + "请求失败")


async def main():
    urls = [
        "https://www.ddyueshu.com/1_1600/",
    ]
    tasks = [asyncio.create_task(fetch(url)) for url in urls]
    await asyncio.wait(tasks)


if __name__ == "__main__":
    starttime = time.time()
    # asyncio.set_event_loop_policy(
    #     asyncio.WindowsSelectorEventLoopPolicy()
    # )  # Windows平台添加此行修复bug
    # asyncio.run(main())
    asyncio.get_event_loop().run_until_complete(main())
    print("耗时:" + str(time.time() - starttime))
