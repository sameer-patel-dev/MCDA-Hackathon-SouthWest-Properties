
from itemadapter import ItemAdapter
from src.logger import logging
from src.exception import CustomException
import sys
import sqlite3

class HousingWebscrapingPipeline:

    def process_item(self, item, spider):
        return item
    
class SQLitePipeline :

    def open_spider(self, spider) :
        self.connection = sqlite3.connect('kijiji.db')
        self.c = self.connection.cursor()
        try:
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS kijiji (
                    Title TEXT,
                    Rent TEXT,
                    Address TEXT,
                    Date_Posted TEXT,
                    How_Long_Ago TEXT,
                    Unit_Type TEXT,
                    Bedrooms TEXT,
                    Bathrooms TEXT,
                    Utilities TEXT,
                    Wifi_and_More TEXT,
                    Parking TEXT,
                    Agreement TEXT,
                    Pet_Friendly TEXT,
                    Size TEXT,
                    Furnished TEXT,
                    Appliances TEXT,
                    Air_Conditioning TEXT,
                    Personal_Space TEXT,
                    Smoking TEXT,
                    Amenities TEXT,
                    Seller TEXT,
                    Seller_Name TEXT
                )
            ''')
            self.connection.commit()
            logging.info('SQLite DB Connection Created and Table Created')
        except Exception as e:
            raise CustomException(e, sys)


    def close_spider(self,spider) :
        self.connection.close()
        logging.info('SQLite DB Connection Closed')


    def process_item(self, item, spider):
        utilities = ', '.join(item.get('Utilities', []))
        appliances = ', '.join(item.get('Appliances', []))
        personal_space = ', '.join(item.get('Personal Space', []))
        amenities = ', '.join(item.get('Amenities', []))

        self.c.execute('''
            INSERT INTO kijiji (Title, Rent, Address, Date_Posted, How_Long_Ago,
            Unit_Type, Bedrooms, Bathrooms, Utilities, Wifi_and_More, Parking,
            Agreement, Pet_Friendly, Size, Furnished, Appliances, Air_Conditioning,
            Personal_Space, Smoking, Amenities, Seller, Seller_Name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get('Title'),
            item.get('Rent'),
            item.get('Address'),
            item.get('Date Posted'),
            item.get('How Long Ago'),
            item.get('Unit Type'),
            item.get('Bedrooms'),
            item.get('Bathrooms'),
            utilities,
            item.get('Wifi and More'),
            item.get('Parking'),
            item.get('Agreement'),
            item.get('Pet Friendly'),
            item.get('Size'),
            item.get('Furnished'),
            appliances,
            item.get('Air Conditioning'),
            personal_space,
            item.get('Smoking'),
            amenities,
            item.get('Seller'),
            item.get('Seller Name')
        ))
        self.connection.commit()
        logging.info('Data added to DB')
        return item  
    