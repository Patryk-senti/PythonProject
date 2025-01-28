import scrapy
from scrapy_playwright.page import PageMethod

class SteamSpecialsSpider(scrapy.Spider):
    name = "steam_specials"
    allowed_domains = ["steampowered.com"]
    start_urls = ["https://store.steampowered.com/specials"]

    def start_requests(self):
        yield scrapy.Request(
            self.start_urls[0],
            meta=dict(
                playwright=True,
                playwright_page_methods=[
                    PageMethod("wait_for_selector", 'div[class="gASJ2lL_xmVNuZkWGvrWg"]'),
                    PageMethod("evaluate", """
                        const interval_id = setInterval(function() {
                            const button = document.querySelector('div[class="_36qA-3ePJIusV1oKLQep-w"] > button');
                            if (button) { 
                                button.scrollIntoView();
                                button.click();
                            } else {
                                clearInterval(interval_id);
                            }
                        }, 2000);"""),
                    PageMethod("wait_for_selector", 'div[class="_36qA-3ePJIusV1oKLQep-w"] > button', state="detached"),
                   ]
            )
        )

    async def parse(self, response):
        # Scrapowanie danych z bieżącej strony
        for offer in response.xpath('//div[@class="ImpressionTrackedElement"]//div[contains(@class,"Panel Focusable")]'):
            yield {
                'title': offer.xpath('.//div[contains(@class,"StoreSaleWidgetTitle")]/text()').get(),
                'price': offer.xpath('.//div[contains(@class,"Discounted")]/div[2]/text()').get(),
                'ReviewScore': offer.xpath('.//a[contains(@class,"ReviewScore Focusable")]/div/div[1]/text()').get(),
            }