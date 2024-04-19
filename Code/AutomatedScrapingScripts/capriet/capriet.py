import requests
import csv
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector
from mysql.connector import errorcode

url_properties = "https://www.capreit.ca/wp-admin/admin-ajax.php?action=property_json&language=en"

# Mapping of utility IDs to utility names
utility_mapping = {
    33: "water",
    34: "heat",
    39: "Laundry",
    43: "Storage",
    32: "Parking(60)",
    35: "Electricity"
}

def fetch_property_details(property_url):
    payload = {}
    files = {}
    headers = {}

    response = requests.request("POST", property_url, headers=headers, data=payload, files=files)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        property_list_items = soup.find_all('li', class_='property-options-list-item')

        details = []

        for property_item in property_list_items:
            availability = property_item.find('div', class_='property-options-list-item-availability').get_text(strip=True)
            bedroom_info = property_item.find('li', class_='property-options-item').get_text(strip=True)

            price_div = property_item.find('div', class_='property-options-list-item-price')
            
            if price_div and price_div.b:
                rent = price_div.b.get_text(strip=True)
                details.append({"availability": availability, "bedroom_info": bedroom_info, "rent": rent})

        return details

    return None

response = requests.get(url_properties)

if response.status_code == 200:
    data = response.json()
    ns_properties = [item for item in data if item.get("province") == "NS" and item.get("has_vacancies")]

    csv_file = 'capreit.csv'

    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        header_row = [
            "id", "title", "address", "city", "province", "postal_code", "earliest_date",
            "has_vacancies", "vacancy_message", "availability", "rent", "bedroom",
            "utilities_message", "building_type_name", 
            "url", "included_in_rent_ids",  *utility_mapping.values()
        ]
        csv_writer.writerow(header_row)

        for item in ns_properties:
            building_type_name = item["building_type"]["name"] if isinstance(item["building_type"], dict) else None

            included_utilities = set(item["included_in_rent_ids"])
            utilities_included = [int(utility_id in included_utilities) for utility_id in utility_mapping]

            property_url = item["url"]
            property_details = fetch_property_details(property_url)

            if property_details:
                for detail in property_details:
                    row = [
                        item["id"], item["title"], item["address"],
                        item["city"], item["province"], item["postal_code"],
                        item["earliest_date"], item["has_vacancies"], item["vacancy_message"],
                        detail["availability"], detail["rent"], detail["bedroom_info"],
                        item["utilities_message"], building_type_name,
                        item["url"], ", ".join(map(str, item["included_in_rent_ids"])),
                        *utilities_included
                    ]
                    csv_writer.writerow(row)
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)

print(f"Data saved to {csv_file}")



df = pd.read_csv("capreit.csv")
df = df.drop(columns=['id', 'utilities_message', 'url', 'included_in_rent_ids'])


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
file_name_in_s3 = 'ScrapingInput/Capriet/capreit.csv'
upload_file_to_s3(bucket_name, file_name_in_s3, df)
print(f'File {file_name_in_s3} uploaded to {bucket_name}')




if True:
    config = {
        'user': '',
        'password': '',
        'host': '',
        'database': ''
    }


    table_name = 'capriet'

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




