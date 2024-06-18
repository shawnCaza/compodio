# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from radio_scrape.radio_scrape.scraper_MySQL import MySQL

import requests
import urllib.parse

from slugify import slugify


class SaveEpisode:
    def process_item(self, episode, spider):
        if episode:
            print(episode, "\n\n")
            mySQL = MySQL()
            mySQL.insert_episode(episode)
        return episode

class EncodeURL:
    def process_item(self, episode, spider):
        episode['mp3'] = episode['mp3'].encode('utf-8')
        return episode
    
class GetFileSize:
    def process_item(self, episode, spider):
        
        if 'file_size' not in episode.keys():
            r = requests.head(episode['mp3'], stream=True)
            if r.status_code == 200:
                header = r.headers
                if 'Content-length' in header.keys():
                    episode['file_size'] = header['Content-length']
                else:
                    # 0 recomended when file size unknown (https://validator.w3.org/feed/docs/error/UseZeroForUnknown.html) 
                    episode['file_size'] = 0
            elif r.status_code >= 400:
                # File may not exist. Don't want to add it to DB
                episode = None
        
        return episode

class ShowSlug:
    def process_item(self, show, spider):
        slug = slugify(f"{show['source']}-{show['showName']}")
        show['slug'] = slug
        return show


class SaveShow:
    def process_item(self, show, spider):
        mySQL = MySQL()
        mySQL.insert_show(show)
        return show

class SaveExtFeedLink:
    def process_item(self, ext_feed, spider):
        mySQL = MySQL()
        mySQL.insert_ext_feed_link(ext_feed)
        return ext_feed