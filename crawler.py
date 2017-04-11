#from html.parser import HTMLParser  
from HTMLParser import HTMLParser  
from urllib import urlopen  
from urlparse import urljoin
from url_normalize import url_normalize
from bs4 import BeautifulSoup
import os, sys, re, robotparser


# We are going to create a class called LinkParser that inherits some
# methods from HTMLParser which is why it is passed into the definition
class LinkParser(HTMLParser):
    # This is a function that HTMLParser normally has
    # but we are adding some functionality to it
    def handle_starttag(self, tag, attrs):
        # We are looking for the begining of a link. Links normally look
        # like <a href="www.someurl.com"></a>
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    # We are grabbing the new URL. We are also adding the
                    # base URL to it. For example:
                    # www.netinstructions.com is the base and
                    # somepage.html is the new URL (a relative URL)
                    #
                    # We combine a relative URL with the base URL to create
                    # an absolute URL like:
                    # www.netinstructions.com/somepage.html
                    newUrl = url_normalize(urljoin(self.baseUrl, value))
                    # And add it to our colection of links:
                    self.links = self.links + [newUrl]

    # This is a new function that we are creating to get links
    # that our spider() function will call
    def getLinks(self, url):
        url = url_normalize(url)
        
        self.links = []
        # Remember the base URL which will be important when creating
        # absolute URLs
        self.baseUrl = url
        # Use the urlopen function from the standard Python 3 library
        response = urlopen(url)
        head = response.info()
        isUrl = head.gettype().startswith('text/html')
        # print(isUrl)
        # Make sure that we are looking at HTML and not other things that
        # are floating around on the internet (such as
        # JavaScript files, CSS, or .PDFs for example)
        if isUrl:
            htmlBytes = response.read()
            # Note that feed() handles Strings well, but not bytes
            # (A change from Python 2.x to Python 3.x)
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            return htmlString, self.links
        else:
            return "",[]
def getCTitle(soup):
    if soup.title:
        return soup.title.get_text().encode("utf-8")
    elif soup.h1:
        return soup.h1.get_text().encode("utf-8")
    elif soup.h2:
        return soup.h2.get_text().encode("utf-8")
    elif soup.h3:
        return soup.h3.get_text().encode("utf-8")
    else:
        tokens = re.findall("\w+",soup.body.get_text().encode("utf-8"))
        upper = len(tokens)
        upper = 3 if upper > 3 else upper
        tokens = tokens[:upper]
        ret = ""
        for t in tokens:
            ret += t+" "
        return ret

def truncateUrl(url):
    if url.startswith("https://"):
        url = url[8:]
    if url.startswith("http://"):
        url = url[7:]
    if url.find('?') > 0:
        url = url[0:url.find('?')]
    if url.find('#') > 0:
        url = url[0:url.find('#')]
    if url[-1] == '/':
        url = url[:-1]
    if url.endswith('/index.html'):
        url = url[:-11]
    return url
        
# And finally here is our spider. It takes in an URL, a word to find,
# and the number of pages to search through before giving up
def spider(url, maxPages, domain):  
    urlVisited = {}
    fHash = {}
    pagesToVisit = [url]
    numberVisited = 0
    urlVisited[truncateUrl(url)] = numberVisited
    # The main loop. Create a LinkParser and get all the links on the page.
    # Also search the page for the word or string
    # In our getLinks function we return the web page
    # (this is useful for searching for the word)
    # and we return a set of links from that web page
    # (this is useful for where to go next)

    rp = robotparser.RobotFileParser()
    roboturl = url_normalize(domain)+'/robots.txt'
    rp.set_url(roboturl)
    rp.read()
    while numberVisited < maxPages and pagesToVisit != []:
        
        # Start from the beginning of our collection of pages to visit:
        url = pagesToVisit.pop(0)
        # print "res: ",rp.can_fetch("*",url)
        if rp.can_fetch("*",url):
            # print(numberVisited, "Visiting:", url)
            parser = LinkParser()
            data, links = parser.getLinks(url)
            # print url
            # print "page downloaded"
            soup = BeautifulSoup(data,'lxml')
            ctitle = getCTitle(soup)
            cbody = soup.body.get_text().encode('utf-8')
            soup()
            # print os.getcwd()
            fp = open("cache/%d"%numberVisited,"w")
            fp.write(soup.body.get_text().encode('utf-8'))
            fp.close()
            # print "page cached"
            fHash[numberVisited] = (url,ctitle)
            # print numberVisited, url, ctitle
            # Add the pages that we visited to the end of our collection
            # of pages to visit:
            for l in links:
                tl = truncateUrl(l)
                if tl not in urlVisited:
                    pagesToVisit.append(l)
                    urlVisited[tl] = numberVisited
            numberVisited = numberVisited +1
            # print(" **Success!**")
    # print fHash
    return fHash
        
if __name__=="__main__":
    spider(sys.argv[1],20)

