import re 

import scrapy
from scrapy.crawler import CrawlerProcess
from radio_scrape.radio_scrape.items import show_item
from radio_scrape.radio_scrape.pipeline_definitions import show_pipelines


class CkutShowsSpider(scrapy.Spider):
    name = 'Ckut_shows'
    custom_settings = {
        'ITEM_PIPELINES': show_pipelines()
    }
    allowed_domains = ['ckut.ca']
    start_urls = ['https://ckut.ca/programming/']

    def parse(self, response):
        shows_to_skip = ['Democracy Now!', 'BBC News', 'A Multilingual Affair']
        existing_show_names = set()

        for show in response.css("div.grid-item"):

            # We start by parsing the programming page to get initial info, and links for all shows. Then go to each shows page to get full info.

            current_show = show_item()

            (      
                    # <div class="grid-item">
                    # 	<a href="/playlists/VM">
                    # 							<img width="1080" height="1080" src="https://ckut.ca/wp-content/uploads/2022/11/New-Voices.png" class="attachment-large size-large wp-post-image" alt="" decoding="async" loading="lazy" srcset="https://ckut.ca/wp-content/uploads/2022/11/New-Voices.png 1080w, https://ckut.ca/wp-content/uploads/2022/11/New-Voices-768x768.png 768w, https://ckut.ca/wp-content/uploads/2022/11/New-Voices-200x200.png 200w, https://ckut.ca/wp-content/uploads/2022/11/New-Voices-300x300.png 300w" sizes="(max-width: 1080px) 100vw, 1080px">							</a>
                    # 	<div class="tags">
                    #     <small>Programming</small>
                    #     <small class="thumbnail-category">
                    # 						<a href="https://ckut.ca/programming-categories/spokenword/arts-culture/">Arts &amp; Culture</a>
                    # 							<a href="https://ckut.ca/programming-categories/mcgill/">McGill</a>
                    # 							<a href="https://ckut.ca/programming-categories/spokenword/">Spoken Word</a>
                    # 		            </small>
                    # 	</div>
                    # 	<a href="/playlists/VM">
                    # 		<div class="featured-blog-title">
                    # 			<h2>Voices of Montreal: New Voices</h2>
                    # 		</div>
                    # 		<div class="featured-blog-description">
                    # 			Wanna be on the radio? Join our Spoken Word Coordinator on the first Thursday of every month from 2-3pm to learn the ropes of live community radio. No experience or preparation necessary! Just email spokenword@ckut.ca if you want to join.				</div>
                    # 	</a>
                    # </div>
                    )

            # print(show.xpath(".//div[@class='links']/a[text()='archives']/@href").get())
            current_show['showName'] = show.xpath(".//div/h2/text()").get()
                
        
            if all(skip_show not in current_show['showName'] for skip_show in shows_to_skip) and current_show['showName'] not in existing_show_names:
                
                existing_show_names.add(current_show['showName'])

                current_show['img'] = show.xpath(".//img/@src").get()

                # programming page contains a short description. Longer desc available at internal link page
                desc = show.xpath(".//div[@class='featured-blog-description']/text()").get()

                raw_internal_link = show.xpath(".//a/@href").get()
                internal_link = raw_internal_link if 'https://ckut.ca/' in raw_internal_link else f'https://ckut.ca{raw_internal_link}'
                current_show['internal_link'] = internal_link

                # Open show page (internal_link)
                yield response.follow(current_show['internal_link'], self.parse_show_page, cb_kwargs=dict(current_show=current_show, desc=desc))

        # Check for 'next' button to go to next page of shows
        next_page = response.xpath("//a[@class='next page-numbers']/@href").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_show_page(self, response, current_show, desc):
        # Get full show info from show page

        hosts = []
        # Get list of potential host nodes
        host_nodes = response.xpath("//div[@class='sidebar-info']//small[contains(text(),'HOST')]/../p")
        # text() for host could be in the host node, or in an a tag in the host node. If it exists add it to hosts list
        for host_node in host_nodes:
            host = host_node.xpath("./text()").get()
            
            if host is None or host.strip() == '':
                host = host_node.xpath("./a/text()").get()

            if host is not None and host.strip() != '':
                hosts.append(host.strip())

        external_link = response.xpath(".//div[@class='sidebar-info']//small[contains(text(),'EXTERNAL SITE')]/../p/a/@href").get()

        schedule_txt = response.xpath(".//div[@class='sidebar-info']//small[contains(text(),'SCHEDULE')]/../p/text()").get()



        current_show['desc'] = desc.strip() if desc is not None else ''  
        current_show['host'] = ', '.join(hosts)
        current_show['ext_link'] = external_link if external_link is not None else ''
        current_show['email'] = ''
        current_show['source'] = 'ckut'
        current_show['duration'] = self.calculate_duration(schedule_txt)

        yield current_show



    def calculate_duration(self, schedule_txt):

        if schedule_txt is not None:
            # standardized time format
            txt = schedule_txt.upper().replace('NOON', '12pm').replace('MIDNIGHT', '12AM')
            # some shows are only aired on certain weeks of the month. Let's remove the week reference, to more reliably parse the time of day it airs
            week_ordinal_refs = ['1ST', '2ND', '3RD', '4TH', '5TH']
            for week_ordinal in week_ordinal_refs:
                txt = txt.replace(week_ordinal, '')
            # capture groups containing a 1-2 digit number, followed by a colon, follwed by a 2 digit number, Or a 1-2 digit number without a colon after it
            time_matches = re.findall(r'(\d{1,2}:\d{2}|\d{1,2})', txt)

            if len(time_matches) == 2:
                # time_matches_decimalized_minutes = [time_match.replace() for time_match in time_matches]
                # replace ':30' with '.5' to convert to decimal
                time_matches_decimalized_minutes = [time_match.replace(':30', '.5') for time_match in time_matches]
                hours = [float(hour) for hour in time_matches_decimalized_minutes]

                # assumes no show is > 12 hours in length
                duration_hours = hours[1] - hours[0] if hours[1] - hours[0] > 0 else hours[1] - hours[0] + 12
                
                duration_seconds = duration_hours * 60 * 60
        else:   
            duration_seconds = 0

            return int(duration_seconds)

if __name__ == '__main__':
    
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(CkutShowsSpider)
    process.start()