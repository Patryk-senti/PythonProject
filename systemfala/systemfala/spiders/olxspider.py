import scrapy
from scrapy_playwright.page import PageMethod
import logging


class OlxSpider(scrapy.Spider):
    name = "olxspider"
    allowed_domains = ["systemfala.pl"]
    start_urls = ["https://systemfala.pl/news/"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", ".row.m-n3"),
                        PageMethod("wait_for_timeout", 10000),
                    ],
                },
                callback=self.parse,
            )

    def parse(self, response):
        # Zapisanie pełnego kodu HTML do pliku dla weryfikacji
        with open("rendered_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        # Ekstrakcja linków do artykułów z atrybutu @click za pomocą CSS
        articles = response.css('div.border.p-4.rounded-sm::attr(@click)').getall()

        if not articles:
            self.log("No articles found!", level=logging.WARNING)
        else:
            self.log(f"Found {len(articles)} articles", level=logging.INFO)

        for article_click in articles:
            # Wyciąganie ścieżki URL z `window.location`
            relative_url = article_click.split("'")[
                1]  # Pobieranie ścieżki URL z @click="window.location = '/news/...'"
            full_url = response.urljoin(relative_url)  # Tworzenie pełnego URL

            yield response.follow(full_url, callback=self.parse_article)

    def parse_article(self, response):
        # Pobranie danych artykułu
        title = response.xpath('//h1/text()').get()
        content = response.xpath('//div[@class="article-content"]//text()').getall()
        content = ' '.join(content).strip()
        url = response.url

        # Zapis danych
        yield {
            'title': title,
            'content': content,
            'url': url,
        }
