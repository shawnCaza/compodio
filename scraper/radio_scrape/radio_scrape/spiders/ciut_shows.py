from re import findall

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from radio_scrape.radio_scrape.items import ShowItem
from radio_scrape.radio_scrape.pipeline_definitions import show_pipelines


class CiutShowsSpider(scrapy.spiders.SitemapSpider):
    name = "ciut_shows"
    custom_settings = {
        "ITEM_PIPELINES": show_pipelines(),
        "HTTPERROR_ALLOWED_CODES": [404],
        # 'CLOSESPIDER_PAGECOUNT':10
    }
    allowed_domains = ["ciut.fm"]
    sitemap_urls = ["https://ciut.fm/page-sitemap.xml"]
    sitemap_rules = [("/shows-by-day/", "parse_show")]

    def parse_show(self, response):

        if response.status != 404:
            shows_to_skip = ["Rainbow Country", "Democracy Now", "Canadaland", "Shows"]

            current_show = ShowItem()

            # print(show.xpath(".//div[@class='links']/a[text()='archives']/@href").get())

            # Usually the show title is in the H1 tag
            if response.xpath("//h1/text()").get():
                current_show["showName"] = response.xpath("//h1/text()").get()
            else:
                # if no H1 tag, then let's try the title tag
                current_show["showName"] = (
                    response.xpath("//title/text()").get().split(" - ")[0]
                )

            print(current_show["showName"])
            if all(
                skip_show not in current_show["showName"] for skip_show in shows_to_skip
            ):

                # Different pages use different methods to include images. bg img or img tag
                # check for bg image first, then img tag if bg image doesn't exist
                img_bg = response.xpath(
                    "//div[contains(@style,'image') and contains(@style,'padding')]"
                ).get()
                img_wrapper = response.xpath(
                    "//div[contains(@class,'image_wrapper')]/img/@data-src"
                ).get()
                img_tag = response.xpath(
                    "//div[@id='Content']//img[not (contains(@alt, 'parallax'))]/@data-src"
                ).get()

                if img_bg:
                    # extract image link out of style definition
                    current_show["img"] = img_bg.split("background-image:url(")[
                        1
                    ].split(")")[0]
                elif img_wrapper:
                    current_show["img"] = img_wrapper
                elif img_tag:
                    current_show["img"] = img_tag
                else:
                    current_show["img"] = None

                # Meta tag is easy to get but not always accurate
                description = response.xpath(
                    "//meta[@name='description']/@content"
                ).get()

                if description and description != "":
                    # Need to check this text is actually on the page

                    # problem in scrapy seems to use xpath v1 with no ability to escape quotes. so we can't do:
                    # escaped_description = description.replace("'","''")
                    escaped_description = self.xpath_string_escape(description)

                    description_verified = response.xpath(
                        f"//p[text()={escaped_description}]"
                    )
                    print("verified", description_verified)
                    if description_verified:
                        current_show["desc"] = response.xpath(
                            "//meta[@name='description']/@content"
                        ).get()

                if not description or not description_verified:
                    # can we assume the first p tag with lots of text, in the same block as the heading, is the description?
                    header_description = description  # either unverified on none

                    if response.xpath(
                        "//h1/../p[string-length(text())>100][1]/text()"
                    ).get():
                        # Usually the first p tag after the header with lots of text. Want to skip any p tags that are just a few characters
                        description = response.xpath(
                            "string(//h1/../p[string-length(text())>100][1])"
                        ).extract()[0]

                    elif response.xpath(
                        "//h1/../div[string-length(text())>100][1]/text()"
                    ).get():
                        # if no p tag, then the first div with lots of text using text() approach
                        description = response.xpath(
                            "string(//h1/../div[string-length(text())>100][1])"
                        ).extract()[0]

                    elif len(response.xpath("string(//h1/../p[1])").extract()[0]) > 100:
                        # If above failed, a sub tag may make the text seem short. So we can use string() to get all text in the p tag.
                        # This just checks the first p tag, so it can be tripped up by empty p tags.
                        description = response.xpath("string(//h1/../p[1])").extract()[
                            0
                        ]

                    elif (
                        len(response.xpath("string(//h1/../div[1])").extract()[0]) > 100
                    ):
                        # if no p tag, then the first div with lots of text using string approach
                        description = response.xpath(
                            "string(//h1/../div[1])"
                        ).extract()[0]

                    if not description:
                        # would be nice if the header descrition was reliable but sometimes it's copied from another show wihout being updated
                        # TODO: could make sure header desc does not match any other show's description.
                        description = header_description

                current_show["desc"] = description

                host = response.xpath(
                    "//p/strong[contains(text(),'Host')]/text()"
                ).get()
                current_show["host"] = host.split(":")[1] if host != None else None
                current_show["internal_link"] = response.url
                current_show["ext_link"] = response.xpath(
                    "//h1/../p[contains(text(),'Web')]/a/@href"
                ).get()
                email = response.xpath(
                    "//h1/../p[contains(text(),'Contact')]/a/@href"
                ).get()
                current_show["email"] = (
                    email.replace("mailto:", "") if email != None else None
                )
                current_show["source"] = "ciut"

                schedule = response.xpath(
                    "//p/strong[contains(text(),'0am') or contains(text(),'0pm') ]/text()"
                ).get()
                current_show["duration"] = self.calculate_duration(schedule)

                yield current_show

        else:
            print("**** 404 error ***")

    def calculate_duration(self, schedule):

        # create tuple of just the start and end hours for show (assumes all shows in schedule start on the hour.)
        hours = tuple(int(hour) for hour in findall(r"([0-9]+):00", schedule))

        # assumes no show is > 12 hours in length
        duration_hours = (
            hours[1] - hours[0] if hours[1] - hours[0] > 0 else hours[1] - hours[0] + 12
        )

        duration_seconds = duration_hours * 60 * 60

        return duration_seconds

    def xpath_string_escape(self, input_str):
        """creates a concatenation of alternately-quoted strings that is always a valid XPath expression"""
        if "'" in input_str:
            parts = input_str.split("'")
            return "concat('" + "', \"'\" , '".join(parts) + "', '')"
        else:
            return f"'{input_str}'"
