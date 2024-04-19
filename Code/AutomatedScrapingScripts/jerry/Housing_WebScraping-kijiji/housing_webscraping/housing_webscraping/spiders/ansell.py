import scrapy
from src.exception import CustomException
import sys
from src.logger import logging
import datetime  

class AnsellSpider(scrapy.Spider):
    name = "ansell"
    allowed_domains = ["www.ansellproperties.ca"]
    start_urls = ["https://www.ansellproperties.ca/rental/"]

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'FEED_URI': 'C:/Users/Administrator/Desktop/ScrapingScripts/jerry/CSV_FILES/ansell.csv',
        'FEED_FORMAT': 'csv'
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.ansellproperties.ca/rental/',
            callback=self.parse,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
        )

    def parse(self, response):
        try :
            listings = response.xpath('//div[@class="entry-content"]//a/@href').getall()
            logging.info(f'Current URL : {response.url}')
            for listing in listings:
                yield response.follow(
                    url = listing, 
                    callback = self.parse_listing,
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
                )
            next_page_url = response.xpath('//div[@class="alignright"]/a/@href').get()
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
            street = response.xpath('//h1[@class="entry-title"]/span[@class="item-street"]/text()').get()
            suburb, state, postcode = response.xpath('//h1[@class="entry-title"]/span[@class="entry-title-sub"]/span/text()').getall()
            item['address'] = f"{street.strip()}, {suburb.strip()}, {state.strip()}, {postcode.strip()}"
            bedrooms = response.xpath('//span[@title="Bedrooms"]/span[@class="icon-value"]/text()').get()
            bathrooms = response.xpath('//span[@title="Bathrooms"]/span[@class="icon-value"]/text()').get()
            parking_spaces = response.xpath('//span[@title="Parking Spaces"]/span[@class="icon-value"]/text()').get()
            air_conditioning = response.xpath('//span[@title="Air Conditioning"]')

            item['bedrooms'] = bedrooms.strip() if bedrooms else "None"
            item['bathrooms'] = bathrooms.strip() if bathrooms else "None"
            item['parking_spaces'] = parking_spaces.strip() if parking_spaces else "None"
            item['air_conditioning'] = "Yes" if air_conditioning else "No"
            item['rent'] = response.xpath('//span[@class="page-price"]/text()').get()
            item['availability'] = response.xpath('//div[@class="property-meta date-available"]/text()').get()
            feature_elements = response.xpath('//div[@class="epl-tab-content tab-content"]//ul[@class="epl-property-features listing-info epl-tab-3-columns"]/li')
            item['feature'] = ', '.join(feature_elements.xpath('normalize-space(.)').getall())
            item['description'] = response.xpath('//div[@class="tab-content"]/div/text()').getall()
            item['extraction_date'] = datetime.date.today().strftime('%Y-%m-%d')

            yield item
    
        except Exception as e :
                logging.error(f'Error parsing response: {str(e)}')
                raise CustomException(e, sys)
        
