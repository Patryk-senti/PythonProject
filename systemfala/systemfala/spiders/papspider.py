import scrapy
import os
import re
import markdownify
from bs4 import BeautifulSoup

class PapSpider(scrapy.Spider):
    name = "papspider"
    allowed_domains = ["pap.pl"]
    start_urls = ["https://pap.pl"]

    output_folder = "pap_scraped_articles"
    visited_urls = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def parse(self, response):
        self.log(f"Visiting: {response.url}")
        links = response.xpath('//a/@href').getall()

        for link in links:
            if link.startswith(('mailto:', 'tel:')) or link.endswith(('.pdf', '.jpg', '.png', '.gif', '.zip')):
                continue

            absolute_url = response.urljoin(link)
            if absolute_url not in self.visited_urls:
                self.visited_urls.add(absolute_url)
                yield response.follow(absolute_url, callback=self.parse_article)

    def parse_article(self, response):
        title = response.xpath('//h1/text() | //title/text()').get()
        content_html = ''.join(response.xpath('//div[contains(@class, "content") or @property="schema:text"]').getall() or "")

        if not title or not content_html:
            self.log(f"Skipping page {response.url} due to missing title or content")
            return

        soup = BeautifulSoup(content_html, "html.parser")
        markdown_content = markdownify.markdownify(str(soup), heading_style="ATX")

        file_name_base = re.sub(r'[^\w\s]', '', title.replace(' ', '_'))[:100] if title else "untitled"
        article_file_name = f"{file_name_base}.md"
        article_file_path = os.path.join(self.output_folder, article_file_name)

        with open(article_file_path, 'w', encoding='utf-8') as f:
            f.write(f"---\n")
            f.write(f"title: \"{title}\"\n")
            f.write(f"url: \"{response.url}\"\n")
            f.write(f"---\n\n")
            f.write(f"# {title}\n\n{markdown_content}\n")

        self.log(f"Saved article: {article_file_name}")

        links = response.xpath('//a/@href').getall()
        for link in links:
            if link.startswith(('mailto:', 'tel:')) or link.endswith(('.pdf', '.jpg', '.png', '.gif', '.zip')):
                continue

            absolute_url = response.urljoin(link)
            if absolute_url not in self.visited_urls:
                self.visited_urls.add(absolute_url)
                yield response.follow(absolute_url, callback=self.parse_article)
