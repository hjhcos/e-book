#!/usr/bin/python
# -*- encoding: utf-8 -*-
"""
@File    :   reader.py
@Time    :   2020/07/19 18:10:09
@Author  :   HJHCos
@Version :   1.0
@Contact :   3140546263@QQ.com
"""
import os
from time import sleep
from requests import get
from lxml import etree
from config import Config
# import traceback
from re import findall, S


config = Config("config.ini")

USER = config.get()[0]

BD = config.get(USER, 'BD')
BD_ie = config.get(USER, 'BD_ie')
BD_wd = config.get(USER, 'BD_wd') if config.get(USER, 'BD_wd') else "三体"
BD_si = config.get(USER, 'BD_si')
BD_ct = config.get(USER, 'BD_ct')
BD_tn = config.get(USER, 'BD_tn')
BD_oq = config.get(USER, "BD_oq")
BD_cl = config.get(USER, 'BD_cl')
BD_search = BD + config.get(USER, 'BD_s') + 'ie=' + BD_ie
# URL_id = config.get(USER, 'URL_id')
URL_id = 1
CHAP_id = 0


def shuffle(x):
    """shuffle list"""
    if x is not None:
        for i in reversed(range(0, len(x))):
            if i < len(x):
                j = i-1
                x[i], x[j] = x[j], x[i]
            else:
                j = i+1
                x[i], x[j] = x[j], x[i]
        return x
    else:
        raise ValueError("x is none")


def save(content, book_name=None, chapter_name=None):
    """save content

    :param content: string
    :param book_name: book name
    :param chapter_name: chapter name in the book
    """
    if chapter_name:
        book_name = os.path.join(".\\book\\", book_name)
        if not os.path.exists(book_name):
            os.mkdir(book_name)
        if os.path.exists(os.path.join(book_name, chapter_name)):
            raise ValueError("The chapter already exists.")
        chapter_name = os.path.join(book_name, chapter_name + '.txt')
        with open(chapter_name, 'w', encoding='utf-8') as fd:
            for co in content:
                if co:
                    co = str(co + '\n')
                    fd.write(co)
                else:
                    continue
    else:
        file_name = os.path.join(".\\temp", content[:10]+'.txt')
        with open(file_name, 'w', encoding='utf-8') as fd:
            fd.write(content)


def download():
    """download the book by url"""
    global BD_wd
    chapters_link = config.get("USER", "chapters_link")
    chapters_name = config.get("USER", "chapters_name")

    while True:
        try:
            if len(chapters_link) != len(chapters_name):
                raise ValueError("The number of links({}) and chapters({}) is not equal. ".format(
                    len(chapters_link), len(chapters_name)))
            for IDX, name in enumerate(chapters_name):
                name = str(IDX+1) + '.' + name
                save(extractContent(chapters_link[IDX]), BD_wd, name)
                config.revise("USER", "download_id", IDX)
                config.save()
        except Exception as e:
            raise ValueError(f"{__file__}:\n{e}")

        return True


def __shizongzuiContent(html):
    """extract www.shizongzui.cc article.

    :return: Each paragraph's content --> generator
    """

    page_content = html.xpath('/html/body/div[5]')
    page_content = etree.tostring(
        page_content[0], encoding='utf-8').decode('utf-8')
    page_content = findall('>(.*?)<br/>', page_content, S)
    for each_content in page_content:
        yield each_content + "\n"


def __luoxiaContent(html):
    """extract www.luoxia.com article.

        :param url: section's url
        :return: Each paragraph's content --> generator
    """
    page_content = html.xpath('.//div[@id="nr1"]/p')
    for each_content in page_content:
        if each_content.text is not None:
            yield "    " + each_content.text + "\n"
        else:
            continue


def __csw99Content(html):
    """extract www.99csw.com article.

    :param url: section's url
    :return: Each paragraph's content --> generator
    内容进行了打乱  不知道如何获取正确内容
    """
    page_content = html.xpath('/html/body/div[2]/div[2]/div')
    for content in page_content:
        yield "    " + content.text + "\n"


def extractContent(url):
    """extract content in the Chapters

    :param url: section's url --> str
    :param url_id: Ebook site id --> int
    :return: Each paragraph's content --> generator

    co = extractContent('http://www.shizongzui.cc/santi/282.html')

    for c in co:

        print(c)
    """
    try:
        html = getHtml(url)
        html = etree.HTML(html)

        if 'shizongzui.cc' in url:
            return __shizongzuiContent(html)

        elif 'luoxia.com' in url:
            return __luoxiaContent(html)

        elif '99csw.com' in url:
            return __csw99Content(html)

    except Exception as e:
        raise ValueError(f"{__file__}:\n{url}: {e}")


