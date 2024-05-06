import scrapy
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor
from twisted.internet import defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from ext_site import ExtSiteSpider
from radio_scrape.radio_scrape.server_sync.sync_compodio_data_to_server import sync_db
setting = get_project_settings()

process = CrawlerProcess(setting)

@defer.inlineCallbacks
def crawl_seq():
    global process

    yield process.crawl(ExtSiteSpider)

crawl_seq()


process.start() # the script will block here until the crawling is finished

# sync_db()

print("done")