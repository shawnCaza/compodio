import scrapy
from scrapy.crawler import CrawlerProcess

from datetime import datetime
import requests

from radio_scrape.radio_scrape.items import episode_item
from radio_scrape.radio_scrape.pipeline_definitions import episode_pipelines
from radio_scrape.radio_scrape.scraper_MySQL import MySQL

class CkutEps(scrapy.Spider):
    name = 'ckut'        
    custom_settings = {
        'ITEM_PIPELINES': episode_pipelines()
    }

    mySQL = MySQL()
    show_results = mySQL.get_shows_by_source('ckut')

    newest_eps = mySQL.get_newest_ep_by_source('ckut')
    newest_ep_map = {ep['show_id']:{'id':ep['id'], 'ep_date':ep['ep_date']} for ep in newest_eps}
    visited_pages = set()

    allowed_domains = ['ckut.ca']

    def start_requests(self):
    
        for show in self.show_results:
            yield scrapy.Request(show['internal_link'], meta={'id':show['id'], 'show_name':show['showName']})

    def parse(self, response):

        show_id = response.meta['id']
        self.visited_pages.add(response.url,)

        for ep_element in response.xpath("//div[@class='playlist-archive']/ul/li"):
            
            # because many other elements are in the same li tag, we need to extract the text from the li tag
            ep_txt = ep_element.xpath("string(.)").extract()[0].strip()
            
            # example ep_txt: "June 16, 2024:" There is *sometimes* an actual title after the date in <b> tag, but this won't included in ep_txt since it's not a direct child of the li tag

            date_str = ep_txt.split(":")[0].strip()
            print(date_str)
            ep_date = datetime.strptime(date_str, "%B %d, %Y")
            
            if show_id in self.newest_ep_map.keys():
                most_recent_ep_date = self.newest_ep_map[show_id]['ep_date']
            else:
                most_recent_ep_date = None

            if not most_recent_ep_date or ep_date > most_recent_ep_date:

                current_episode = episode_item()

                current_episode['show_id'] = show_id
                current_episode['ep_date'] = ep_date

                # the url on the download link is redirected to the actual mp3 file (status 302)
                download_link = ep_element.xpath('./a[text()="Download"]/@href').get()
                r = requests.head(f"https://ckut.ca{download_link}", stream=True)
                header = r.headers
                if 'location' in header.keys(): 
                    current_episode['mp3'] = header['location']
                    yield current_episode
                
            else:
                break

        else:
            # Reached the end of the page. Check for pagination links.
            for page_relative_link in response.xpath("//div[@class='playlist-year']/a"):
                
                potential_next_page = page_relative_link.xpath("./@href").get()
                if potential_next_page and potential_next_page not in self.visited_pages:
                    # use urljoin to get the full url from relative path
                    next_page = response.urljoin(potential_next_page)
                    yield scrapy.Request(next_page, callback=self.parse)
                    break

if __name__ == '__main__':
    
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(CkutEps)
    process.start()