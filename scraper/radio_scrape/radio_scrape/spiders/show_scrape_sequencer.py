import scrapy
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor
from twisted.internet import defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from ciut_shows import CiutShowsSpider
from cfru_shows import CfruShowsSpider
from ckut_shows import CkutShowsSpider
from ciut_eps import CiutEps
from cfru_eps import CfruEps
from ckut_eps import CkutEps
from radio_scrape.radio_scrape.server_sync.sync_compodio_data_to_server import sync_db
setting = get_project_settings()

process = CrawlerProcess(setting)

@defer.inlineCallbacks
def crawl_seq():
    global process

    yield process.crawl(CiutShowsSpider)
    yield process.crawl(CfruShowsSpider)
    yield process.crawl(CkutShowsSpider)
    #reactor.stop()

crawl_seq()

# after the show spider completes, run the episode spiders
@defer.inlineCallbacks
def crawl_seq2():
    global process

    yield process.crawl(CiutEps)
    yield process.crawl(CkutEps)
    yield process.crawl(CfruEps)
    # reactor.stop()

crawl_seq2()

process.start() # the script will block here until the crawling is finished

sync_db()

print("done")