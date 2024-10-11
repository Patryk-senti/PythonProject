import scrapy
import re
import os
import markdownify


class DkmsspiderSpider(scrapy.Spider):
    name = "dkmsspider"
    allowed_domains = ["dkms.pl"]
    start_urls = ["https://dkms.pl"]

    # Nazwa folderu, w którym będą zapisywane pliki
    output_folder = "dkms_scraped_articles"

    # Zbiór do przechowywania odwiedzonych linków (dla uniknięcia duplikatów)
    visited_urls = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tworzenie folderu, jeśli nie istnieje
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def parse(self, response):
        # Logowanie odwiedzonej strony
        self.log(f"Visiting: {response.url}")

        # Znalezienie wszystkich linków na bieżącej stronie
        links = response.xpath('//a/@href').getall()

        # Logowanie znalezionych linków
        self.log(f"Found {len(links)} links on the page {response.url}")

        for link in links:
            absolute_url = response.urljoin(link)

            # Sprawdzanie, czy link jest już odwiedzony
            if absolute_url not in self.visited_urls:
                self.visited_urls.add(absolute_url)
                self.log(f"Following new link: {absolute_url}")
                yield response.follow(absolute_url, callback=self.parse_help_article)

    def parse_help_article(self, response):
        # Pobranie danych artykułów
        title = response.xpath('//h1/text()').get()
        content_html = response.xpath('//div[@class="text-section text row"]').get()
        url = response.url

        if title and content_html:
            # Konwersja HTML na Markdown
            markdown_content = markdownify.markdownify(content_html, heading_style="ATX")

            # Tworzenie nazwy pliku
            file_name = re.sub(r'[^\w\s]', '', title.replace(' ', '_')) + ".md"
            file_path = os.path.join(self.output_folder, file_name)

            # Zapis danych do pliku Markdown w nowym folderze
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n{markdown_content}\n\nLink: {url}\n")
                self.log(f"File {file_name} created successfully in {self.output_folder}")
        else:
            self.log(f"Skipping article due to missing title or content on {url}")

        # Po przetworzeniu artykułu, pobierz nowe linki i spróbuj je odwiedzić
        links = response.xpath('//a/@href').getall()
        self.log(f"Found {len(links)} links on the article page {response.url}")

        for link in links:
            absolute_url = response.urljoin(link)

            # Sprawdzanie, czy link jest już odwiedzony
            if absolute_url not in self.visited_urls:
                self.visited_urls.add(absolute_url)
                self.log(f"Following new link: {absolute_url}")
                yield response.follow(absolute_url, callback=self.parse_help_article)
