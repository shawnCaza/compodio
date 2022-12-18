import scrapy

from datetime import datetime
import requests

from radio_scrape.items import episode_item
from radio_scrape.pipeline_definitions import episode_pipelines
from radio_scrape.etc_MySQL import MySQL

class CfruSpider(scrapy.Spider):
    name = 'ciut_episodes'        
    custom_settings = {
        'ITEM_PIPELINES': episode_pipelines()
    }

    mySQL = MySQL()
    show_results = mySQL.get_shows_by_source('ciut')
    newest_eps = mySQL.get_newest_ep_by_source('ciut')
    
    show_id_map = {show['showName']:show['id'] for show in show_results}

    newest_ep_map = {ep['show_id']:{'id':ep['id'], 'ep_date':ep['ep_date']} for ep in newest_eps}

    start_urls = [show['internal_link'] for show in show_results]
    allowed_domains = ['ciut.fm']


    def parse(self, response):
        current_episode = episode_item()

        show_name = response.xpath("//h1/text()").get()

        show_id = self.show_id_map[show_name]

        # Need to get most recently stored ep for show to see if current live listing is newer
        if show_id in self.newest_ep_map.keys():
            most_recent_ep_date = self.newest_ep_map[show_id]['ep_date'] 
        else:
            most_recent_ep_date = None

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
