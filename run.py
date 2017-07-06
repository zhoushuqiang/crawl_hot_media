#!/usr/bin/env python
#coding=utf-8
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import random
import logging
from db.models import Base
from sites.site_miaopai import Miaopai
import settings

logging.basicConfig(level=logging.DEBUG)

sites = [
    'http://www.meipai.com/medias/hot',
    'http://www.pearvideo.com/',
    'http://www.miaopai.com/miaopai/plaza',
]

proxy_url = 'http://dev.kuaidaili.com/api/getproxy/?orderid=949918412269929&num=100&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=1&method=2&an_an=1&an_ha=1&sp1=1&sp2=1&sp3=1&sep=1'

url_dict = {
    'miaopai':[
        'http://www.miaopai.com/miaopai/index_api?cateid=2002&per=20&page=1',
        'http://www.miaopai.com/miaopai/plaza?cateid=124',
        'http://www.miaopai.com/miaopai/plaza?cateid=136',
        'http://www.miaopai.com/miaopai/plaza?cateid=132',
        'http://www.miaopai.com/miaopai/plaza?cateid=160',
        'http://www.miaopai.com/miaopai/plaza?cateid=128',
        'http://www.miaopai.com/miaopai/plaza?cateid=144',
        'http://www.miaopai.com/miaopai/plaza?cateid=140',
        'http://www.miaopai.com/miaopai/plaza?cateid=9',
    ],
}

def get_ip():
    r = requests.get(proxy_url)
    return r.content.split('\r\n')


def main():
    ip_list = get_ip()
    print ip_list
    headers = {'user-agent': user_agent.USER_AGENTS[random.randint(0, len(user_agent.USER_AGENTS) - 1)]}
    ip = ip_list[random.randint(1, len(ip_list)-1)]
    proxies = {'http': str(ip)}
    print ip, url_dict['miaopai'][0]
    r = requests.get(url_dict['miaopai'][0], proxies=proxies, headers=headers)
    print r.content
    r_dict = r.json()
    video_url = []
    for item in r_dict['result']:
        id = item['channel']['scid']+'.mp4'
        u = item['channel']['stream']['base'].split('?')[0]
        video_url.append([id, u])
        print id, u
    for v in video_url:
        ip = ip_list[random.randint(1, len(ip_list) - 1)]
        proxies = {'http': str(ip)}
        headers = {'user-agent': user_agent.USER_AGENTS[random.randint(0, len(user_agent.USER_AGENTS) - 1)]}
        name = v[0]
        url = v[1]
        print 'download: ', url, ' with IP: ', ip
        logging.debug('download ....')
        r = requests.get(url, proxies=proxies, headers=headers)
        with open('data/'+str(name), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    logging.debug('write....')
                    f.write(chunk)


if __name__ == '__main__':
    engine = create_engine(settings.DATABASES['default']['NAME'], **settings.DATABASES['default']['CONFIG'])
    __session = sessionmaker(bind=engine)
    session = __session()
    Base.metadata.create_all(engine)
    miaopai = Miaopai(session)
    # miaopai.parse()
    miaopai.download()
    # main()