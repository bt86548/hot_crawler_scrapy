import scrapy
from turtorial.items import DmozItem

class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ['dmoz.org']
    start_urls = [
        "https://dmoz-odp.org/Computers/Programming/Languages/Python/Books/",
        "https://dmoz-odp.org/Computers/Programming/Languages/Python/Resources/"
        ]
    def parse(self,response): #存入位置,產生Books跟Resources的檔案
        sel = scrapy.selector.Selector(response)
        sites = sel.xpath('//ul[@class="social-link"]/li')
        items = []
        for site in sites:
            item = DmozItem()
            item['title'] = site.xpath('a/text()').extrcat()
            item['link'] = site.xpath('a/@href').extract()
            item['desc'] = site.xpath('text()').extract()
            items.append(item)

        return items
