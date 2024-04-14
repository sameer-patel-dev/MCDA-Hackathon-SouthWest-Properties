import scrapy
from urllib.parse import urljoin
from src.exception import CustomException
import sys
from src.logger import logging
import re
import datetime  

class PagepmSpider(scrapy.Spider):
    name = "pagepm"
    allowed_domains = ["pagepm.ca"]
    start_urls = ["https://pagepm.ca/residential-properties"]
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'FEED_URI': 'C:/Users/Administrator/Desktop/ScrapingScripts/jerry/CSV_FILES/pagepm.csv',
        'FEED_FORMAT': 'csv'
    }
    
    def start_requests(self):
        yield scrapy.Request(
            url='https://pagepm.ca/residential-properties',
            callback=self.parse,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
        )

    def parse(self, response):
        try :
            listings = response.xpath('//div[@class="col-md-6 col-sm-12 properties-grid views-row"]//a[@hreflang="en"]/@href').getall()
            logging.info(f'Current URL : {response.url}')
            for listing in listings:
                full_url = urljoin(response.url, listing)
                yield response.follow(
                    url = full_url, 
                    callback = self.parse_listing,
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
                )

        except Exception as e :
            logging.error(f'Error parsing response: {str(e)}')
            raise CustomException(e, sys)
        
    def parse_listing(self, response):
        try:
            listings = response.xpath('//div[@class="view-content"]//table[contains(@class, "views-table")]//tbody//tr')

            for listing in listings:
                item = {}
                item['description'] = listing.xpath('.//td[contains(@class, "views-field-field-unit-description")]/text()').get()
                rent_text = listing.xpath('.//td[contains(@class, "views-field-field-rent")]/text()').get()
                rent_number = None

                if rent_text:
                    rent_match = re.search(r'\d+', rent_text)
                    if rent_match:
                        rent_number = rent_match.group()

                item['rent'] = rent_number

                sqft_text = listing.xpath('.//td[contains(@class, "views-field-field-sq")]/text()').get()
                sq_ft_number = None

                if sqft_text:
                    sq_ft_match = re.search(r'\d+', sqft_text)
                    if sq_ft_match:
                        sq_ft_number = sq_ft_match.group()

                item['sq_ft'] = sq_ft_number

                item['availability'] = listing.xpath('.//td[contains(@class, "views-field-field-availability")]/text()').get()
                
                amenities_list = response.xpath('//div[@class="item-list"]/ul//text()').getall()
                cleaned_amenities = [amenity.strip() for amenity in amenities_list if amenity.strip()]
                item['amenities'] = ', '.join(cleaned_amenities)
                item['extraction_date'] = datetime.date.today().strftime('%Y-%m-%d')

                yield item
                    
        except Exception as e:
            logging.error(f'Error parsing response: {str(e)}')
            raise CustomException(e, sys)

        
