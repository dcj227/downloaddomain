# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from BeautifulSoup import BeautifulSoup

import os

def get_path(url): 
    start = url.find('//')
    if (start == -1):
        return ''

    if url.find('?') != -1:
        url = url[:url.find('?')]
    if url.find('#') != -1:
        url = url[:url.find('#')]

    if url.endswith('/'):
        url += 'index.html'

    pos1 = url.find('/', start + 2)

    url = url[pos1 + 1:]

    return url

def change_path(base, href):
    temp_path = base
    if temp_path.find('/') == 0:
        temp_path = temp_path[1:]
    if href.find('/') == 0:
        href = href[1:]
    while temp_path.find('/') != -1:
        temp = temp_path[:temp_path.find('/')]
        pos2 = href.find(temp)
        if pos2 == 0:
            href = href[len(temp)+1:]
        else:
            while temp_path.find('/') != -1:
                temp_path = temp_path[temp_path.find('/') + 1:]
                href = '../' + href
            return href
        temp_path = temp_path[temp_path.find('/') + 1:]
    return href

def create_file(work_dir, file_path, soup):
    if not os.path.isdir(work_dir):
        os.mkdir(work_dir)
    os.chdir(work_dir)
    if file_path.find('/') == 0:
        file_path = file_path[1:]
    #if not file_path.endswith('/'):
    #    file_path += '/'
    i = 0
    while file_path.find('/') != -1:
        i += 1
        temp = file_path[0:file_path.find('/') + 1]
        file_path = file_path[file_path.find('/') + 1:]
        if not os.path.exists(temp):
            os.mkdir(temp)
        os.chdir(temp)
    filename = file_path[file_path.rfind('/') + 1:]
    if not (os.path.exists(filename)):
        fo = open(filename, 'wb')
        fo.write(str(soup))
        fo.close()

    while i:
        os.chdir('../')
        i -= 1
    os.chdir('../')

class CplusplusSpider(CrawlSpider):
    name = "cplusplus"
    allowed_domains = ["cplusplus.com"]
    start_urls = (
        'http://www.cplusplus.com/',
    )
    rules = (
        Rule(
            LinkExtractor(tags = ('a', 'area', 'img', 'script'),
                attrs=('href', 'src')),
            callback = 'parse_website'),
    )
    path = ''
    workdir = 'www.cplusplus.com/'
    number = 0

    def __init__(self):
        CrawlSpider.__init__(self)
        #log.start()

    def parse_website(self, response):
        self.number += 1 
        print self.number

        self.path = get_path(response.url)
        #log('start parse, url=%s', response.url, level=log.WARNING)
        soup = BeautifulSoup(response.body)
        soup = self.rewrite_path(soup)
        # loop crawl links in this page

        create_file(self.workdir, self.path, soup)

    def rewrite_path(self, soup):
        if not (isinstance(soup, BeautifulSoup)): 
            return 
        tags = soup.findAll(href = True)
        for tag in tags:
            tag['href'] = self.parse_href_src(tag['href'])
        tags = soup.findAll(src = True)
        for tag in tags:
            tag['src'] = self.parse_href_src(tag['src'])

        return soup

    def parse_href_src(self, href):
        try:
            if href.index('http') == 0:
                return href
        except Exception, e:
            pass
        try:
            href = href[:href.index('?')]
        except Exception, e:
            pass
        
        try:
            href = href[:href.index('#')]
        except Exception, e:
            pass
        try:
            if (href.endswith('/')):
                href += 'index.html'
        except Exception, e:
            pass
        try:
            if (href.index('/') == 0):
                href = href[1:]
        except Exception, e:
            pass
        href = change_path(self.path, href) 

        return href
