import scrapy

from datetime import datetime

from radio_scrape.items import episode_item
from radio_scrape.pipeline_definitions import episode_pipelines
from radio_scrape.etc_MySQL import MySQL

class CfruSpider(scrapy.Spider):
    name = 'cfru'        
    custom_settings = {
        'ITEM_PIPELINES': episode_pipelines()
    }

    mySQL = MySQL()
    show_results = mySQL.get_shows_by_source('cfru')
    show_id_map = {show['showName']:show['id'] for show in show_results}
    start_urls = [show['ext_link'] for show in show_results]
    allowed_domains = ['cfru.ca']


    def parse(self, response):
        pass
        for episode in response.css('div.archiveList-post'):
            current_episode = episode_item()

            title = episode.xpath(".//div[contains(@class,'archive-title')]/text()").get()
            # example full_desc "Tiempo de Mujeres – November 19, 2022 at 20:00"
            showName, date_str = title.rsplit(" – ",1)

            current_episode['mp3'] = episode.xpath('.//a/@href').get()
            current_episode['show_id'] = self.show_id_map[showName]
            current_episode['ep_date'] = datetime.strptime(date_str, "%B %d, %Y at %H:%M")
            yield current_episode


        next_relative_path = response.xpath("//a[contains(text(),'Older Entries')]/@href").get()
        if next_relative_path is not None:
            next_page = response.urljoin(next_relative_path)
            yield scrapy.Request(next_page, callback=self.parse)