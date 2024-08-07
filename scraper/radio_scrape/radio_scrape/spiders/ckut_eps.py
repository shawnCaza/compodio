import scrapy
from scrapy.crawler import CrawlerProcess

from datetime import datetime
import requests
import time

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
                

                # the url on the download link is redirected(status 302), multiple times, to the actual mp3 file.
                # Unfortunelty, the final url does not appear available without first visiting the intermediary url.
                # This creates errors in podcachers-ex. in Apple podcasts, the mp3 will only play after hitting play twice, and first getting an error.
                # There doesn't seem to be a better solution.

                download_link = ep_element.xpath('./a[text()="Download"]/@href').get()

                if download_link:

                    time.sleep(2)
                    #First we'll get the header of the final url using alllow_redirects
                    actual_mp3_request = requests.head(f"https://ckut.ca{download_link}", stream=True, allow_redirects=True)
                    
                    redirection_link_request = requests.head(f"https://ckut.ca{download_link}", stream=True)
                    redirection_header = redirection_link_request.headers

                    if 'location' in redirection_header.keys(): 
                        current_episode['mp3'] = redirection_header['location']

                        # mp3 file name contains date and time of show. website doesn't list time.
                        # So lets get the time from the mp3 file.
                        # Since mp3 file time will be newer than the ep_date above, we still need to use that to check for newness. After fresh episodes have been added we could switch to using the mp3 file time if desired.
                        # But do we care about preserving the 'air' date, why not use the modified date of the mp3 file?

                        # mp3 file name format: "https://archives.ckut.ca/128/20240617.23.00.00-00.00.00.mp3"
                        ep_date_with_time = current_episode['mp3'].split('/')[-1].split('-')[0]
                        current_episode['ep_date'] = datetime.strptime(ep_date_with_time, "%Y%m%d.%H.%M.%S")

                        if 'content-length' in actual_mp3_request.headers.keys():
                            current_episode['file_size'] = actual_mp3_request.headers['Content-length']
                        else:
                            current_episode['file_size'] = 0

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
        time.sleep(2)

if __name__ == '__main__':
    
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(CkutEps)
    process.start()