A tool to find sql injections by baidu search engine and sqlmapapi
====

###Usage:

####0x00、change the current the directory to sqlmap's directory,run the commod in console<br>
```Bash
python sqlmapapi.py -s -H localhost
```
####    the sqlmapapi.py will listens the localhost's port 8775 and receives the requests from client to start a task<br>
####0x01、run the spider_baidu.py with the `Idle` or other `Python Interpreter` you like<br>
####0x02、input the baidu dork what you want to search(eg:inurl:"show.php?id")<br>
####0x03、input the thread numbers what you want to use<br>
####0x04、input the page numbers what you want to search<br>
####0x05、when the spider finished its jobs,it will ask you whether you want to check sql injection vulns by the sqlmapapi<br>
if you want to check,enter `Y` or enter `N` not to check vulns
####0x06、when script find a sql injection,it will log it in `successSqli.txt` or log failed info in `failedSqli.txt` when a url is not vunerable.


###使用方法:

####0x00、切换到sqlmap的目录下，在终端运行下面的命令<br>
```Bash
python sqlmapapi.py -s -H localhost
```
####    sqlmapapi.py 会监听本地localhost的8775端口，同时接受来自客户端的请求去开启一个任务<br>
####0x01、使用`Idle`或者其他你喜欢的`Python解释器`来运行spider_baidu.py<br>
####0x02、输入你想搜索的baidu dork（如:inurl:"show.php?id"）<br>
####0x03、输入你想要使用的线程数<br>
####0x04、输入你想要爬取的百度搜索结果的页数<br>
####0x05、当爬虫结束的时候，它会询问你是否通过sqlmapapi去检测sql注入漏洞。<br>
如果你想去检测的话，输入`Y`或者输入`N`不去检测漏洞
####0x06、当脚本发现一个sql注入漏洞的时候，它会把它记录在 `successSqli.txt` 或者把不存在注入漏洞的失败信息记录在`failedSqli.txt` <br>
