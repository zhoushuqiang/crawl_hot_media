#!coding=utf-8
import datetime
import os
import re

import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
import logging
import requests
from db.models import ViedoModel, Base
import time

baseurl = 'http://www.miaopai.com/miaopai/index_api?'
sitename = u'秒拍'
basepage = '1'
all_cate = {
    'hot': [u'热门', 'cateid=2002&per=20&page='],
    'stars': [u'明星名人', 'cateid=124&per=20&page='],
    'hot_news': [u'热点', 'cateid=136&per=20&page='],
    'goddess': [u'女神', 'cateid=132&per=20&page='],
    'creative': [u'创意', 'cateid=160&per=20&page='],
    'funny': [u'搞笑', 'cateid=128&per=20&page='],
    'pet': [u'宠物', 'cateid=140&per=20&page='],
    'any_shot': [u'随手拍', 'cateid=2003&per=20&page=']
}
logging.basicConfig(format='[ %(asctime)s - %(filename)s - %(lineno)d ] : %(message)s')
logger = logging.getLogger('miaopai')
logger.setLevel(logging.DEBUG)


class Miaopai(object):
    def __init__(self, session):
        self.session = session
        pass

    def parse(self):

        # 创建文件夹
        today = datetime.datetime.now()
        date_str = '{}_{}_{}'.format(today.year, today.month, today.day)
        site_base_dir = os.path.join(settings.DATA_BASE_DIR, date_str, sitename)
        if not os.path.isdir(site_base_dir):
            os.makedirs(site_base_dir)
        for value in all_cate.itervalues():
            cate_dir = os.path.join(site_base_dir, value[0])
            relative_dir = os.path.join(date_str, sitename, value[0])
            if not os.path.isdir(cate_dir):
                os.mkdir(cate_dir)
            url = baseurl + value[1] + basepage
            # print 'URSL: ', url
            # try:
            logger.debug('Start: %s' % url)
            r = requests.get(url, headers=settings.get_header())
            json_data = r.json()
            results = json_data['result']
            for obj in results:
                uuid = obj['channel']['scid']
                title = obj['channel']['ext']['t']
                desc = obj['channel']['ext']['t']
                download_url = obj['channel']['stream']['base'].split('.mp4')[0]+'.mp4'

                video = ViedoModel(uuid=uuid, category=value[0], site=sitename,
                                   title=title, desc=desc, url=download_url, path=relative_dir)
                exist = self.session.query(ViedoModel).filter(or_(ViedoModel.uuid==uuid,
                                                          ViedoModel.desc==desc, ViedoModel.title==title)).all()
                if not exist:
                    self.session.add(video)
                else:
                    logger.debug(u'Dump video find, ignore. %s' % title)
                logger.debug(u'find video: %s' % title)
            self.session.commit()
            # except Exception as e:
            #     logger.debug('Exception:', e)
            logger.debug(' sleep 3 s '.center(60, '-'))
            time.sleep(3)

    def download(self):
        logger.debug('Download file')
        videos = self.session.query(ViedoModel).all()
        if not videos:
            logger.debug('None video find in db, return')
            return
        logger.debug('Start download {} files...'.format(len(videos)))
        for video in videos:
            if not video.download:
                name = ''.join(re.findall('[^\/<>"]+', video.title[:20]))
                # print 'sb',name
                file_name = os.path.join(settings.DATA_BASE_DIR, video.path, name+'.mp4')
                print file_name
                r = requests.get(video.url, headers=settings.get_header(), stream=True)
                with open(file_name, 'w') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                logger.debug(' sleep 2s '.center(60, '-'))
                video.download = True
                session.add(video)
                session.commit()
                time.sleep(2)
            else:
                logger.debug('video has downloaded')

if __name__ == '__main__':
    global session
    engine = create_engine(settings.DATABASES['default']['NAME'], **settings.DATABASES['default']['CONFIG'])
    __session = sessionmaker(bind=engine)
    session = __session()
    Base.metadata.create_all(engine)
    miaopai = Miaopai(session)
    # miaopai.parse()
    miaopai.download()
