#-*- coding:utf-8 -*-
import re
import time

import requests
from lxml import etree
from threading import Thread
from queue import Queue


class XingZuo():

    def __init__(self):
        self.list_url = 'https://www.xingzuo360.cn/baiyangzuo/'  # 第一页
        self.headers = {
            'authority': 'www.xingzuo360.cn',
            'method': 'GET',
            'path': '/baiyangzuo/',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'cookie': 'Hm_lvt_529d3552780f4969c7a05dd1caca7919=1578225881; Hm_lpvt_529d3552780f4969c7a05dd1caca7919=1578227989; SERVERID=396e78d111bf7a55bc9c8ea38ebcfdc0|1578228274|1578225875',
            'referer': 'https://www.xingzuo360.cn/shierxingzuo/',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'

        }
        self.page_queue = Queue()

    def save2csv(self):
        pass

    def parse_data(self,detail_page_urls):
            for each in detail_page_urls:
                time.sleep(0.5)
                detail_page_url = 'http:'+each
                response = requests.get(detail_page_url,headers=self.headers)
                data = response.content.decode()
                e = etree.HTML(data)

                # 标题
                title = e.xpath('//div[@class="detail_box"]/h1/text()')
                title = title[0] if title else ''

                # 发布时间
                publish_time = e.xpath('//div[@class="detail_box"]/p/text()')
                publish_time = publish_time[0] if publish_time else ''
                publish_time = re.findall(r'发布时间：(.*?)\s+作者',publish_time)[0]

                # 内容
                content = e.xpath('//div[@id="xz360ArticleContent"]/p//text()')
                content = ''.join(content).strip()

                print(title,publish_time,content)


    def get_detail_page_urls(self,page_queue):
        while not page_queue.empty():
            list_url = self.page_queue.get()
            response = requests.get(list_url,headers=self.headers)
            html = response.content.decode()
            e = etree.HTML(html)
            detail_page_urls = e.xpath('//div[@class="public_column_list"]/ul/li/a/@href')

            self.parse_data(detail_page_urls)
            page_queue.task_done()
        
    def thread(self,page_queue):
        for i in range(10):
            thread = Thread(target=self.get_detail_page_urls,args=(page_queue,))
            thread.daemon = True
            thread.start()
        self.page_queue.join()

    def get_pages(self):
        response = requests.get(self.list_url, headers=self.headers)
        html = response.content.decode()
        pages = re.findall('pageindex">1/(.*?)<',html)[0]
        for page in range(1,int(pages)+1):
            page_urls = f'https://www.xingzuo360.cn/baiyangzuo/p{page}.html'
            self.page_queue.put(page_urls)
            self.thread(self.page_queue)


    def run(self):
        self.get_pages()


if __name__ == '__main__':
    xingzuo = XingZuo()
    xingzuo.run()










