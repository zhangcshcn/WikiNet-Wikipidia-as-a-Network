from urllib import urlopen
from bs4 import BeautifulSoup as bs
import os
import sys
import re
import robotparser
import lxml
import shutil
import cPickle as pkl
import threading


def readNode(filename):
    url2idx = {}
    for lines in file(filename):
        line = lines.strip('\n').split(' ')
        url2idx[line[1]] = int(line[0])
    return url2idx


def wikiPageParser(url):
    html_text = file(url).read().decode('utf-8')
    soup = bs(html_text, 'lxml')
    body = bs(soup.find(id="mw-content-text").prettify(), 'lxml')
    links = []
    introflag = 1
    intro = u""
    content = u""
    for tag in body.find_all():
        if introflag == 1 and tag.name == 'div':
            if tag.prettify().find('id="toc"') != -1:
                introflag = 0
        if tag.name == 'p':
            if tag.find('a'):
                links += tag.find_all('a')
            if introflag:
                intro += tag.get_text()
            else:
                content += tag.get_text()
    return links, intro, content



def job(urlList,urlGraph):
    for url in urlList:
        idx = int(url.strip('.html'))
        links, intro, cnt = wikiPageParser(pagepath + '/' + url)
        fp = open("content/%d.txt" % idx, "w")
        fp.write((intro + '\n' + cnt).encode('utf-8'))
        fp.close()
        with wlock:
            urlGraph[idx] = set([url2idx[x.get('href')]
                             for x in filter(lambda x: x.get('href') in url2idx, links)])


if __name__ == '__main__':
    newpath = 'apple_inc'
    pagepath = 'Apple_Inc'
    #newpath = sys.argv[1]
    #pagepath = sys.argv[2]
    os.chdir(newpath)
    if os.path.isdir("content"):
        shutil.rmtree("content")
    os.mkdir("content")
    url2idx = readNode(pagepath + '.stats')
    urlGraph = {}
    urlList = os.listdir(pagepath)
    # print urlList
    urlLen = len(urlList)/4
    urlLists = []
    urlLists.append(urlList[:urlLen])
    urlLists.append(urlList[urlLen:2*urlLen])
    urlLists.append(urlList[2*urlLen:3*urlLen])
    urlLists.append(urlList[3*urlLen:])
    wlock = threading.Lock()
    th = [threading.Thread(target = job, args=(urlLists[i],urlGraph)) for i in range(4)]
    for t in th:
        t.start()
    '''for url in urlList:
        idx = int(url.strip('.html'))
        links, intro, cnt = wikiPageParser(pagepath + '/' + url)
        fp = open("content/%d.txt" % idx, "w")
        fp.write((intro + '\n' + cnt).encode('utf-8'))
        fp.close()
        urlGraph[idx] = set([url2idx[x.get('href')]
                             for x in filter(lambda x: x.get('href') in url2idx, links)])'''
    for t in th:
        t.join()
    idx2url = { url2idx[url]: url for url in url2idx }
    pkl.dump((urlGraph, url2idx, idx2url), file('urlgi.pkl', 'w'))