def __shizongzuiChapters(html):
    """extract each chapter‘s name and chapter‘s link in the e-book

    :param html: chapters html
    :return: chapter‘s name chapter‘s link --> list
    """
    html = etree.HTML(html)
    book_span = html.xpath('/html/body/div[6]/span//*')
    chapter_list = list()
    for book_a in book_span:
        chapter_link = book_a.xpath("./@href")[0]
        chapter_name = book_a.text
        chapter_list.append([chapter_name, chapter_link])
    # print(href[0], html_span.text)
    config.add('user', 'chapters_link', [link[1] for link in chapter_list])
    config.add('user', 'chapters_name', [name[0] for name in chapter_list])
    config.save()
    return chapter_list


def __luoxiaChapters(html):
    """extract each chapter‘s name and chapter‘s link in the e-book

    :param html: chapters html
    :return: chapter‘s name chapter‘s link --> list
    """
    html = etree.HTML(html)
    book_div = html.xpath('/html/body/div[2]/div')
    # print(len(cha_div))
    for book_list in book_div:
        if "book-list clearfix" == book_list.xpath('./@class')[0]:
            book_a = book_list.xpath('./ul/li//*')
            chapter_list = []
            for chapter in book_a:
                try:
                    chapter_link = chapter.xpath('./@href')[0]
                except Exception as e:
                    logger.info(e)
                    chapter_link = chapter.xpath('./@onclick')[0]
                    chapter_link = findall(r'.*"(.*?)"', chapter_link, S)[0]
                chapter_name = chapter.text
                chapter_list.append([chapter_name, chapter_link])
            config.add('user', 'chapters_link', [
                       link[1] for link in chapter_list])
            config.add('user', 'chapters_name', [
                       name[0] for name in chapter_list])
            config.save()
            return chapter_list


def __csw99Chapters(html):
    """extract each chapter‘s name and chapter‘s link in the e-book

        :param html: chapters html
        :return: chapter‘s name chapter‘s link --> list
        网站的访问受到限制 访问速度慢 内容打乱
    """
    html = etree.HTML(html)
    book_a = html.xpath("/html/body/div[5]/dl//a")
    chapter_list = []
    for chapter in book_a:
        chapter_name = chapter.text
        chapter_link = "http://99csw.com" + chapter.xpath("./@href")[0]
        chapter_list.append([chapter_name, chapter_link])
    config.add('user', 'chapters_link', [link[1] for link in chapter_list])
    config.add('user', 'chapters_name', [name[0] for name in chapter_list])
    config.save()
    return chapter_list


def extractChapters(url, url_id=1):
    """extract chapters in the e-book url

    :param url_id:
    :param url: e-book url
    :return: chapter and chapter link --> list
    """

    try:
        html = getHtml(url)

        if 'shizongzui.cc' in url or url_id == 0:
            return __shizongzuiChapters(html)

        elif 'luoxia.com' in url or url_id == 1:
            return __luoxiaChapters(html)

        elif '99csw.com' in url or url_id == 2:
            return __csw99Chapters(html)
        else:
            raise ValueError("{} no value in e-book".format(url))

    except Exception as e:
        raise ValueError(f"{__file__}:\n {url}: {e}")


def bdExtractLink(wd=BD_wd, url_id=1, url=BD):
    """baidu extract book sources

    :param url: baidu url
    :param wd:
    :param url_id:
    :return:
    """

    detection = True
    BD_list = ['&wd=' + wd, '&si=' + BD_si[url_id],
               '&ct=' + str(BD_ct), '&tn=' + BD_tn]
    while detection:
        if 'baidu' in url:
            BD_list = shuffle(BD_list)
            if '/link?' not in url:
                url = BD_search
                for bd in BD_list:
                    url += bd
        try:
            html = getHtml(url)
            html = etree.HTML(html)
            # get target link from baidu
            html_data = html.xpath(
                '/html/body/div/div[3]/div[1]/div[4]/div[1]/div[2]/a[1]/@href')
            if html_data[0] is not None:
                detection = False
            if not detection:
                return html_data[0]
        except Exception as e:
            print(e)


def getHtml(url):
    """
    to get page in the url.
    :param url: web page's url --> str
    :return: page's content
    """

    header = {'User-Agent': 'Chrome/84.0.4147.89'}

    # 传说的“七秒效应”
    html = get(url, headers=header, timeout=7)
    sleep(2)   # wait 2s
    html.encoding = 'utf-8'
    return html.text
