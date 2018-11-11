# coding:utf-8
import requests
import urllib2
import re
import json
import os.path
import os
import sys
import pickle
import logging
import agents
import socket
import time
import random
import string


def get_ids(url):
    try:
        result = requests.get(url)
    except Exception as e:
        logging.exception(e)
    if result:

        html = result.content.decode('utf-8')

        title = ''
        id_list = []

        match = re.search(r'var ids = \[([\s\S]*?)\]', html)
        if match:
            id_list = [{'id': id.strip('\t\r\n"')}
                       for id in match.group(1).split(',')]

        match = re.search(r'<div class="name">\s*?<h1>([\s\S]*?)</h1>', html)
        if match:
            title = match.group(1)

        return title, id_list

    return None, []


def get_audio_info(audio_id):
    url = 'http://vdn.apps.cntv.cn/api/getIpadVideoInfo.do?pid=' + audio_id
    try:
        result = requests.get(url)
    except Exception as e:
        logging.exception(e)
    if result:
        match = re.search(r'var html5VideoData\s*=\s*\'([\s\S]*)\';',
                          result.content)
        if match:
            info = json.loads(match.group(1).decode(result.encoding))
            temp_title = info.get('title', '')
            temp_title = string.replace(temp_title, '\\', '-')
            temp_title = string.replace(temp_title, '/', '-')

            while temp_title[-1] == ' ':
                temp_title = temp_title[:-1]
            rv = {
                'title': temp_title,
                'url': info.get('video', {}).get('chapters', [{}])[0].get('url')
            }

            return rv


def download_audios(url, directory='.'):
    album_title, id_list = get_ids(url)
    if album_title is None:
        print(u'无法获取到该专辑的信息')
    else:
        print(u'专辑：%s(%d)' % (album_title, len(id_list)) )

        base_dir = os.path.join(directory, album_title)
        pickle_path = os.path.join(base_dir, 'pickle.dat')
        try:
            album_title, id_list = pickle.load(open(pickle_path, 'rb'))
        except:
            pass

        try:
            os.mkdir(base_dir)
        except OSError:
            pass

        for info in id_list:
            if info.get('title') is None:
                info.update(get_audio_info(info.get('id')))
            if info.get('complete'):
                print(u'　【已完成】' + info['title'])
                continue
            else:
                print(u'　正在下载：' + info['title'])
            save_path = os.path.join(base_dir, info['title'] + '.mp3')

            failed_limit = 100
            failed_times = failed_limit
            delay_time = 2
            while failed_times > 0:
                try:
                    request = urllib2.Request(info['url'], headers={
                        'User-Agent': agents.get_only_agent(),
                        'X-Requested-With': 'ShockwaveFlash/21.0.0.242',
                        'Connection': 'keep-alive',
                        'Referer': url
                    })
                    data = urllib2.urlopen(request, timeout=1000000)
                    audio_data = data.read()
                    '''
                    audio_data = requests.get(info['url'], headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)',
                        'X-Requested-With': 'ShockwaveFlash/21.0.0.242',
                        'Connection': 'keep-alive',
                        'Referer': url
                    }).content
                    '''
                    with open(save_path, 'wb') as f:
                        f.write(audio_data)
                    info['complete'] = True
                    print(u'【成功】')
                    break
                except urllib2.HTTPError as e:
                    if hasattr(e, 'code'):
                        print('错误状态码是' + str(e.code))
                        if e.code == 403:
                            delay_time = delay_time + 2
                            time.sleep(1 + random.random() * delay_time)
                except urllib2.URLError as e:
                    if hasattr(e, 'reason'):
                        # print('url 为 %', urlStr)
                        print('错误原因是' + str(e.reason))
                except socket.timeout:
                    print('socket超时')
                except OSError as e:
                    logging.exception(e)
                except ValueError as e:
                    logging.exception(e)
                except Exception as e:
                    logging.exception(e)
                finally:
                    failed_times -= 1
            if failed_times == 0:
                print(u'【失败】')

            pickle.dump((album_title, id_list), open(pickle_path, 'wb'))


if __name__ == '__main__':
    download_audios(sys.argv[1])
    # download_audios('http://ncpa-classic.cntv.cn/2013/07/16/VIDA1373960896399814.shtml')
