# -*- coding: utf-8 -*-

import json
import re
import os
import requests
from bs4 import BeautifulSoup
from requests import RequestException
import time
from hashlib import md5
from multiprocessing import Pool
import sys
sys.path.append("E:\PythonProject\jiepai")
import config

def get_page_index(offset,keyword):
    data={
            'offset':offset,
            'format':'json',
            'keyword':keyword,
            'autoload':'true',
            'count':'20',
            'cur_tab':1,
            'from':'search_tab'
    }
    headers={
            'referer':'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
            'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Mobile Safari/537.36',
            'x-requested-with':'XMLHttpRequest',
            'cookie':'uuid="w:eda26cb7f71b4082989cf72050143613"; _ga=GA1.2.1465496017.1517130472; UM_distinctid=1613c05db45524-05319a30e1b5b8-4323461-100200-1613c05db46aaf; tt_webid=6516025715698451976; sso_login_status=0; tt_webid=6516025715698451976; WEATHER_CITY=%E5%8C%97%E4%BA%AC; CNZZDATA1259612802=2081794518-1517129274-%7C1517449101; __tasessionId=zrltezo5h1517450759922'
    }
    url='https://www.toutiao.com/search_content'
    try:
        response = requests.get(url,params=data,headers=headers)
        #print(type(response)) <class 'requests.models.Response'>
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求索引页错误")
        return None
    pass
def parse_page_index(html):
    parse_data = json.loads(html)
    #print(type(parse_data)) #<class 'dict'>
    if parse_data and 'data' in parse_data.keys():
        for item in parse_data.get('data'):
            if item and 'article_url' in item.keys():
                yield item.get('article_url')
                
def get_page_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求详情页错误",url)
        return None
    pass
def parse_page_detail(detail_html):
    soup = BeautifulSoup(detail_html,"lxml")
    #print(soup)
    title = soup.select('title')[0].get_text()
    print(title)
    images_pattern = re.compile(r'gallery: JSON.parse\("(.*?)"\),',re.S)
    # json_data is type json, replace:  \" ---->  "
    list_data = re.findall(images_pattern,detail_html.replace('\\"','"'))
    #print(type(list_data))  <class 'list'>
    if list_data:
        str_data = list_data[0] #<class 'str'>
        json_data = json.loads(str_data)
        #print(type(json_data)) #dict
        if json_data and 'sub_images' in json_data.keys():
            sub_images = json_data.get('sub_images')  #<class list>
            for items in sub_images:
                image_urls = items.get('url')
                #print(image_urls)
                download_image(image_urls)
        
    return True
            
def download_image(image_url):
    #print(type(image_url))
    image_standardurl = image_url.replace('\\','')
    print('正在加载图片',image_standardurl)
    
    try:
        response = requests.get(image_standardurl)
        #print(response.status_code)
        if response.status_code == 200 :
            print('okokokoko')
            save_image(response.content)
    except RequestException:
        print('请求图片错误',image_url)
    pass

def save_image(content):
    file_path = '{0}/{1}/{2}.{3}'.format(os.getcwd(),'pictures',md5(content).hexdigest(),'jpg')
    file_standardpath = file_path.replace('\\','/')
    #print(file_standardpath)
    if not os.path.exists(file_standardpath):
        with open(file_standardpath,'wb') as f:
            f.write(content)
            f.close()

def main(offset):
    html = get_page_index(offset,config.KEYWORD)
    #print(type(html)) <class 'str'>
    #print(html)
    for url in parse_page_index(html):
        detail_html = get_page_detail(url)
        if detail_html:
            #print(detail_html)
            #print('---'*30)
            #print(type(detail_html))
            time.sleep(3)
            parse_page_detail(detail_html)
            
    
if __name__ =='__main__':
    groups = [x * 20 for x in range(config.GROUP_START,config.GROUP_END)]
    pool = Pool()
    pool.map(main,groups)
    