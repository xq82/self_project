#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-11-19 13:35:35
# Project: 201763_1599_web

from pyspider.libs.base_handler import *
import re, random, time, requests, datetime, json
from pickle import loads


'''这个是华丽志网站的爬取
去年11月19号写的
是我写的200多个脚本中的一个
'''



class Handler(BaseHandler):
    crawl_config = {
    }


    @every(minutes=24 * 60)
    def on_start(self):
        #起始页面
        self.crawl('http://luxe.co/', callback=self.cl_img)

        self.crawl('http://en.luxe.co/', callback=self.cl_img)

    @config(age=10 * 24 * 60 * 60)
    def cl_img(self, res):
        #所有的板块的url
        for a in res.doc(
                '.right > .menu-item-66892 > .sub-menu a,.right > .menu-item-66897 > .sub-menu a,.right > .menu-item-66898 > .sub-menu a,.right > .menu-item-67090 > .sub-menu a,.right > .menu-item-66900 > a,.right > .menu-item-67069 > .sub-menu a,.right > .menu-item-66901 > .sub-menu a,.right > .menu-item-66938 > .sub-menu a,.right > .menu-item-66902 > .sub-menua a').items():
            self.crawl(a.attr.href, callback=self.cl_ajax)

        for a in res.doc(
                '.sec-menu > .sec-main-navigation .menu-item-118 > a,.sec-menu > .sec-main-navigation .menu-item-119 > a,.sec-menu > .sec-main-navigation .menu-item-117 > a').items():
            self.crawl(a.attr.href, callback=self.cl_ajax)

    def cl_ajax(self, res):
        for a in res.doc('h2 > a').items():
            self.crawl(a.attr.href, callback=self.cl_zym)

        # 翻页 找到每个板块的最大页数   正则匹配最大值  然后拼接成新的url进行翻页
        max_page = re.findall(r'var max_num_pages=(.*?);', res.text)
        max_page = int(max_page[0]) if re.findall(r'var max_num_pages=(.*?);', res.text) else 1
        if max_page >= 2:
            for next_page_num in range(2, max_page + 1):
                url = res.url.rsplit('page', 1)[0] + '/page/{}'.format(next_page_num)
                self.crawl(url, callback=self.find_zym)

    def find_zym(self, res):
        for a in res.doc('h2 > a').items():
            self.crawl(a.attr.href, callback=self.cl_zym)

    def cl_zym(self, res):
        for img in res.doc('.content p img,p img,.content img').items():
            img_u = img.attr.src
            date = res.doc('.post-meta').text()
            title = res.doc('h1').text()
            text = res.doc('.content > p').text()
            data = {
                "pid": str(time.time()).split('.')[0] + str(random.randint(10000, 99999)),
                "url": res.url,
                "pic_url": img_u,
                "url_article_title": title,
                "url_article": text,
            }
            #将爬取的title, url, content, img_url数据发送到页面上，能够展示的
            self.send_message(self.project_name, data, img_u)

    def on_message(self, project, msg):
        return msg