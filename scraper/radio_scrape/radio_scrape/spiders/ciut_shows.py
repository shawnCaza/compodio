from re import findall

import scrapy

from radio_scrape.radio_scrape.items import ShowItem
from radio_scrape.radio_scrape.pipeline_definitions import show_pipelines
from radio_scrape.radio_scrape.spiders.ciut_helpers import show_name


class CiutShowsSpider(scrapy.Spider):
    name = "ciut_shows"
    custom_settings = {
        "ITEM_PIPELINES": show_pipelines(),
        "HTTPERROR_ALLOWED_CODES": [404],
    }
    allowed_domains = ["ciut.fm"]
    start_urls = ["https://ciut.fm/show-list/"]

    def parse(self, response):
        for show in response.xpath("//p/a/@href"):
            yield scrapy.Request(show.get(), callback=self.parse_show)

    def parse_show(self, response):

        if response.status == 404:
            return

        shows_to_skip = ["Rainbow Country", "Democracy Now", "Canadaland", "Shows"]

        current_show = ShowItem()

        current_show["showName"] = show_name(response)

        if any(skip_show in current_show["showName"] for skip_show in shows_to_skip):
            return

        current_show["img"] = self.img_url(response)

        current_show["desc"] = self.desc(response)

        host = response.xpath("//p/strong[contains(text(),'Host')]/text()").get()
        current_show["host"] = host.split(":")[1] if host != None else None
        current_show["internal_link"] = response.url
        current_show["ext_link"] = response.xpath(
            "//h1/../p[contains(text(),'Web')]/a/@href"
        ).get()
        email = response.xpath("//h1/../p[contains(text(),'Contact')]/a/@href").get()
        current_show["email"] = email.replace("mailto:", "") if email != None else None
        current_show["source"] = "ciut"

        try:
            sched = self.schedule(response)
            current_show["duration"] = self.calculate_duration(sched)
        except:
            current_show["duration"] = 0

        yield current_show

    def img_url(self, response) -> str | None:
        # Different pages use different methods to include images. bg img or img tag
        # check for bg image first, then img tag if bg image doesn't exist
        img_bg = response.xpath(
            "//div[contains(@style,'image') and contains(@style,'padding')]"
        ).get()
        img_wrapper = response.xpath(
            "//div[contains(@class,'image_wrapper')]/img/@data-src"
        ).get()
        img_wrapper_alt = response.xpath(
            "//div[contains(@class,'image_wrapper')]/img/@src"
        ).get()
        img_tag = response.xpath(
            "//div[@id='Content']//img[not (contains(@alt, 'parallax'))]/@data-src"
        ).get()

        if img_bg:
            # extract image link out of style definition
            img = img_bg.split("background-image:url(")[1].split(")")[0]
        elif img_wrapper:
            img = img_wrapper
        elif img_wrapper_alt:
            img = img_wrapper_alt
        elif img_tag:
            img = img_tag
        else:
            img = None

        return img

    def desc(self, response) -> str:
        # Meta tag is easy to get but not always accurate
        description = response.xpath("//meta[@name='description']/@content").get()
        description_verified = False

        if description and description != "":
            # Need to check this text is actually on the page

            # problem in scrapy seems to use xpath v1 with no ability to escape quotes. so we can't do:
            # escaped_description = description.replace("'","''")
            escaped_description = self.xpath_string_escape(description)

            description_verified = response.xpath(f"//p[text()={escaped_description}]")
            if description_verified:
                return response.xpath("//meta[@name='description']/@content").get()

        # if we're here description wasn't verified. Lets try to get it from the page
        if response.xpath("//h1/../p[string-length(text())>100][1]/text()").get():
            # Usually the first p tag after the header with lots of text. Want to skip any p tags that are just a few characters
            description = response.xpath(
                "string(//h1/../p[string-length(text())>100][1])"
            ).extract()[0]

        elif response.xpath("//h1/../div[string-length(text())>100][1]/text()").get():
            # if no p tag, then the first div with lots of text using text() approach
            description = response.xpath(
                "string(//h1/../div[string-length(text())>100][1])"
            ).extract()[0]

        elif len(response.xpath("string(//h1/../p[1])").extract()[0]) > 100:
            # If above failed, a sub tag may make the text seem short. So we can use string() to get all text in the p tag.
            # This just checks the first p tag, so it can be tripped up by empty p tags.
            description = response.xpath("string(//h1/../p[1])").extract()[0]

        elif len(response.xpath("string(//h1/../div[1])").extract()[0]) > 100:
            # if no p tag, then the first div with lots of text using string approach
            description = response.xpath("string(//h1/../div[1])").extract()[0]

        elif response.xpath("//p[string-length(text())>100][1]/text()").get():
            # Getting desprate. Maybe there's no header tag. Let's just grab the first p tag on the page with lots of text.
            description = response.xpath(
                "//p[string-length(text())>100][1]/text()"
            ).extract()[0]

        # If none of the above worked, then we will be returning unverified description from the meta tag
        # would be nice if the header descrition was reliable but sometimes it's copied from another show wihout being updated
        # TODO: could make sure header desc does not match any other show's description.
        if description == "Just another WordPress site":
            description = ""

        return description

    def schedule(self, response) -> str:
        return response.xpath(
            "//p/*[self::strong or self::b][contains(translate(text(), 'AM', 'am'),'am-') or contains(translate(text(), 'PM', 'pm'),'pm-')]/text()"
        ).get()

    def calculate_duration(self, sched) -> int:

        # create tuple of just the start and end hours for show (assumes all shows in schedule start on the hour.)
        hours = tuple(
            int(time) for time in findall(r"(\d{1,2})(?::00)?(?:\s)?(?:am|pm)", sched)
        )
        if len(hours) != 2:
            raise ValueError("Could not parse show schedule")

        # assumes no show is > 12 hours in length
        duration_hours = (
            hours[1] - hours[0] if hours[1] - hours[0] > 0 else hours[1] - hours[0] + 12
        )

        duration_seconds = duration_hours * 60 * 60

        return duration_seconds

    def xpath_string_escape(self, input_str) -> str:
        """creates a concatenation of alternately-quoted strings that is always a valid XPath expression"""
        if "'" in input_str:
            parts = input_str.split("'")
            return "concat('" + "', \"'\" , '".join(parts) + "', '')"
        else:
            return f"'{input_str}'"


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess(
        {"USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)"}
    )

    process.crawl(CiutShowsSpider)
    process.start()
