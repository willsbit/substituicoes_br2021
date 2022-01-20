import scrapy


class LivescoreSpider(scrapy.Spider):
    name = 'livescore'
    allowed_domains = ['https://www.livescore.com/en/football/brazil/serie-a/results/']
    start_urls = ['http://https://www.livescore.com/en/football/brazil/serie-a/results//']

    def parse(self, response):
        pass
