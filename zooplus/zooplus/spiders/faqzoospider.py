import re
import scrapy


class FaqzoospiderSpider(scrapy.Spider):
    name = "faqzoospider"
    allowed_domains = ["support.zooplus.pl"]
    start_urls = ["https://support.zooplus.pl/pl/support/home"]

    def parse(self, response):
        # Linki kategorii na stronie głównej
        categories = response.xpath('//div[@class="card card--animated center articleSection"]/a/@href').getall()
        for category in categories:
            yield response.follow(category, callback=self.parse_category)

    def parse_category(self, response):
        # Znajdź wszystkie artykuły
        articles =  response.xpath('//ul[@class="article-list"]/a/@href').getall()
        for article in articles:
            yield response.follow(article, callback=self.parse_article)


    def parse_article(self, response):

        # Czyszczenie tekstu
        tekst = response.xpath('//article/p/text()').getall()
        tekst = ' '.join(tekst).strip()

        title = response.xpath('//h2/text()').get()

        # Usuwam niepotrzebne znaki
        tekst = tekst.replace('\n', ' ').replace('\xa0', ' ').strip()
        tekst = re.sub(r'\s+', ' ', tekst)


        # Rozdzielanie słów sklejonych przez usunięcie spacji
        title = re.sub(r'\s+', ' ', title).strip()


        # Dane artykułów
        yield {
            'title': title,
            'tekst': tekst,
            'url': response.url,
        }
