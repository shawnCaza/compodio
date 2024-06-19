import scrapy
from radio_scrape.radio_scrape.items import ext_feed_item
from radio_scrape.radio_scrape.pipeline_definitions import external_feed_pipelines
from scrapy.crawler import CrawlerProcess

from scrapy.spiders import CrawlSpider, Rule, Request
from scrapy.linkextractors import LinkExtractor

from urllib.parse import urlparse
import requests

from radio_scrape.radio_scrape.scraper_MySQL import MySQL

# function to seperate any camel case words in string to seperate words, use full words for variable names
def camel_case_split(str):
    split_words = [[str[0]]]
    for character in str[1:]:
        if split_words[-1][-1].islower() and character.isupper():
            split_words.append(list(character))
        else:
            split_words[-1].append(character)
    return ' '.join([''.join(word) for word in split_words])

def validate_pod_link(pod_link, show_name):

    # use requests to get text content of pod_link
    r = requests.get(pod_link)
    # check if show name is in text content
    if show_name.lower() not in r.text.lower() and camel_case_split(show_name).lower() not in r.text.lower():
        return False
    else:
        return True

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
do_not_crawl = ['twitter','facebook','podomatic', 'mixcloud', 'soundcloud', 'linktr.ee', 'anchor.fm', 'tumblr', 'instagram', 'youtube', 'itunes', 'podbay', 'blogspot', 'tripod.com', 'wordpress.com', 'stitcher', 'tunein', 'overcast', 'player.fm', 'podbean', 'pca.st', 'podcastaddict', 'podcastrepublic', 'podcasts.apple.com', 'spotify.com', 'google.com', 'podcastone.com', 'podcastindex.org', 'podcastland.com', 'podcastpedia.org', 'podcastalley.com', 'podcast411.com', 'podcastdirectory.com', 'podcast.net', 'podcast.com', 'ckut.ca']

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
           
            yield scrapy.Request(show['ext_link'], meta={'id':show['id'], 'showName':show['showName']})


    def parse(self, response):
        
        print("\n--------------------------------------------\n")
        print(response.url)
        links = response.css('a::attr(href)').getall()

        # Get show name from passed meta data
        show_name = response.meta['showName']

        # Create list of podcast domains
        # itunes is outdated, but links currently redirect to apple
        podcast_domains = ['podcasts.apple.com', 'itunes.apple.com', 'spotify.com/show', 'podcasts.google.com', 'google.com/podcasts']

        feed_types = ['apple', 'apple', 'spotify', 'google', 'google']

        # Filter out links that are not podcasts
        podcast_links = [link for link in links if any(domain in link for domain in podcast_domains)]

        if len(podcast_links):

            for pod_link in podcast_links:
                print("\n\n~~~~~~~~~ {pod_link} ~~~~~~\n\n")

                # Because a shows website may link to other podcasts we need to validate if the podcast feed link contains text matching the title of the current show
                # Because some shows like 'FoodFarm Talk' may not use camel case in their feed link we need to check both variations

                pod_link_valid = validate_pod_link(pod_link, show_name)
                if not pod_link_valid:
                    print("Show name not in text content, skipping link")
                    continue

                # use requests to get text content of pod_link
                r = requests.get(pod_link)
                # check if show name is in text content
                if show_name.lower() not in r.text.lower() and camel_case_split(show_name).lower() not in r.text.lower():
                    # if not, then skip this link
                    print("Show name not in text content, skipping link")
                    continue

                feed_type = feed_types[feed_types.index([feed_type for feed_type in feed_types if feed_type in pod_link][0])]

                if feed_type == 'apple' and '.mp4' in r.text:
                    # Apple also has video podcasts (used by democracy now). Need to note the difference
                    feed_type = 'apple_video'
                    

                # If show name is in text content, then create item


                current_feed_link = ext_feed_item()

                # Get show id from passed meta data
                show_id = response.meta['id']
                current_feed_link['show_id'] = show_id

                current_feed_link['link'] = pod_link

                current_feed_link['feed_type'] = feed_type

                yield current_feed_link


        else:
            # If no podcast links, then use linkextractor to find links to other pages
            # and follow them
            
            for link in self.link_extractor.extract_links(response):

                
                yield Request(link.url, meta={'id':response.meta['id'], 'showName':show_name}, callback=self.parse)



if __name__ == '__main__':
    
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(ExtSiteSpider)
    process.start()