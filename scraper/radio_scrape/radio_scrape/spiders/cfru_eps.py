import scrapy

from datetime import datetime

from radio_scrape.radio_scrape.items import episode_item
from radio_scrape.radio_scrape.pipeline_definitions import episode_pipelines
from radio_scrape.radio_scrape.scraper_MySQL import MySQL

class CfruEps(scrapy.Spider):
    name = 'cfru'        
    custom_settings = {
        'ITEM_PIPELINES': episode_pipelines()
    }

    mySQL = MySQL()
    show_results = mySQL.get_shows_by_source('cfru')

    newest_eps = mySQL.get_newest_ep_by_source('cfru')
    newest_ep_map = {ep['show_id']:{'id':ep['id'], 'ep_date':ep['ep_date']} for ep in newest_eps}


    allowed_domains = ['cfru.ca']

    def start_requests(self):
    
        for show in self.show_results:
            yield scrapy.Request(show['internal_link'], meta={'id':show['id'], 'show_name':show['showName']})

    def parse(self, response):

        show_id = response.meta['id']
 

        for episode in response.css('div.archiveList-post'):

            all_eps_scraped = False

            title = episode.xpath(".//div[contains(@class,'archive-title')]/text()").get()

            # cfru playist is sometimes mashed into other shows (title will contain a '+'). They all show up in the ordinary cfru archive page. Don't want to duplicate episodes across shows.

            if not (response.meta['show_name'] == 'CFRU Playlist' and '+' in title) and not 'Rebroadcast' in title:

                # example full_desc "Tiempo de Mujeres – November 19, 2022 at 20:00"
                date_str = title.rsplit(" – ",1)[1]
                print(date_str)
                ep_date = datetime.strptime(date_str, "%B %d, %Y at %H:%M")
                
                if show_id in self.newest_ep_map.keys():
                    most_recent_ep_date = self.newest_ep_map[show_id]['ep_date']
                else:
                    most_recent_ep_date = None

                if not most_recent_ep_date or ep_date > most_recent_ep_date:

                    current_episode = episode_item()

                    current_episode['mp3'] = episode.xpath('.//a/@href').get()
                    current_episode['show_id'] = show_id
                    current_episode['ep_date'] = ep_date

                    yield current_episode

                else:
                    all_eps_scraped = True
                    break

        if not all_eps_scraped:

            next_relative_path = response.xpath("//a[contains(text(),'Older Entries')]/@href").get()

            if next_relative_path is not None:
                next_page = response.urljoin(next_relative_path)
                yield scrapy.Request(next_page, callback=self.parse)