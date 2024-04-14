import scrapy
from src.exception import CustomException
import sys
from src.logger import logging
import re
import datetime  

class OlympusSpider(scrapy.Spider):
    name = "olympus"
    allowed_domains = ["www.olympusproperties.ca"]
    start_urls = ["https://www.olympusproperties.ca/available-units/"]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'FEED_URI': 'C:/Users/Administrator/Desktop/ScrapingScripts/jerry/CSV_FILES/olympus.csv',
        'FEED_FORMAT': 'csv'
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.olympusproperties.ca/available-units/',
            callback=self.parse,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
        )
    
    def parse(self, response):
        try :
            listings = response.xpath('//div[contains(@class, "col-md-6") and contains(@class, "has_prop_slider") and contains(@class, "listing_wrapper")]//div[@class="item active"]/a/@href').getall()
            logging.info(f'Current URL : {response.url}')
            for listing in listings:
                yield response.follow(
                    url = listing, 
                    callback = self.parse_listing,
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
                )
            next_page_url = response.xpath("//ul[@class='pagination pagination_nojax']/li[@class='roundright']/a/@href").get()
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
            item['address'] = response.xpath('//div[@id="collapseOne"]//div[@class="panel-body"]//div[@class="listing_detail col-md-4"][1]/strong/following-sibling::text()').get()
            city_element = response.xpath('//div[@class="panel-body"]//div[@class="listing_detail col-md-4"]/strong[text()="City:"]/following-sibling::a/text()').get()
            item['city'] = city_element.strip() if city_element else None
            area_element = response.xpath('//div[@class="panel-body"]//div[@class="listing_detail col-md-4"]/strong[text()="Area:"]/following-sibling::a/text()').get()
            item['area'] = area_element.strip() if area_element else None
            state_county_element = response.xpath('//div[@class="panel-body"]//div[@class="listing_detail col-md-4"]/strong[text()="State/County:"]/following-sibling::a/text()').get()
            item['state_county'] = state_county_element.strip() if state_county_element else None
            zip_code_element = response.xpath('//div[@class="panel-body"]//div[@class="listing_detail col-md-4"]/strong[text()="Zip:"]/following-sibling::text()').get()
            item['zip_code'] = zip_code_element.strip() if zip_code_element else None
            country_element = response.xpath('//div[@class="panel-body"]//div[@class="listing_detail col-md-4"]/strong[text()="Country:"]/following-sibling::text()').get()
            item['country'] = country_element.strip() if country_element else None

            price_elements = response.xpath('//div[@id="collapseOne"]//div[@class="listing_detail col-md-4"]/strong[text()="Price:"]/following-sibling::text()').getall()
            price = None

            for element in price_elements:
                # Remove leading and trailing whitespace and extract numeric characters
                cleaned_price = ''.join(filter(str.isdigit, element.strip()))
                if cleaned_price:
                    price = int(cleaned_price)
                    break  

            item['price'] = price
            property_id_element = response.xpath('//div[@id="collapseOne"]//div[@class="listing_detail col-md-4"]/strong[text()="Property Id :"]/following-sibling::text()').get()
            item['property_id'] = property_id_element.strip() if property_id_element is not None else None
            property_size_element = response.xpath('//div[@id="collapseOne"]//div[@class="listing_detail col-md-4"]/strong[text()="Property Size:"]/following-sibling::text()').get()
            item['property_size'] = property_size_element.strip() if property_size_element is not None else None
            rooms_element = response.xpath('//div[@id="collapseOne"]//div[@class="listing_detail col-md-4"]/strong[text()="Rooms:"]/following-sibling::text()').get()
            item['rooms'] = rooms_element.strip() if rooms_element is not None else None
            bedrooms_element = response.xpath('//div[@id="collapseOne"]//div[@class="listing_detail col-md-4"]/strong[text()="Bedrooms:"]/following-sibling::text()').get()
            item['bedrooms'] = bedrooms_element.strip() if bedrooms_element is not None else None
            bathrooms_element = response.xpath('//div[@id="collapseOne"]//div[@class="listing_detail col-md-4"]/strong[text()="Bathrooms:"]/following-sibling::text()').get()
            item['bathrooms'] = bathrooms_element.strip() if bathrooms_element is not None else None

            details = response.xpath('//div[@id="collapseThree"]//div[@class="panel-body"]//div[@class="listing_detail col-md-4"]/text()').getall()
            item['features'] = ', '.join(detail.strip() for detail in details if detail.strip())
            item['extraction_date'] = datetime.date.today().strftime('%Y-%m-%d')

            yield item
    
        except Exception as e :
                logging.error(f'Error parsing response: {str(e)}')
                raise CustomException(e, sys)
        
