import scrapy
import re
import os
import markdownify


class FalascraperSpider(scrapy.Spider):
    name = "falascraper"
    allowed_domains = ["systemfala.pl"]
    start_urls = ["https://systemfala.pl/help/"]

    # Nazwa folderu, w którym będą zapisywane pliki
    output_folder = "scraped_articles"

    def __init__(self):
        # Tworzenie folderu, jeśli nie istnieje
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def parse(self, response):
        # Znalezienie linków do poszczególnych artykułów na bieżącej stronie
        links = response.xpath('//article/a/@href').getall()

        for link in links:
            yield response.follow(link, callback=self.parse_article_links)

    def parse_article_links(self, response):
        # Znalezienie linków do artykułów na podstronach
        article_links = response.xpath('//article/a/@href').getall()

        for article_link in article_links:
            yield response.follow(article_link, callback=self.parse_help_article)

    def parse_help_article(self, response):
        # Pobranie danych artykułów
        title = response.xpath('//main//h1/text()').get()
        content_html = response.xpath('//main/section').get()
        url = response.url

        # Konwersja HTML na Markdown
        markdown_content = markdownify.markdownify(content_html, heading_style="ATX")

        # Tworzenie nazwy pliku
        file_name = re.sub(r'[^\w\s]', '', title.replace(' ', '_')) + ".md"
        file_path = os.path.join(self.output_folder, file_name)

        # Zapis danych do pliku Markdown w nowym folderze
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n{markdown_content}\n\nLink: {url}\n")
            self.log(f"File {file_name} created successfully in {self.output_folder}")
