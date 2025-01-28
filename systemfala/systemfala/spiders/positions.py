import scrapy
from scrapy_playwright.page import PageMethod


class PositionsSpider(scrapy.Spider):
    name = "positions"
    allowed_domains = ["myworkdayjobs.com"]
    start_urls = ["https://trafigura.wd3.myworkdayjobs.com/TrafiguraCareerSite"]

    def start_requests(self):
        yield scrapy.Request(
            self.start_urls[0],
            meta=dict(
                playwright=True,
                playwright_page_methods=[
                    PageMethod("wait_for_selector", 'ul[role="list"] > li'),
                ],
            ),
            callback=self.parse,
        )

    async def parse(self, response):
        # Scrapowanie danych z bieżącej strony
        for job in response.css('ul[role="list"] > li'):
            yield {
                'title': job.css('h3 a::text').get(),
                'location': job.css('div[data-automation-id="locations"] dd::text').get(),
            }

        # Obsługa paginacji: kliknięcie „Next”, jeśli przycisk istnieje
        next_button = response.css('button[aria-label="next"]')
        if next_button:
            self.logger.info("Next button found! Navigating to the next page.")

            # Kliknij „Next” i czekaj na załadowanie nowych danych
            yield scrapy.Request(
                response.url,
                meta=dict(
                    playwright=True,
                    playwright_page_methods=[
                        PageMethod("click", 'button[aria-label="next"]'),  # Kliknij przycisk
                        PageMethod("wait_for_selector", 'ul[role="list"] > li'),  # Czekaj na wyniki
                    ],
                ),
                callback=self.parse,
                            )
        else:
            self.logger.info("No Next button found. Scraping complete.")
