# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CountryGdpItem(scrapy.Item):
    country_name = scrapy.Field()
    IMF_forecast= scrapy.Field()
    year = scrapy.Field()
    WorldBank_estimate = scrapy.Field()
    pass
