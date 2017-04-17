from urllib import urlopen
from bs4 import BeautifulSoup as bs
import os
import sys
import re
import robotparser
import lxml
import shutil
#import threading

prefix = r"https://en.wikipedia.org"


def extractToken(url):
    ### Given a wikipedia internal reference link, 
    ### return a word sequence of the title of the page 
    ### in lower case. 
    text_of_interest = url[6:].replace("_", " ").lower()
    next_token = re.findall('^[^(]+', text_of_interest, re.UNICODE)
    return next_token[0].strip()


def heuristicLinkParser(reladdr, parent):
    ### reladdr: /wiki/***
    ### parent: the url of the parent page 
    ### each refernce to the parent page counts 3, each appearence of the parent seq counts 1

    # print reladdr, parent
    html_text = urlopen(prefix + reladdr).read().decode('utf-8')
    soup = bs(html_text, 'lxml')
    body = bs(soup.find(id="mw-content-text").prettify(), 'lxml')
    #links = body.find_all('a')

    ### Back check the page's relation with its parent.
    if parent != "":
        cot = body.get_text().lower()
        score = cot.count(parent.lower()) * 3 + cot.count(extractToken(parent)) 
        if score < 3:
            return 0, [], ""
    links = []
    introflag = 1
    intro = u""
    content = u""
    words = {}
    ### Heuristically choose relavent urls.
    ### Only the urls in <p></p> are taken into consideration.
    ### For urls whose anchor appear in the introduction, each appearence weighs 3
    ### For urls whose anchor appear in the content, each appearence weighs 1
    ### Urls (determined by anchor text instead of by url) which weigh less than
    ### 2 are excluded.
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
    linkd = {}
    for link in links:
        score = 0
        anc = link.get_text().strip()
        if link.get('href'):
            linkd[link.get('href')] = [intro.count(
                anc) * 3 + content.count(anc), anc]
    # print len(linkd),linkd
    for link in linkd.keys():
        # print link

        ### exclude urls that
        ### 1. weigh insufficiently
        ### 2. go outside of wikipedia
        ### 3. refer to pages introducing wikipedia files
        if linkd[link][0] <= 2 or not link.startswith("/wiki/") or link.startswith("/wiki/File:"):
            linkd.pop(link)
            continue
        if link.find("#") != -1:
            linkd[link[:link.find("#")]] = linkd.pop(link)
    '''for link in linkd:
        print link'''
    return score, linkd.keys(), html_text

if __name__ == '__main__':
    # seed = "/wiki/Apple_Inc"
    # maxDepth = 5
    seed = sys.argv[1]
    maxDepth = int(sys.argv[2])
    abspath = seed[6:]
    if (os.path.isdir(abspath)):
        shutil.rmtree(abspath)
    os.mkdir(abspath)
    os.chdir(abspath)
    urlList = [seed]
    urlHash = {seed: [0, "", 0]}
    idx = 1
    urlNum = 0
    while urlList:
        url = urlList.pop(0)
        if urlHash[url][2] < maxDepth:
            s, child, html_text = heuristicLinkParser(url, urlHash[url][1])
            # print s, child
            if s == 0 and child == []:
                # print url, urlLen
                urlHash.pop(url)
                urlNum -= 1
            else:
                # print url, urlHash[url]
                fp = open("%d.html" % urlHash[url][0], "w")
                fp.write(html_text.encode("utf-8"))
                fp.close()
                for ch in child:
                    if ch not in urlHash:
                        urlHash[ch] = [idx, url, urlHash[url][2] + 1]
                        idx += 1
                        urlNum += 1
                        urlList.append(ch)
        else:
            s, child, html_text = heuristicLinkParser(url, urlHash[url][1])
            # print s, child
            if s == 0 and child == []:
                # print url, urlLen
                urlHash.pop(url)
                urlNum -= 1
            else:
                fp = open("%d.html" % urlHash[url][0], "w")
                fp.write(html_text.encode("utf-8"))
                fp.close()
    urlHashList = list(zip(urlHash.values(), urlHash.keys()))
    urlHashList.sort()
    os.chdir("..")
    fp = open(abspath+".stats","w")
    for stats, url in urlHashList:
        fp.write( "%d %s %s %d\n"%(stats[0], url, stats[1], stats[2]) )
    fp.close()
    '''for url in urlHash:
        print url, urlHash[url]'''
