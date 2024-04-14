import scrapy
from src.exception import CustomException
import sys
from src.logger import logging
import datetime  

class NorthpointSpider(scrapy.Spider):
    name = "northpoint"
    allowed_domains = ["rentinhalifax.com"]
    start_urls = ["https://rentinhalifax.com/available-units/"]

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'FEED_URI': 'C:/Users/Administrator/Desktop/ScrapingScripts/jerry/CSV_FILES/northpoint.csv',
        'FEED_FORMAT': 'csv'
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://rentinhalifax.com/available-units/',
            callback=self.parse,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
        )
    
    def parse(self, response):
        try :
            listings = response.xpath('//div[@class="right custom-card"]/a/@href').extract()
            logging.info(f'Current URL : {response.url}')
            for listing in listings:
                yield response.follow(
                    url = listing, 
                    callback = self.parse_listing,
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
                )
            next_page_url = response.xpath('//div[@class="paging-properties"]//a[@class="nextpostslink"]/@href').get()

            if next_page_url :
                yield response.follow(url = next_page_url, callback = self.parse, 
                        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
                )
        
        except Exception as e :
            logging.error(f'Error parsing response: {str(e)}')
            raise CustomException(e, sys)
        
    def parse_listing(self, response):
        try:
            listings = response.xpath('//div[@class="inner-wrap inner" and h6="Available Units"]/ul/li')

            for listing in listings:
                item = {}
                item['title'] = listing.xpath('normalize-space(.//p[@class="unit_title"]/text())').get().replace('Unit ', '')
                item['price'] = listing.xpath('normalize-space(substring-after(.//p[@class="unit_price"]/text(), "$"))').get()
                item['apartment_details'] = listing.xpath('normalize-space(substring-after(.//p[@class="unit_bedroom"]/text(), ":"))').get()
                item['address'] = listing.xpath('normalize-space(.//p[@class="unit_address"]/text()[2])').get()
                item['available_month'] = listing.xpath('normalize-space(substring-after(.//p[@class="unit_availablemonth"]/text(), ":"))').get()
                item['extraction_date'] = datetime.date.today().strftime('%Y-%m-%d')

                yield item
                    
        except Exception as e:
            logging.error(f'Error parsing response: {str(e)}')
            raise CustomException(e, sys)


        
