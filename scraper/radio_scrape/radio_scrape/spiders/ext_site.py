import scrapy
from radio_scrape.items import ext_feed_item
from radio_scrape.pipeline_definitions import external_feed_pipelines

from scrapy.spiders import CrawlSpider, Rule, Request
from scrapy.linkextractors import LinkExtractor

from urllib.parse import urlparse

from radio_scrape.etc_MySQL import MySQL

def get_domain(url):
    
    parsed_uri = urlparse(url)
    domain = parsed_uri.netloc 
    return domain

def generate_key_from_link(link):
    parsed_uri = urlparse(link)
    # remove non alphabet characters from netloc
    domain_key = ''.join([char for char in parsed_uri.netloc if char.isalpha()])
    return domain_key

# Don't want to crawl all of twitter
do_not_crawl = ['twitter','facebook','podomatic', 'mixcloud', 'soundcloud', 'linktr.ee', 'anchor.fm', 'tumblr', 'instagram', 'youtube', 'itunes', 'podbay', 'blogspot', 'tripod.com', 'wordpress.com', 'stitcher', 'tunein', 'overcast', 'player.fm', 'podbean', 'pca.st', 'podcastaddict', 'podcastrepublic', 'podcasts.apple.com', 'spotify.com', 'google.com', 'podcastone.com', 'podcastindex.org', 'podcastland.com', 'podcastpedia.org', 'podcastalley.com', 'podcast411.com', 'podcastdirectory.com', 'podcast.net', 'podcast.com']

class ExtSiteSpider(scrapy.Spider):
    name = 'ext_site'

    custom_settings = {
        'ITEM_PIPELINES': external_feed_pipelines()
    }

    mySQL = MySQL()
    show_results = mySQL.get_shows_ext_sites()

    
    allowed_domains = [get_domain(show['ext_link']) for show in show_results if not any(domain in show['ext_link'] for domain in do_not_crawl)]
    print('allowed:', allowed_domains)

    # initialize link extractor, deny links with a depth of 2 or more
    link_extractor = LinkExtractor(deny=r'/\w+/\w+', allow_domains=allowed_domains, unique=True)
    
    def start_requests(self):
        
        for show in self.show_results:
            yield scrapy.Request(show['ext_link'], meta={'id':show['id']})


    def parse(self, response):
        
        print("\n--------------------------------------------\n")
        print(response.url)
        links = response.css('a::attr(href)').getall()
    
        # Create list of podcast domains
        podcast_domains = ['podcasts.apple.com', 'spotify.com/show', 'podcasts.google.com', 'google.com/podcasts']
        feed_types = ['apple', 'spotify', 'google', 'google']

        # Filter out links that are not podcasts
        podcast_links = [link for link in links if any(domain in link for domain in podcast_domains)]

        if len(podcast_links):

            for pod_link in podcast_links:
                print("\n\n~~~~~~~~~ {pod_link} ~~~~~~\n\n")
                current_feed_link = ext_feed_item()

                # Get show id from passed meta data
                show_id = response.meta['id']
                current_feed_link['show_id'] = show_id

                current_feed_link['link'] = pod_link

                current_feed_link['feed_type'] = feed_types[feed_types.index([feed_type for feed_type in feed_types if feed_type in pod_link][0])]

                yield current_feed_link


        else:
            # If no podcast links, then use linkextractor to find links to other pages
            # and follow them
            print('look for more pages to scrape')
            for link in self.link_extractor.extract_links(response):

                
                yield Request(link.url, meta={'id':response.meta['id']}, callback=self.parse)


    
