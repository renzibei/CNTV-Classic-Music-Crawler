# Description
这是一个用来爬取 [CNTV国家大剧院音乐频道](http://www.ncpa-classic.com/) 上面的音乐专辑的爬虫

# Requirements
* Python2.7 64bits (version above 3 not been tested)
* requests library

# Usage
爬下古典音乐全站 `python ncpa_spider.py`

爬特定歌曲页面 `theater.py url`

# Example
```shell
python ncpa_spider.py
# 这个代码会把http://ncpa-classic.cntv.cn/gdyysx/1/index.shtml古典音乐内的所有音乐都下载下来，储存在music文件夹中

theater.py http://ncpa-classic.cntv.cn/2013/07/16/VIDA1373960896399814.shtml  
# 这样的代码会在运行目录下产生一个文件夹，文件夹的名字为专辑的名字。
# 在该文件夹下保存该专辑所有的音乐(码率：192Kbps)
# 并且还有一个pickle.dat文件用来存储断点续传的信息，该文件可以删除
```

# Remark
CNTV会对过于频繁的ip封禁，且封国外ip,线程数不要开得太高

