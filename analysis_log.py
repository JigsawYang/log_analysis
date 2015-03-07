#!/usr/bin python
#coding:utf-8
import sys, os, time
import hashlib
import requests
import re


def extract_data(ck_dict, url_dict, path):
    fp = open(path, 'r')
    try:
        while 1:
            line = next(fp)
            log_list = line.split('|')
            list_len = len(log_list)
            if(list_len != 9):
                continue
            ck = log_list[0]
            url = log_list[4]
            urlmd5 = hashlib.md5(url.encode("utf8")).hexdigest()
            if(ck not in ck_dict):
                ck_dict[ck] = [1, {url : 1}]
            else:
                if(url not in ck_dict[ck][1]):
                    ck_dict[ck][0] += 1
                    ck_dict[ck][1].update({url : 1})
                else:
                    ck_dict[ck][0] += 1
                    ck_dict[ck][1][url] += 1
            if(urlmd5 not in url_dict):
                url_dict[urlmd5] = [url, {ck : 1}, 1]
            else:
                if(ck not in url_dict[urlmd5][1]):
                    url_dict[urlmd5][1].update({ck : 1})
                    url_dict[urlmd5][2] += 1
                else:
                    url_dict[urlmd5][1][ck] += 1
                    url_dict[urlmd5][2] += 1
    except StopIteration:
        fp.close()

def sort_ck(ck_dict):
    return sorted(ck_dict.items(), key = lambda e:e[1][0], reverse = True)

def sort_url(url_dict):
    return sorted(url_dict.items(), key = lambda e:e[1][2], reverse = True)

def pt_ck(dt):
    count = 0
    for temp in dt:
        # print(temp)
        if(count > 4):
            break
        print(str(temp[1][0]) + '\t' + temp[0])
        inner = sorted(temp[1][1].items(), key = lambda e:e[1], reverse=True)
        inner_count = 0
        for tmp in inner:
            if(inner_count > 3):
                break
            print(str(tmp[1]) + '\t' + tmp[0])
            inner_count += 1
        print('\n')
        count += 1

def pt_url(dt):
    count = 0
    for temp in dt:
        if(count > 3):
            break
        print(temp[1][0])
        inner = sorted(temp[1][1].items(), key = lambda e:e[1], reverse=True)
        inner_count = 0
        for tmp in inner:
            if(inner_count > 3):
                break
            print(str(tmp[1]) + '\t' + tmp[0])
            inner_count += 1
        print('\n')
        count += 1

def top(list_url):
    """Get top 100 url into a list"""
    count = 0
    top_url = []
    for i in list_url:
        if(count > 100):
            break
        top_url.append(i[1][0])
        count += 1
    return top_url

def dump_parse(url):
    """dump page and judge js and get title"""
    js_flag = 0
    title = ""
    bad = 0
    pat_script = re.compile(""".*?(<script.*?src=[\"\'].*?[\"\'].*?>).*""") 
    pat_title = re.compile(""".*?<title>(.*?)</title>.*""", re.S)
    try:
        r = requests.get(url, timeout = 2)
        r.raise_for_status()
    except requests.RequestException as e:
        print(e)
        bad += 1
        return bad
    else:        
        web_b = r.content.decode('utf-8', 'ignore')
        pos1 = web_b.find('<head>')
        pos2 = web_b.find('</head>')
        head = web_b[pos1:pos2]
        js = pat_script.search(head)
        if js is not None:
            js_flag = 1
        try:
            c_type = r.headers['content-type']
        except KeyError as e:
            c_type = "无"
        t_flag = pat_title.search(head)
        if t_flag is not None:
            title = t_flag.group(1)
        print(url + '\t' + c_type + '\t' + str(js_flag) + '\t' + title)
        return bad

def run(top_url):
    bad_connect = 0
    pat_http = re.compile("""^[a-zA-Z]+://""")
    for i in top_url:
        http = pat_http.match(i)
        if http is not None:
            bad_connect += dump_parse(i)
        else:
            url = "http://" + i
            bad_connect += dump_parse(url)
    print("未连接成功页面个数: " + str(bad_connect))





if __name__ == '__main__':
    print(time.ctime())
    if len(sys.argv) != 2:
        print('Usage: ./go.py logfile')
        sys.exit()
    ck = {}
    url = {}
    extract_data(ck, url, sys.argv[1])
    # list_ck = sort_ck(ck)
    # pt_ck(list_ck)
    list_url = sort_url(url)
    # pt_url(list_url)
    top_url = top(list_url)
    run(top_url)
    print(time.ctime())
    
