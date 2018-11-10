from __future__ import division
import requests
import agents
import theater
import re
import multiprocessing
import threading
import os
import urllib2
import urllib
import logging


total_url_nums = 0
finished_num = 0


def get_quote_url(url):
    new_url = urllib.quote(url, '')
    re_patten = r'(.*)\.(html|htm|shtml)'
    m = re.search(re_patten, new_url)
    if m:
        url_str = m.group(1)
    else:
        url_str = new_url
    return url_str


def handle_batch(urls):
    global finished_num
    global total_url_nums
    for each_url in urls:
        new_url = get_quote_url(each_url)
        new_hash_path = './hash/' + new_url
        if not os.path.exists(new_hash_path):
            with open(new_hash_path, 'w') as out_f:
                out_f.write(' ')
            theater.download_audios(each_url, './music')
            lock = threading.Lock()
            lock.acquire()
            finished_num = finished_num + 1
            print("-- Finish downloads %d albums, %.2f%% of total\n" %(finished_num, finished_num/total_url_nums * 100))
            lock.release()
        else:
            lock = threading.Lock()
            lock.acquire()
            finished_num = finished_num + 1
            lock.release()


def get_album_urls():
    global total_url_nums
    index_url = "http://ncpa-classic.cntv.cn/gdyysx/1/index.shtml"
    try:
        request = urllib2.Request(index_url, headers=agents.get_user_agent())
        page = urllib2.urlopen(request, timeout=10)
    except Exception as e:
        logging.exception(e)
    pattern = r'<li\s+[^>]+>\s*<div\s+class[^>]+>\s*<a\s+href="([^"]+)"\s*[^>]*>'
    # thread_num = multiprocessing.cpu_count()
    thread_num = 4
    if not os.path.exists('./music'):
        os.mkdir('./music')
    if not os.path.exists('./hash'):
        os.mkdir('./hash')
    if page:
        page_content = page.read().decode('utf-8')
        match = re.findall(pattern, page_content)
        if match:
            total_num = len(match)
            # thread_num = total_num
            total_url_nums = total_num
            batch_size = total_num // thread_num
            thread_queue = []
            for i in range(thread_num):
                if i < thread_num - 1:
                    url_batch = match[i * batch_size: (i+1) * batch_size]
                else:
                    url_batch = match[i * batch_size: batch_size]
                t = threading.Thread(target=handle_batch, args=(url_batch, ), name='thread' + str(i))
                thread_queue.append(t)
            for thread in thread_queue:
                thread.start()
            for thread in thread_queue:
                thread.join()


def main():
    get_album_urls()


if __name__ == '__main__':
    get_album_urls()
