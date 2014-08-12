#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os
import shutil
import urllib
from bs4 import BeautifulSoup

def all_course_url(url):
    content = urllib.urlopen(url).read()
    course_list = re.findall('http://v.163.com/movie/.*?html', content)
    return list(set(course_list))

def pick_srt(url):
    piece_url = url.split("/")
    piece_url[-1] = "2_" + piece_url[-1].split(".")[0] + ".xml"
    xml_url = "http://live.ws.126.net/movie/" + '/'.join(piece_url[-3:])
    xml_content = urllib.urlopen(xml_url).read()
    soup = BeautifulSoup(xml_content)
    title = soup.title.string
    srt_url = soup.find_all('url')
    number = get_number(url)
    try:
        zh_srt = srt_url[0].string
        en_srt = srt_url[1].string
    except:
        print "[-] can't pick %s\n%s" % (number, xml_url)
        return False
    return number, title, zh_srt, en_srt

def get_number(url):
    content = urllib.urlopen(url)
    soup = BeautifulSoup(content)
    number_regex = re.compile('\[(.+\d+.+)\]')
    for i in soup.find(id="j-playlist-container").div.children:
        tag = str(i)
        if 'positem' in tag:
            return number_regex.search(tag).group(1).decode('utf-8')

def down_srt(dir_name, zh_srt, en_srt, number):
    zh_dist = number + '_zh.srt'
    en_dist = number + '_en.srt'
    urllib.urlretrieve(zh_srt, zh_dist)
    urllib.urlretrieve(en_srt, en_dist)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    try:
        shutil.move(zh_dist, dir_name)
        shutil.move(en_dist, dir_name)
    except:
        print "[-] srt exits"
        os.remove(zh_dist)
        os.remove(en_dist)

def query_download(question, default="no"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("[*] Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

def check_url(url):
    if 'special/opencourse' in url:
        return True
    else:
        return False

def process(urls):
    number, title, dir_name, zh_srt, en_srt = info(urls[0])
    if len(urls) == 1:
        print dir_name
        print zh_srt
        print en_srt
        if query_download("Download %s?" % dir_name):
            down_srt(dir_name, zh_srt, en_srt, number)
            print "[*] Done %s!" % dir_name
    else:
        print title
        if query_download("Download All %s?" % title):
            for url in urls:
                if info(url):
                    number, title, dir_name, zh_srt, en_srt = info(url)
                    down_srt(title, zh_srt, en_srt, number)
                    print "[*] Done %s!" % number

def info(url):
    if pick_srt(url):
        number, title, zh_srt, en_srt = pick_srt(url)
        dir_name = title + number
        return number, title, dir_name, zh_srt, en_srt
    return False

def main():
    argv = sys.argv
    if len(argv) < 2:
        print "Usage: python open163_srt_pick.py [url]"
        sys.exit()

    url = argv[1]
    urls = []
    if check_url(url):
        urls = all_course_url(url)
    else:
        urls.append(url)
    process(urls)


if __name__ == "__main__":
    main()
