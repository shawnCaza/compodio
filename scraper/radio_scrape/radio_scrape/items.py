# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class episode_item(scrapy.Item):
    # define the fields for your item here like:
    mp3 = scrapy.Field()
    show_id = scrapy.Field()
    ep_date = scrapy.Field()
    file_size = scrapy.Field()

class show_item(scrapy.Item):
    # define the fields for your item here like:
    showName = scrapy.Field()
    source = scrapy.Field()
    img = scrapy.Field()
    desc = scrapy.Field()
    host = scrapy.Field()
    internal_link = scrapy.Field()
    ext_link = scrapy.Field()
    email = scrapy.Field()
    duration = scrapy.Field()
    slug = scrapy.Field()
    
