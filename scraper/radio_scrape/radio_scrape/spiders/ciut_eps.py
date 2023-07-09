import scrapy

from datetime import datetime, timezone
import requests
from urllib.parse import urlparse, parse_qs

from radio_scrape.radio_scrape.items import episode_item
from radio_scrape.radio_scrape.pipeline_definitions import episode_pipelines
from radio_scrape.radio_scrape.scraper_MySQL import MySQL

class CiutEps(scrapy.Spider):
    name = 'ciut_episodes'        
    custom_settings = {
        'ITEM_PIPELINES': episode_pipelines()
    }

    mySQL = MySQL()
    show_results = mySQL.get_shows_by_source('ciut')
    newest_eps = mySQL.get_newest_ep_by_source('ciut')
    
    show_id_map = {show['showName']:show['id'] for show in show_results}

    newest_ep_map = {ep['show_id']:{'id': ep['id'], 'ep_date': ep['ep_date'], 'ep_mp3': ep['mp3']} for ep in newest_eps}

    start_urls = [show['internal_link'] for show in show_results]
    allowed_domains = ['ciut.fm', 'podbean.com']


    def parse(self, response):

        show_name = response.xpath("//h1/text()").get()

        show_id = self.show_id_map[show_name]

        # Need to get most recently stored ep for show to determine if anything is newer
        if show_id in self.newest_ep_map.keys():
            
            most_recent_mp3 = self.newest_ep_map[show_id]['ep_mp3']

            if most_recent_mp3 and 'ciut.fm' in most_recent_mp3:
                
                # Older file scraped before podbean feed was available.
                # most recent date no longer relevant, so set to None
                most_recent_ep_date = None

                # Need to clean up any episodes scraped before switch to podbean feed as they are no longer relevant
                where_clause = """mp3 like '/%%ciut.fm%%'"""
                self.mySQL.remove_old_eps_by_show(show_id, where_clause)

            else:

                most_recent_ep_date = self.newest_ep_map[show_id]['ep_date'] 

        else:
            most_recent_ep_date = None
            most_recent_mp3 = None

        podbean_info_link = response.xpath("//iframe/@data-src").extract_first()

        if podbean_info_link:
            print('has podbean player:', podbean_info_link)
            parsed_url = urlparse(podbean_info_link)
            query_string = parse_qs(parsed_url.query)
            podbean_show_id = query_string['i'][0]

            podbean_feed_link = f"https://www.podbean.com/player/{podbean_show_id}-pbblog-playlist?scode=&pfauth=&referrer=&order=episodic&limit=10&filter=all&publish_start=&publish_end=&season=&tag=&ss=a713390a017602015775e868a2cf26b0&touchable=false&type=playlist"

            yield scrapy.Request(url=podbean_feed_link, callback=self.parse_podbean_info, meta={'show_id': show_id, 'most_recent_ep_date': most_recent_ep_date, 'most_recent_mp3': most_recent_mp3})

        
        else:
            current_episode = episode_item()
            current_episode['mp3'] = response.xpath("//audio/source/@src").get()

            if current_episode['mp3']:

                # Since CIUT only ever lists one mp3 file, and no information on the page when it was last updated, we need to check last modified header on the file itself to ensure we have a new date reference to add to the DB.
                mp3_last_mod = requests.head(current_episode['mp3']).headers['last-modified']
                mp3_last_mod_dt = datetime.strptime(mp3_last_mod.replace(" GMT",""), "%a, %d %b %Y %H:%M:%S")

                if not most_recent_ep_date or mp3_last_mod_dt > most_recent_ep_date:
                    print("\n\n*** NEW *** \n\n")
                    # Since old ep is no longer relevant we need to remove it
                    if show_id:
                        print("removing", show_id)
                        self.mySQL.remove_old_eps_by_show(show_id)

                    current_episode['ep_date'] = mp3_last_mod_dt
                    current_episode['show_id'] = show_id

                    yield current_episode

    def parse_podbean_info(self, response):
            
            show_id = response.meta['show_id']
            most_recent_ep_date = response.meta['most_recent_ep_date']

            
            url_title = response.xpath("//setting/author/text()").get()
            podbean_feed_link = f"https://feed.podbean.com/{url_title}/feed.xml"

            yield scrapy.Request(url=podbean_feed_link, callback=self.parse_podbean_feed, meta={'show_id': show_id, 'most_recent_ep_date': most_recent_ep_date})


    def parse_podbean_feed(self, response):

        show_id = response.meta['show_id']
        most_recent_ep_date = response.meta['most_recent_ep_date']
        # select all episodes
        episodes = response.xpath("//item")


        for ep in episodes:
            print("\n\nep:", ep)
            current_episode = episode_item()
            current_episode['mp3'] = ep.xpath("enclosure/@url").get()
            current_episode['file_size'] = ep.xpath("enclosure/@length").get()

            # TODO: add title and description columns in DB so we can store this info
            # current_episode['title'] = ep.xpath("title/text()").get()
            # current_episode['description'] = ep.xpath("description/text()").get()

            # timzone naive datetime object to match DB
            current_episode['ep_date'] = datetime.strptime(ep.xpath("pubDate/text()").get(), "%a, %d %b %Y %H:%M:%S %z").astimezone(timezone.utc).replace(tzinfo=None)
            
            
            if not most_recent_ep_date or current_episode['ep_date'] > most_recent_ep_date:   
                
                if show_id:

                    current_episode['show_id'] = show_id

                    yield current_episode

            else:

                print("\n\nEnd of new episodes")
                break


    

        
