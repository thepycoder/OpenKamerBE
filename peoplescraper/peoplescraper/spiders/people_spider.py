import re
import scrapy


class LinkSpider(scrapy.Spider):
    name = "people_spider"
    start_urls = [
        "https://www.dekamer.be/kvvcr/showpage.cfm?section=/depute&language=nl&cfm=/site/wwwcfm/depute/cvlist54.cfm"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                self.parse,
                headers=self.headers,
            )

    def parse(self, response):
        # Extract all links and yield requests to scrape data from them
        for href in response.css("td:nth-child(1) > a::attr(href)").getall():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_link, headers=self.headers)

    def parse_link(self, response):
        # This function will scrape data from each linked page
        # You can customize what data to scrape here
        short_description = response.css("td > p::text").get().strip()

        # Fractie regex
        regex = r"(?<=\()[\*&\w\s-]+(?=\))"
        result = re.search(regex, short_description)
        if result:
            fraction = result.group(0)
        else:
            fraction = "N/A"

        # Birthyear
        regex = r"op (\d{1,2} \w+ \d{4})"
        result = re.search(regex, short_description)
        if result:
            birthyear = result.group(1)
        else:
            birthyear = "N/A"

        yield {
            "name": response.css("center > h2::text").get(),
            "image_url": response.css("td > img::attr(src)").get(),
            "fraction": fraction,
            "birthyear": birthyear,
        }
