#coding=utf-8
__author__ = '3ky7in4'

'''
1、首先根据关键词，进行一次百度dork
====》获取dork的页码与链接的url组成的元祖
    根据正则表达式打印出当前页面找到的最大页码
2、等待用户输入搜索的页数
    再次发出请求，根据最大页数。循环搜索请求，同时更新最大页码数。

'''

import urllib,urllib2,cookielib,re,math,time,urlparse
from corelib import baidu_sqlmap
from threading import Thread,Lock
from Queue import Queue
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
}
lock = Lock()

class HttpRequestThread(Thread):
    def __init__(self,index,opener,urlqueues,urls):
        Thread.__init__(self)
        self.opener = opener
        self.urlqueues = urlqueues
        self.name = 'Thread'+str(index)
        self.urls = urls
        self.headers = headers

    def run(self):
        global lock
        while True:
            item = self.urlqueues.get()
            if str(item) == 'end':
                self.urlqueues.put('end')
                with lock:
                    print("%s done..." % self.name)
                break
            response = self.makerequest(item)
            if not response:
                continue
            else:
                url = response.url
                with lock:
                    if url not in self.urls:
                        self.urls.append(url)
            self.urlqueues.task_done()

    def makerequest(self,url):
        # if not self.headers.has_key('Referer'):
        #     self.headers['Referer'] = url
        req = urllib2.Request(url,headers=self.headers)
        try: 
            response = self.opener.open(req,timeout=5)
            return response
        except Exception,e:
            print url,':',e
            return None

class BaiDu:
    def __init__(self,headers,debug=False):
        self.host = 'https://www.baidu.com/%s'
        self.headers = headers
        self.cookiehandler = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        self.threads = []
        self.links = Queue()
        self.urls = []
        self.html = ''
        self.pagelinks = {}
        if debug:
            httphandler = urllib2.HTTPHandler(debuglevel=1)
            self.opener = urllib2.build_opener(httphandler,self.cookiehandler)
        else:
            self.opener = urllib2.build_opener(self.cookiehandler)


    def fetchContents(self,host=None,word='',pagenum=1):
        if host == None:
            host = self.host
        #第一次访问，获取页码。
        if self.html == '' and pagenum == 1:
            #step1.构造url请求参数,wd对应为搜索的关键词
            self.word = 's?wd=%s' % urllib2.quote(word)
            url = self.host % (self.word)
            #step2.对构造好的url，发出请求，讲返回的页面存储在self.html
            req = urllib2.Request(url,headers=self.headers)
            response = self.opener.open(req)
            self.html = response.read()
            #step3.使用正则表达式匹配数据
            self.getBaidulinks()
        #第二次访问，根据用户输入的页码进行搜索
        if pagenum>1:
            time.sleep(1)
            for i in xrange(2,pagenum+1):
                #页码的的数值计算方式为(pagenum-1)*10,参数名为pn
                self.word = 's?wd=%s&pn=%d' % (urllib2.quote(word),(i-1)*10)
                url = self.host % (self.word)
                req = urllib2.Request(url,headers=self.headers)
                response = self.opener.open(req)
                #Improve it,这里可以使用列表来存储每一页的结果。
                #Think about it,这样代码是整洁了？但是效率会提高吗？
                self.html = response.read()
                self.getBaidulinks()
        if self.links.qsize()>0:
            self.links.put('end')
            return list(self.links.queue)
        else:
            return None

    def getPageNums(self):
        getnum_pattern = r'<span class="pc">(.*?)<'
        l = re.findall(getnum_pattern,self.html,re.S|re.I)
        if len(l)>0:
            self.pagenum = max([int(i) for i in l ])


    def getBaidulinks(self):
        if self.html == '':
            self.fetchContents(word=self.word,pagenum=1)
            return
        #获取百度搜索结果的中转url，一页一页的获取
        pattern = r'<h3 class="t".*?<a.*?href = "(.*?)".*?target='
        l = re.findall(pattern,self.html,re.S|re.I)
        for item in l:
            if item not in list(self.links.queue):
                self.links.put(item)
        self.getPageNums()

    def getUrls(self,threadsnum=5):
        #根据中转url获取真实的网站url
        if self.links.qsize()>0:
            for i in range(1,threadsnum+1):
                t = HttpRequestThread(i,self.opener,self.links,self.urls)
                t.start()
                self.threads.append(t)
            for t in self.threads:
                t.join()
            self.handleUrls()
            return self.urls
        else:
            return None

    def handleUrls(self):
        paths = {}
        urls = {}
        if len(self.urls)>0:
            for url in self.urls:
                parses = urlparse.urlparse(url)
                if not paths.has_key(parses.netloc):
                    #这里把路径作为键值，fix me
                    paths[parses.netloc] = [parses.path]
                    urls[parses.netloc] = [url]
                else:
                    if parses.path not in paths[parses.netloc]:
                        paths[parses.netloc].append(parses.path)
                        urls[parses.netloc].append(url)
                    else:
                        continue
        self.handleurls = urls

    def printUrls(self):
        for index,item in zip(range(1,len(self.urls)+1),self.urls):
            print "%d %s" % (index,item)
            for url in self.urls[item]:
                print "\t%s" % (url)

    def makeRequest(self,url):
        if not self.headers.has_key('Referer'):
            self.headers['Referer'] = url
        req = urllib2.Request(url,headers=self.headers)
        try: 
            response = self.opener.open(req)
            return response
        except urllib2.URLError,e:
            print url,':',e
            return None

    def printHosts(self):
        for host in self.handleurls.iterkeys():
            print host
            for index,value in enumerate(self.handleurls[host]):
                print (index+1),"\t",value


    def saveOutputInFile(self,urlsfilename='urls.txt',hostsfilename='hosts.txt'):
        with open(urlsfilename,'w') as f:
            for host in self.handleurls.iterkeys():
                for url in self.handleurls[host]:
                    f.write(url+"\n")
        with open(hostsfilename,'w') as f:
            for host in self.handleurls.iterkeys():
                f.write('http://'+host+"\n")

def main():
    urllists = []
    baidu = BaiDu(headers,debug=False)
    #keyword = 'inurl:"view.php?"'
    keyword = raw_input("请输入你的百度dork:")
    threadsnum = raw_input("请输入爬虫的线程数:")
    links = baidu.fetchContents(word=keyword)
    if links == None:
        return
    if len(links)>0:
        starttime = time.time()
        if hasattr(baidu,'pagenum'):
            pagenum = raw_input(("百度当前一共有%d页搜索结果,输入你想要搜索的页数:" % (baidu.pagenum)))
            baidu.fetchContents(word=keyword,pagenum=int(pagenum))
        else:
            baidu.fetchContents(word=keyword,pagenum=1)
        urls = baidu.getUrls(int(threadsnum))
        baidu.printHosts()
        baidu.saveOutputInFile()
    endtime = time.time()
    print '查询结束，一共耗费了%f秒' % ((endtime-starttime))
    checkSqli = raw_input('是否需要对带有参数的链接进行sql注入检测(Y/N):')
    if checkSqli and checkSqli.lower()=='y':
        for host in baidu.handleurls.iterkeys():
            for url in baidu.handleurls[host]:
                parses = urlparse.urlparse(url)
                if parses.query:
                    if url not in urllists:
                        urllists.append(url)
        if len(urllists) == 0:
            print('not avaiable url')
            return
        baidu_sqlmap.checkInjection(urllists)
    else:
        exit()


if __name__ == '__main__':
    main()

