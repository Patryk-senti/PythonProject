# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re


class ZooplusPipeline:
    def process_item(self, item, spider):
        return item

class MarkdownPipeline:
    def process_item(self, item, spider):
        # Sprawdzenie, który spider przetwarza dane
        if spider.name == "zoospider":
            # Przetwarzanie danych zoospider
            markdown_output = (
                f"### {item['name']}\n\n"
                f"**URL:** [{item['url']}]({item['url']})\n\n"
                f"**Price:** {item['price']} {item['price per kg']}\n\n"
                f"**Description:**\n{item['description']}\n\n"
                f"**Ingredients:**\n{item['ingredients']}\n"
            )
            file_name = f"{item['name'].replace(' ', '_')}.md"

        elif spider.name == "faqzoospider":
            # Przetwarzanie danych faqzoospider
            markdown_output = (
                f"# {item['title']}\n\n"
                f"**URL:** [{item['url']}]({item['url']})\n\n"
                f"**Content:**\n\n{item['tekst']}\n"
            )
            file_name = re.sub(r'[^\w\s]', '', item['title'].replace(' ', '_')) + ".md"

        else:
            # Jeśli dane pochodzą od innego spidera, możemy je zignorować lub zwrócić bez przetwarzania
            return item

        # Zapisywanie pliku Markdown
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(markdown_output)
                print(f"File {file_name} created successfully.")
        except Exception as e:
            print(f"Error saving file {file_name}: {e}")

        return item