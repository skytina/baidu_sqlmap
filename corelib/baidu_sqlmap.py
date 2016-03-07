#coding=utf-8

import requests
import json
import time
import sys
from sys import exit
from os import path

options = {
	"level"		   : 1,
    "randomAgent"  : True,
    "getBanner" : True ,
    "checkWaf"    : True ,
    "verbose"    : 3 ,
    "batch"        : True,
    "answer"    : "extending=N,follow=N,keep=N,exploit=n",
    "retries"	: 1,
    "batch"		: True,
    "timeout"	: 5
}

headers = { "Content-Type":"application/json"}

class SQLiInterface():
    def __init__(self,localserver='http://localhost:8775'):
        global options,headers
        self.options = options
        self.headers = headers
        self.localserver = localserver[:-1] if (localserver.endswith('/')) else localserver

    def createTask(self):
        url = '%s/task/new' % (self.localserver)
        req = requests.get(url,headers=self.headers)
        if req:
            self.taskid = json.loads(req.text)["taskid"]
            if not self.taskid:
                return False
            else:
                return True
        else:
            return False

    def stopScan(self):
        url = '%s/scan/%s/stop' % (self.localserver,self.taskid)
        req = requests.get(url,headers=self.headers)
        if req:
            status = json.loads(req.text)["success"]
            return status
        else:
            return False

    def deleteTask(self):
        url = '%s/task/%s/delete' % (self.localserver,self.taskid)
        req = requests.get(url,headers=self.headers)
        if req:
            status = json.loads(req.text)["success"]
            return status
        else:
            return False

    def setTaskOptions(self,conf=None):
        conf = self.options if not options else options
        if self.taskid:
            url = '%s/option/%s/set' % (self.localserver,self.taskid)
            req = requests.post(url,data=json.dumps(conf),headers=self.headers)
            if req:
                return json.loads(req.text)["success"]
            else:
                return False
        else:
            return False

    def startSqli(self,url=''):
        self.options["url"] = url
        scanurl = '%s/scan/%s/start' % (self.localserver,self.taskid)
        #print(scanurl)
        try:
            #print(json.dumps(conf))
            self.setTaskOptions()
            req = requests.post(scanurl,data=json.dumps({}),headers=self.headers)
            if json.loads(req.text)["success"]:
                return True
            else:
                return False
        except Exception,e:
            self.logInFile(str(e))
            exit()

    def getData(self):
        url = '%s/scan/%s/data' % (self.localserver,self.taskid)
        try:
            req = requests.get(url)
            if req:
                return json.loads(req.text)
            else:
                return False
        except Exception,e:
            self.logInFile(str(e))
            exit()

    def getLog(self):
        url = '%s/scan/%s/log' % (self.localserver,self.taskid)
        try:
            req = requests.get(url)
            if req:
                return req.text
            else:
                return False
        except Exception,e:
            self.logInFile(str(e))
            exit()


    def getStatus(self):
        url = '%s/scan/%s/status' % (self.localserver,self.taskid)
        try:
            req = requests.get(url)
            if req:
                return json.loads(req.text)["status"]
            else:
                return False
        except Exception,e:
            self.logInFile(str(e))
            exit()
    def logInFile(self,content=''):
        pass

    def outputScreen(self,level="Info",message=""):
        print("[%s]\t%s" % (level,message))



errorFileName = 'failedSqli.txt'
successFileName = 'successSqli.txt'


def checkInjection(urllists):
    if not urllists:
        print("No avaiable url to check sqli")
        return
    sqli = SQLiInterface()
    for url in urllists:
        if sqli.createTask():
            if sqli.startSqli(url=url):
                sqli.outputScreen(level="Info",message="%s test starts" % (url))
                starttime = time.time()
                while True:
                    if time.time()-starttime>(60*10):
                        print('[%s] 花费时间过长，已经超过10分钟，终止对该url的测试' % url)
                        sqli.stopScan()
                        break
                    status = sqli.getStatus()
                    if status == 'terminated':
                        results = sqli.getData()
                        if len(results["data"])>0 and not results["error"]:
                            sqli.outputScreen(level='success',message='%s is vunerable' % (url))
                            with open(successFileName,'a+') as successf:
                                successf.write(json.dumps(sqli.getData())+'\n')
                        else:
                            sqli.outputScreen(level='failed',message='url is not vunerable')
                            with open(errorFileName,'a+') as errf:
                                errf.write(sqli.getLog())
                            #print(sqli.getLog())
                        break
                    elif status == 'running':
                        #print(sqli.getLog())
                        time.sleep(3)
                    else:
                        sqli.outputScreen(level='exception',message='error occurs!')
                        break
                if sqli.deleteTask():
                    sqli.outputScreen(message="%s test end,it cost %.2f seconds" % (url,time.time()-starttime))
            else:
                print('could not start sqli')
        else:
            print('Create Task failed!')

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('Usage: python baidu_sqlmap.py urls.txt')
	else:
		if path.isfile(sys.argv[1]):
			urllists = []
			with open(sys.argv[1],'r') as urlsf:
				for url in urlsf:
					if url not in urllists:
						urllists.append(url.strip())
			checkInjection(urllists)