import csv
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from time import sleep
from bs4 import BeautifulSoup
import json
import mysql.connector
from mysql.connector import errorcode
import pandas as pd

def fetch_html_data(url):
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    # Specify the path to chromedriver directly
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)

    driver.maximize_window()
    driver.get(url)

    # Wait for some time to ensure the page is loaded completely
    # You might need to adjust the sleep duration based on the page load time
    sleep(5)

    # Print the entire HTML source code of the page
    html_content = driver.page_source

    # Close the webdriver
    driver.quit()

    return html_content

def extract_data_and_write_to_csv(json_data, csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['propertyType', 'lat', 'lon', 'listingType', 'street', 'city', 'state', 'zip',
                      'numBeds', 'lowPrice', 'highPrice', 'minBeds','maxBeds','title', 'highlightedAmenities']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for building in json_data['data']['buildings']:
            for listing in building['listings']:
                data = {
                    'propertyType': listing['propertyType'],
                    'lat': building['geo']['lat'],
                    'lon': building['geo']['lon'],
                    'listingType': listing['listingType'],
                    'street': listing['address']['street'],
                    'city': listing['address']['city'],
                    'state': listing['address']['state'],
                    'zip': listing['address']['zip'],
                    'numBeds': listing['models'][0]['numBeds'],
                    'lowPrice': listing['models'][0]['lowPrice'],
                    'highPrice': listing['models'][0]['highPrice'],
                    'minBeds':listing['modelSummary']['minBeds'],
                    'maxBeds':listing['modelSummary']['maxBeds'],
                    'title': listing['title'],
                    'highlightedAmenities': ', '.join([amenity['display'] for amenity in listing['amenities'].get('highlightedAmenities', [])])
                }
                writer.writerow(data)

if __name__ == '__main__':
    html_content = fetch_html_data("https://hotpads.com/node/hotpads-api/api/v2/listing/byCoordsV2?orderBy=score&bedrooms=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C8plus&bathrooms=0%2C0.5%2C1%2C1.5%2C2%2C2.5%2C3%2C3.5%2C4%2C4.5%2C5%2C5.5%2C6%2C6.5%2C7%2C7.5%2C8plus&pets=&laundry=&amenities=&propertyTypes=condo%2Cdivided%2Cgarden%2Chouse%2Cland%2Clarge%2Cmedium%2Ctownhouse&listingTypes=rental%2Croom%2Csublet%2Ccorporate&keywords=&includePhotosCollection=true&visible=favorite%2Cinquiry%2Cnew%2Cnote%2Cnotified%2Cviewed&lat=44.6653&lon=-63.5103&maxLat=44.7904&maxLon=-63.3302&minLat=44.5401&minLon=-63.6899&offset=0&limit=40&channels=&components=basic%2Cuseritem%2Cquality%2Cmodel%2Cphotos&trimResponse=true")
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the JSON data from the <pre> tag
    json_data = json.loads(soup.find('pre').text)

    csv_filename = 'hotpads_data.csv'
    extract_data_and_write_to_csv(json_data, csv_filename)
    print(f'Data written to {csv_filename}')

    df = pd.read_csv("hotpads_data.csv")

    import boto3
    from io import StringIO
    session = boto3.Session(
        aws_access_key_id='',
        aws_secret_access_key=''
    )

    s3 = session.client('s3')
    def upload_file_to_s3(bucket_name, file_name, data_frame):
        csv_buffer = StringIO()
        data_frame.to_csv(csv_buffer, index=False)
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())

    bucket_name = ''
    file_name_in_s3 = 'ScrapingInput/Hotspad/hotpads_data.csv'
    upload_file_to_s3(bucket_name, file_name_in_s3, df)
    print(f'File {file_name_in_s3} uploaded to {bucket_name}')

    if True:
        config = {
            'user': '',
            'password': '',
            'host': '',
            'database': ''
        }


        table_name = 'hotpads'

        # Function to create table if not exists
        def create_table(cursor, table_name, columns):
            # Adding an auto-incrementing ID column as the primary key
            sql_columns = ', '.join([f"`{col}` VARCHAR(255)" for col in columns])
            sql_create_table = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                {sql_columns}
            );"""
            cursor.execute(sql_create_table)

        # Function to insert data into table
        def insert_data(cursor, table_name, df):
            placeholders = ', '.join(['%s'] * len(df.columns))
            columns = ', '.join([f"`{col}`" for col in df.columns])
            sql_insert = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            for _, row in df.iterrows():
                cursor.execute(sql_insert, tuple(row.astype(str)))


        try:
            # Connect to MySQL database
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()

            # Create table if it does not exist
            create_table(cursor, table_name, df.columns)

            # Insert data into table
            insert_data(cursor, table_name, df)

            # Commit changes
            cnx.commit()

            print(f"Data inserted successfully into '{table_name}'.")

        except mysql.connector.Error as err:
            print(f"Failed to insert data into MySQL table: {err}")

        finally:
            # Close cursor and connection without checking if they're already closed
            if cursor is not None:
                cursor.close()
            if cnx.is_connected():
                cnx.close()
