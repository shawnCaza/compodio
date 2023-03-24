import scrapy
from radio_scrape.items import ext_feed_item
from radio_scrape.pipeline_definitions import external_feed_pipelines

from scrapy.spiders import CrawlSpider, Rule, Request
from scrapy.linkextractors import LinkExtractor

from urllib.parse import urlparse

from radio_scrape.etc_MySQL import MySQL

def get_domain(url):
    
    parsed_uri = urlparse(url)
    domain = f'{parsed_uri.scheme}://{parsed_uri.netloc}/'  
    return domain

def generate_key_from_link(link):
    parsed_uri = urlparse(link)
    # remove non alphabet characters from netloc
    domain_key = ''.join([char for char in parsed_uri.netloc if char.isalpha()])
    return domain_key


class ExtSiteSpider(scrapy.Spider):
    name = 'ext_site'

    custom_settings = {
        'ITEM_PIPELINES': external_feed_pipelines()
    }



    mySQL = MySQL()
    show_results = mySQL.get_shows_ext_sites()
    show_id_map = {generate_key_from_link(show['ext_link']):show['id'] for show in show_results}
    start_urls = [show['ext_link'] for show in show_results]
    

    
    allowed_domains = [get_domain(show['ext_link']) for show in show_results ]
    print(allowed_domains)
    # initialize link extractor, deny links with a depth of 2 or more
    link_extractor = LinkExtractor(deny=r'/\w+/\w+', allow_domains=allowed_domains, unique=True)
    

    def parse(self, response):
        print("--------------------------------------------")
        print("--------------------------------------------")
        print("--------------------------------------------")
        links = response.css('a::attr(href)').getall()
    
        # Create list of podcast domains
        podcast_domains = ['podcasts.apple.com', 'spotify.com/show/']
        feed_types = ['apple', 'spotify']

        # Filter out links that are not podcasts
        podcast_links = [link for link in links if any(domain in link for domain in podcast_domains)]

        if len(podcast_links):

            for pod_link in podcast_links:
                print(pod_link)
                current_feed_link = ext_feed_item()

                # Get show id from show_id_map
                show_id = self.show_id_map[generate_key_from_link(response.url)]
                current_feed_link['show_id'] = show_id

                current_feed_link['link'] = pod_link

                current_feed_link['feed_type'] = feed_types[feed_types.index([feed_type for feed_type in feed_types if feed_type in pod_link][0])]

                yield current_feed_link


            #  stop following links
            return
            
            

        else:
            # If no podcast links, then use linkextractor to find links to other pages
            # and follow them
            for link in self.link_extractor.extract_links(response):
                yield Request(link.url, callback=self.parse)


    
