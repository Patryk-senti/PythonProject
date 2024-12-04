import scrapy
import re
import os
import markdownify
from bs4 import BeautifulSoup
import openai
import requests
import base64
from io import BytesIO

class DkmsspiderSpider(scrapy.Spider):
    name = "dkmsspider"
    allowed_domains = ["dkms.pl"]
    start_urls = ["https://dkms.pl"]

    output_folder = "dkms_scraped_articles"
    visited_urls = set()


    openai_api_key = os.getenv("OPENAI_API_KEY")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def parse(self, response):
        self.log(f"Visiting: {response.url}")
        links = response.xpath('//a/@href').getall()
        self.log(f"Found {len(links)} links on the page {response.url}")

        for link in links:
            if not link.startswith("http") and not link.startswith("/"):
                self.log(f"Skipping non-HTTP link: {link}")
                continue

            absolute_url = response.urljoin(link)
            if absolute_url not in self.visited_urls:
                self.visited_urls.add(absolute_url)
                self.log(f"Following new link: {absolute_url}")
                yield response.follow(absolute_url, callback=self.parse_help_article)

    def parse_help_article(self, response):
        title = response.xpath('//h1/text()').get()
        header_description = response.xpath('//p[@class="article-header__description typo-h4"]/text()').get()
        content_html = response.xpath('//div[@class="text-section text row"]').get()
        url = response.url

        if title and content_html:
            soup = BeautifulSoup(content_html, "html.parser")


            header_markdown = ""
            if header_description:
                header_markdown = f"## {header_description}\n\n"


            images = soup.find_all("img")
            if images:
                file_name_base = re.sub(r'[^\w\s]', '', title.replace(' ', '_'))
                image_descriptions_file = os.path.join(self.output_folder, f"{file_name_base}_images.md")

                with open(image_descriptions_file, 'w', encoding='utf-8') as image_file:
                    image_file.write(f"# Image Descriptions for: {title}\n\n")
                    image_file.write(f"**Article URL**: [{url}]({url})\n\n")


                    image_counter = 1
                    for img_tag in images:
                        img_url = img_tag.get("src")
                        if img_url and not img_url.startswith("data:image"):
                            absolute_img_url = response.urljoin(img_url)


                            description = self.get_image_caption_with_openai(absolute_img_url)

                            image_file.write(f"## Image {image_counter}\n")
                            image_file.write(f"- **Image URL**: {absolute_img_url}\n")
                            image_file.write(f"- **Description**: {description}\n\n")

                            self.log(f"Added description for Image {image_counter} in {file_name_base}_images.md")
                            image_counter += 1

            markdown_content = markdownify.markdownify(str(soup), heading_style="ATX")
            file_name_base = re.sub(r'[^\w\s]', '', title.replace(' ', '_'))
            article_file_name = f"{file_name_base}.md"
            article_file_path = os.path.join(self.output_folder, article_file_name)

            with open(article_file_path, 'w', encoding='utf-8') as f:

                f.write(f"---\n")
                f.write(f"title: \"{title}\"\n")
                f.write(f"url: \"{url}\"\n")
                f.write(f"---\n\n")

                f.write(f"# {title}\n\n{header_markdown}{markdown_content}\n")
                self.log(f"File {article_file_name} created successfully in {self.output_folder}")
        else:
            self.log(f"Skipping article due to missing title or content on {url}")

        links = response.xpath('//a/@href').getall()
        self.log(f"Found {len(links)} links on the article page {response.url}")

        for link in links:
            if not link.startswith("http") and not link.startswith("/"):
                self.log(f"Skipping non-HTTP link: {link}")
                continue

            absolute_url = response.urljoin(link)
            if absolute_url not in self.visited_urls:
                self.visited_urls.add(absolute_url)
                self.log(f"Following new link: {absolute_url}")
                yield response.follow(absolute_url, callback=self.parse_help_article)

    def get_image_caption_with_openai(self, image_url):
        """
        Image description by openai
        """
        try:
            # Download url
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            image = BytesIO(response.content)

            # encode into base 64
            base64_image = base64.b64encode(image.read()).decode("utf-8")
            data_url = f"data:image/jpeg;base64,{base64_image}"

            # OpenAI client
            client = openai.OpenAI(api_key=self.openai_api_key)

            # API
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this image in detail:"},
                            {"type": "image_url", "image_url": {"url": data_url}}
                        ],
                    }
                ],
            )

            # decoding answer
            if hasattr(completion, "choices") and len(completion.choices) > 0:
                description = completion.choices[0].message.content.strip()
                return description
            else:
                self.log(f"Response does not contain 'choices': {completion}")
                return "No description"

        except Exception as e:
            self.log(f"Error generating image caption with OpenAI: {e}")
            return "Brak opisu obrazu"

