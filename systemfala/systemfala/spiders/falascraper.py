import scrapy


class FalascraperSpider(scrapy.Spider):
    name = "falascraper"
    allowed_domains = ["systemfala.pl"]
    start_urls = ["https://systemfala.pl"]

    def parse(self, response):
        pass
