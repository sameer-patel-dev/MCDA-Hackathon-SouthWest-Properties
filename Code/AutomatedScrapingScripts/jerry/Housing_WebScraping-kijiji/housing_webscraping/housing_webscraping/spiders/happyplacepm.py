import scrapy
import urllib.parse
from src.exception import CustomException
import sys
from src.logger import logging
import datetime  

class HappyplacepmSpider(scrapy.Spider):
    name = "happyplacepm"
    allowed_domains = ["www.happyplacepm.com"]
    start_urls = ["https://www.happyplacepm.com/rentals/"]
    custom_settings = { 
        'DOWNLOAD_DELAY': 7,
        'FEED_URI': 'C:/Users/Administrator/Desktop/ScrapingScripts/jerry/CSV_FILES/happyplacepm.csv',
        'FEED_FORMAT': 'csv'
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.happyplacepm.com/rentals/',
            callback=self.parse,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
        )
    
    def parse(self, response):
        try :
            listings = response.xpath('//div[@class="listing-description"]//a/@href').extract()
            logging.info(f'Current URL : {response.url}')
            for listing in listings:
                yield response.follow(
                    url = listing, 
                    callback = self.parse_listing,
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
                )
            next_page_url = response.xpath('//a[@class="next page-numbers"]/@href').get()
            if next_page_url :
                yield response.follow(url = next_page_url, callback = self.parse, 
                        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
                )
        
        except Exception as e :
            logging.error(f'Error parsing response: {str(e)}')
            raise CustomException(e, sys)


    def parse_listing(self, response):
        try:
            item = {}
            item['title'] = response.xpath('//div[@class="col-sm-12"]/header[@class="article-header"]/h1/text()').get()
            item['address'] = response.xpath('normalize-space(//div[@class="col-sm-12"]/header[@class="article-header"]/div[@class="fullAddress"]/text())').get()
            item['price'] = response.xpath('normalize-space(//td[contains(@class, "details-label") and contains(text(), "Price")]/following-sibling::td[@class="detail-amount"]/text())').get()
            item['bedrooms'] = response.xpath('normalize-space(//td[contains(@class, "details-label") and contains(text(), "Bedrooms")]/following-sibling::td[@class="detail-amount"]/text())').get()
            item['bathrooms'] = response.xpath('normalize-space(//td[contains(@class, "details-label") and contains(text(), "Bathrooms")]/following-sibling::td[@class="detail-amount"]/text())').get()
            item['pets'] = response.xpath('normalize-space(//td[contains(@class, "details-label") and contains(text(), "Pets")]/following-sibling::td[@class="detail-amount"]/text())').get()
            item['description'] = response.xpath('normalize-space(//div[@class="panel panel-primary"]//div[@class="panel-body"])').get()
            item['available_date'] = response.xpath('normalize-space(//div[contains(@class, "panel-body") and preceding-sibling::div[@class="panel-heading"]="Date Available"])').get()
            item['extraction_date'] = datetime.date.today().strftime('%Y-%m-%d')

            yield item
    
        except Exception as e :
                logging.error(f'Error parsing response: {str(e)}')
                raise CustomException(e, sys)
