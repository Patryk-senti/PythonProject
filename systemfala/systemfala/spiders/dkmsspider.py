import scrapy
import re
import os
import markdownify
from bs4 import BeautifulSoup


class DkmsspiderSpider(scrapy.Spider):
    name = "dkmsspider"
    allowed_domains = ["dkms.pl"]
    start_urls = ["https://dkms.pl"]

    output_folder = "dkms_scraped_articles"
    visited_urls = set()
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def parse(self, response):
        self.log(f"Visiting: {response.url}")
        links = response.xpath('//a/@href').getall()
        self.log(f"Found {len(links)} links on the page {response.url}")

        for link in links:
            absolute_url = response.urljoin(link)
            #  Pomijaj img
            if absolute_url not in self.visited_urls and not absolute_url.lower().endswith(self.image_extensions):
                self.visited_urls.add(absolute_url)
                self.log(f"Following new link: {absolute_url}")
                yield response.follow(absolute_url, callback=self.parse_help_article)

    def parse_help_article(self, response):
        title = response.xpath('//h1/text()').get()
        content_html = response.xpath('//div[@class="text-section text row"]').get()
        url = response.url

        if title and content_html:
            # Remove <img>
            soup = BeautifulSoup(content_html, "html.parser")
            for img_tag in soup.find_all("img"):
                img_tag.decompose()  # Remove image tags

            # Konwersja Markdown
            markdown_content = markdownify.markdownify(str(soup), heading_style="ATX")

            # Dzielenie na czesci (max 2000 znakow)
            chunk_size = 2000
            full_content = f"# {title}\n\n{markdown_content}\n\nLink: {url}\n"
            chunks = [full_content[i:i + chunk_size] for i in range(0, len(full_content), chunk_size)]
            num_parts = len(chunks)

            file_name_base = re.sub(r'[^\w\s]', '', title.replace(' ', '_'))

            # Zapisywanie w czesciach
            for idx, chunk in enumerate(chunks):
                part_number = idx + 1
                chunk_file_name = f"{file_name_base}_part_{part_number}.md"
                file_path = os.path.join(self.output_folder, chunk_file_name)

                # Tabelka Metadane
                split_info = f"Part {part_number} of {num_parts}" if num_parts > 1 else "Single Part"
                metadata_table = (
                    f"| **Title**       | **URL**           | **Part**              |\n"
                    f"|-----------------|-------------------|-----------------------|\n"
                    f"| {title}         | [{url}]({url})    | {split_info}          |\n\n"
                )

                # Metadane w kazdym pliku
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(metadata_table + chunk)
                    self.log(f"File {chunk_file_name} created successfully in {self.output_folder}")
        else:
            self.log(f"Skipping article due to missing title or content on {url}")

        links = response.xpath('//a/@href').getall()
        self.log(f"Found {len(links)} links on the article page {response.url}")

        for link in links:
            absolute_url = response.urljoin(link)
            # Pomijaj img w linkach
            if absolute_url not in self.visited_urls and not absolute_url.lower().endswith(self.image_extensions):
                self.visited_urls.add(absolute_url)
                self.log(f"Following new link: {absolute_url}")
                yield response.follow(absolute_url, callback=self.parse_help_article)
