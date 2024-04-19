import scrapy
import urllib.parse
from src.exception import CustomException
import sys
from src.logger import logging
import datetime  

class KijijiSpider(scrapy.Spider):
    name = "kijiji"
    allowed_domains = ["www.kijiji.ca"]
    start_urls = ["https://www.kijiji.ca/b-apartments-condos/city-of-halifax/apartment/k0c37l1700321?sort=dateDesc&radius=50.0&ad=offer&address=Halifax+Regional+Municipality%2C+NS&ll=44.6475811%2C-63.5727683"]

    custom_settings = {
        'DOWNLOAD_DELAY': 15,
        'FEED_URI': 'C:/Users/Administrator/Desktop/ScrapingScripts/jerry/CSV_FILES/kijiji.csv',
        'FEED_FORMAT': 'csv'
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.kijiji.ca/b-apartments-condos/city-of-halifax/apartment/k0c37l1700321?sort=dateDesc&radius=50.0&ad=offer&address=Halifax+Regional+Municipality%2C+NS&ll=44.6475811%2C-63.5727683',
            callback=self.parse,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
        )
    
    def parse(self, response):
        try :
            listings = response.xpath("//div[@class='sc-63c588db-0 fEeWHy']/ul/li")
            logging.info(f'Current URL : {response.url}')
            for listing in listings:
                link = listing.xpath('.//h3/a/@href').get()
                yield response.follow(
                    url = link, 
                    callback = self.parse_listing,
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
                )
            next_page_url = response.xpath('//div[@class="sc-fa75c125-0 YhqUg"]//a[contains(@class, "sc-6b17eca1-0 laaUHx sc-4c795659-3 garPwt") and contains(@href, "http")]/@href').get()
            if next_page_url :
                yield response.follow(url = next_page_url, callback = self.parse, 
                        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0'}
                )
        
        except Exception as e :
            logging.error(f'Error parsing response: {str(e)}')
            raise CustomException(e, sys)


    def parse_listing(self, response):
        try :
            title = response.xpath("//h1[@class='title-4206718449']/text()").get()
            rent_with_symbol = response.xpath('//span[@content]/text()').get()
            if rent_with_symbol:
                rent = rent_with_symbol.replace('$', '').replace(',', '')
            else:
                rent = None
            
            address = response.xpath('//div[@class="locationContainer-1255831218"]/text()').get()
            if address is None:
                address = response.xpath('//span[@class="address-2094065249"]/text()').get()        
            date_posted = response.xpath('//div[@class="datePosted-1776470403"]/time/@datetime').get()
            if date_posted is None:
                date_posted = response.xpath('//div[@class="datePosted-1776470403"]/span/@title').get()

            how_long = response.xpath('//div[@class="datePosted-1776470403"]/time/text()').get()
            if how_long is None:
                how_long = response.xpath('//div[@class="datePosted-1776470403"]/span/text()').get()

            unit_type = response.xpath('//span[preceding-sibling::svg[@class="icon-2308439956 attributeIcon-544566124 attributeIcon__condensed-2733727630"]]/text()').get()
            bedrooms_element = response.xpath('//span[contains(text(), "Bedrooms")]/text()').get()
            bedrooms = None 
            if bedrooms_element:
                bedrooms = bedrooms_element.split(':')[-1].strip()
            bathrooms_element = response.xpath('//span[contains(text(), "Bathrooms")]/text()').get()
            bathrooms = None
            if bathrooms_element:
                bathrooms = bathrooms_element.split(':')[-1].strip()
            utilities = response.xpath('//h4[text()="Utilities Included"]/following-sibling::ul/li[.//svg[contains(@aria-label, "Yes")]]/text()').getall()
            wifi_and_more = response.xpath('//h4[text()="Wi-Fi and More"]/following-sibling::ul/text()').get()
            parking = response.xpath('//dt[text()="Parking Included"]/following-sibling::dd/text()').get()
            agreement = response.xpath('//dt[text()="Agreement Type"]/following-sibling::dd/text()').get()
            pet_friendly = response.xpath('//dt[text()="Pet Friendly"]/following-sibling::dd/text()').get()
            size = response.xpath('//dt[text()="Size (sqft)"]/following-sibling::dd/text()').get()
            furnished = response.xpath('//dt[text()="Furnished"]/following-sibling::dd/text()').get()
            appliances = response.xpath('//h4[text()="Appliances"]/following-sibling::ul/li/text()').getall()
            air_conditioning = response.xpath('//dt[text()="Air Conditioning"]/following-sibling::dd/text()').get()
            personal_space = response.xpath('//h4[text()="Personal Outdoor Space"]/following-sibling::ul/li/text()').getall()
            smoking = response.xpath('//dt[text()="Smoking Permitted"]/following-sibling::dd/text()').get()
            amenities = response.xpath('//h4[text()="Amenities"]/following-sibling::ul/li/text()').getall()
            seller = response.xpath('//div[@class="line-794739306"]/text()').get()
            seller_website = response.xpath('//div[@class="lines-515559956"]//a[contains(@class, "link-") and contains(@href, "http")]/@href').get()
            if seller_website:
                seller_name = urllib.parse.urlparse(seller_website).netloc
            else:
                seller_name = None
            description = response.xpath('//div[@class="descriptionContainer-2067035870"]/div/p/text()').getall()
            latitude = response.xpath('//meta[@property="og:latitude"]/@content').get()
            longitude = response.xpath('//meta[@property="og:longitude"]/@content').get()
            extraction_date = datetime.date.today().strftime('%Y-%m-%d')

            yield {
                'Title': title,
                'Rent': rent,
                'Address' : address.strip() if address else None,
                'Date Posted' : date_posted,
                'How Long Ago' : how_long,
                'Unit Type' : unit_type,
                'Bedrooms' : bedrooms,
                'Bathrooms' : bathrooms,
                'Utilities' : utilities,
                'Wifi and More' : wifi_and_more,
                'Parking' : parking,
                'Agreement' : agreement,
                'Pet Friendly' : pet_friendly,
                'Size' : size,
                'Furnished' : furnished,
                'Appliances' : appliances,
                'Air Conditioning' : air_conditioning,
                'Personal Space' : personal_space,
                'Smoking' : smoking,
                'Amenities' : amenities,
                'Seller' : seller,
                'Seller Name' : seller_name,
                'Description' : description,
                'Latitude' : latitude,
                'Longitude' : longitude,
                'extraction_date' : extraction_date
             }
    
        except Exception as e :
                logging.error(f'Error parsing response: {str(e)}')
                raise CustomException(e, sys)
        