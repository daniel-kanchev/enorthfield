import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from enorthfield.items import Article


class EnorthfieldSpider(scrapy.Spider):
    name = 'enorthfield'
    start_urls = ['https://www.enorthfield.com/resources']

    def parse(self, response):
        links = response.xpath('//div[@class="newsContent"]/a[2]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="newsdetailBlock"]//i/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="newsContent"]//text()').getall()
        content = [text for text in content if text.strip() and text.strip() != 'share']
        content = "\n".join(content).strip()

        if not content:
            return

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
