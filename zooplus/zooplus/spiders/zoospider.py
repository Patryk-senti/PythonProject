import re

import scrapy

class ZoospiderSpider(scrapy.Spider):
    name = "zoospider"
    allowed_domains = ["zooplus.pl"]
    start_urls = ["https://www.zooplus.pl/"]

    def parse(self, response):
        # Linki do podkategorii na stronie głównej
        subcategories = response.xpath('//a[contains(@class,"LeftNavigationList_navigationLink")]/@href').getall()
        for subcategory in subcategories:
            yield response.follow(subcategory, callback=self.parse_category)

    def parse_category(self, response):
        # Linki do stron z produktami
        products = response.xpath('//div[contains(@class,"ProductListItem_productRow")]')
        for product in products:
            relative_url = product.xpath('.//a[@data-zta="product-link"]/@href').get()
            yield response.follow(relative_url, callback=self.parse_product_page)

        # Pejdzowanie na stronie z produktami
        next_page = response.xpath('//a[@data-zta="paginationNext"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_category)

    def parse_product_page(self, response):

        #Czyszczenie tekstu
        description = response.xpath('//div[@id="description"]//text()').getall()
        description = ' '.join(description).strip()

        ingridients = response.xpath('//div[@id="ingredients"]//div/text()').getall()
        ingridients = ' '.join(ingridients).strip()

        #Usuwam niepotrzebne znaki
        description = description.replace('\n', ' ').replace('\xa0',' ').strip()
        ingridients = ingridients.replace('\n', ' ').replace('\xa0',' ').strip()

        #Usuwam białe znaki
        description = re.sub(r'\s+',' ', description)
        ingridients = re.sub(r'\s+',' ', ingridients)

        # Zbieranie danych
        yield {
            'url': response.url,
            'name': response.xpath('//h1/text()').get(),
            'description': description,
            'ingredients': ingridients,
            'price': response.xpath('//span[@data-zta="productStandardPriceAmount"]/text()').get(),
            'price per kg': response.xpath('//span[@data-zta="productStandardPriceSuffix"]/text()').get(),
        }
