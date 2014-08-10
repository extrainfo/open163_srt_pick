#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os
import shutil
import urllib
from bs4 import BeautifulSoup

def pick_srt(url):
    piece_url = url.split("/")
    piece_url[-1] = "2_" + piece_url[-1].split(".")[0] + ".xml"
    xml_url = "http://live.ws.126.net/movie/" + '/'.join(piece_url[-3:])
    xml_content = urllib.urlopen(xml_url).read()
    soup = BeautifulSoup(xml_content)
    title = soup.title.string
    srt_url = soup.find_all('url')
    try:
        zh_srt = srt_url[0].string
        en_srt = srt_url[1].string
    except:
        print "can't pick %s" % xml_url
        return False
    return title, zh_srt, en_srt

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
    shutil.move(zh_dist, dir_name)
    shutil.move(en_dist, dir_name)

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
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

def main():
    argv = sys.argv
    if len(argv) < 2:
        print "Usage: python open163_srt_pick.py [url]"
        sys.exit()

    url = argv[1]
    title, zh_srt, en_srt = pick_srt(url)
    number = get_number(url)
    dir_name = title + number
    print dir_name
    print zh_srt
    print en_srt
    if query_download("Download?"):
        down_srt(dir_name, zh_srt, en_srt, number)
        print "Done"

if __name__ == "__main__":
    main()
