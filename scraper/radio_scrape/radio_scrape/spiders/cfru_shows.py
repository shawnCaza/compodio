import scrapy
from radio_scrape.items import show_item
from radio_scrape.pipeline_definitions import show_pipelines

class CfruShowsSpider(scrapy.Spider):
    name = 'cfru_shows'
    custom_settings = {
        'ITEM_PIPELINES': show_pipelines()
    }
    allowed_domains = ['cfru.ca']
    start_urls = ['https://www.cfru.ca/shows/']

    def parse(self, response):
        shows_to_skip = ['A Fill-In Broadcast', 'Your Show Here', 'CFRU Rebroadcast', 'BBC News', 'Rebroadcast']
        existing_show_names = set()

        for day_column in response.css("div.schedule-day"):
            for show in day_column.css("div.schedule-showWrapper"):
                current_show = show_item()

                # print(show.xpath(".//div[@class='links']/a[text()='archives']/@href").get())
                current_show['showName'] = show.xpath(".//a[@class='showTitle']/text()").get()

                if all(skip_show not in current_show['showName'] for skip_show in shows_to_skip) and current_show['showName'] not in existing_show_names:
                    existing_show_names.add(current_show['showName'])
                    current_show['img'] = show.xpath(".//div[@class='show_image']/img/@src").get()


                    # loop through each paragraph in the div with the description class
                    desc_paragraphs = show.xpath(".//div[@class='description']/p")


                    desc = ''
                    for p in desc_paragraphs:
                        if p.xpath("./text()") and len(p.xpath("./text()").get().strip()):
                            desc += f"<p>{p.xpath('./text()').get().strip()}</p>"
                        
                        
                    



                    current_show['desc'] = desc.strip() if desc is not None else ''  
                    current_show['host'] = show.xpath(".//div[@class='hosts']/text()").get().replace('hosted by','').strip()
                    current_show['internal_link'] = show.xpath(".//div[@class='links']/a[text()='archives']/@href").get()
                    current_show['ext_link'] = show.xpath(".//div[@class='links']/a[text()='website']/@href").get()
                    current_show['email'] = show.xpath(".//div[@class='links']/a[text()='email']/@href").get().replace('mailto:', '')
                    current_show['source'] = 'cfru'
                    current_show['duration'] = 60 * 60 #all eps are broken into 1hr segments

                    yield current_show

    {
# <div class="category-box category_15 showtime" style="height:70.450097847358px ">
#                                              <a class="showTitle">The Kookoo Bananas Variety Hour</a>
#                                              <div class="hover show">
#                                                  <button type="button" class="close" data-dismiss="alert">×</button>
#                                                  <div class="show_image">
#                                                      <img src="https://www.cfru.ca/wp-content/uploads/2018/04/The-Kookoo-Bananas-Variety-Hour.jpg" alt="The Kookoo Bananas Variety Hour">
#                                                  </div>
#                                                  <div class="copy">
#                                                      <h2>The Kookoo Bananas Variety Hour</h2>
#                                                      <div class="show_time">
#                                                          <span> sunday </span>
#                                                          <span> 10:00 am to </span>
#                                                          <span> 11:00 am </span>
#                                                      </div>
#                                                      <div class="hosts">
#                                                          hosted by
#                                                          Curtis Walker &amp; kids                                                     </div>
#                                                      <div class="description"><p>The Kookoo Bananas Variety Hour is a family-friendly show jam-packed with kiddie records, weirdo pop culture, and songs sung by robots, animals, and even kids! Hosted by Cap’n Kookoo &amp; The Banana Brats.</p>
# </div>
#                                                      <div class="links">
#                                                          <a target="_blank" href="https://www.cfru.ca/?s=The%20Kookoo%20Bananas%20Variety%20Hour&amp;posttype_search=mcm_recording">archives</a>
#                                                          <a target="_blank" href="https://www.cfru.ca/www.facebook.com/KookooBananas">website</a>
#                                                          <a target="_blank" href="mailto:kookookoobananas@gmail.com">email</a>
#                                                      </div>
#                                                      <div class="category_15 category_icon"></div>
#                                                  </div>
#                                              </div>
#                                             </div>
}

                

        
    def get_cat():
        """Returns dict which acts as a map of category ids:category names. Made from scaping the category legend on the page. Needed to map show category ids to actual categories"""
        pass