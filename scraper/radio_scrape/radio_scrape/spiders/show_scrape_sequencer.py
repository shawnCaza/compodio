# import scrapy
# from twisted.internet import reactor
# from scrapy.crawler import CrawlerRunner
# from scrapy.utils.log import configure_logging
# from scrapy.utils.project import get_project_settings
# from ciut_shows import CiutShowsSpider

# configure_logging()
# settings = get_project_settings()
# runner = CrawlerRunner(settings)
# runner.crawl(CiutShowsSpider)
# d = runner.join()
# d.addBoth(lambda _: reactor.stop())

# reactor.run() # the script will block here until all crawling jobs are finished
# print("That's all folks")