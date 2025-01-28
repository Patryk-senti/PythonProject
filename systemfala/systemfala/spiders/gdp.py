import scrapy
from systemfala.items import CountryGdpItem


class GdpSpider(scrapy.Spider):
    name = "gdp"
    allowed_domains = ["wikipedia.org"]
    start_urls = ["https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"]

    def parse(self, response):
        for country in response.css('table.wikitable.sortable tbody tr:not([class])'):
            item = CountryGdpItem()

            item["country_name"] = country.css('td:nth-child(1) a::text').get()
            item["IMF_forecast"] = country.css('td:nth-child(2) ::text').get()
            item["year"] = country.css('td:nth-child(3) ::text').get()
            item["WorldBank_estimate"] = country.css('td:nth-child(4) ::text').get()


            yield item


