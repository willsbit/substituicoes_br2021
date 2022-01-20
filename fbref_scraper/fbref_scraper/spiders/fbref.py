import scrapy
from scrapy import Request
from scrapy.linkextractors import LinkExtractor


class FbrefSpider(scrapy.Spider):
    name = 'fbref'
    # allowed_domains = ['https://fbref.com/pt/comps/24/cronograma/Serie-A-Resultados-e-Calendarios']
    start_urls = ['https://fbref.com/pt/comps/24/cronograma/Serie-A-Resultados-e-Calendarios/']

    def parse(self, response):
        for link in self.link_extractor.extract_links(response):
            yield Request(link.url, callback=self.parse)