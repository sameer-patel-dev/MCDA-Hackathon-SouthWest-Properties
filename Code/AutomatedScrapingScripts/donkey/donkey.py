import requests
import json
import csv
import mysql.connector
from mysql.connector import errorcode
import pandas as pd

url = "https://www.rentdonkey.ca/search.php"

payload = {
    'funct': 'search',
    'hash': 'area=Halifax&studio&1BR&2BR&3BR&4BR&available=all&&NE_lat=44.7273144919652&NE_long=-63.572065830215884&SW_lat=44.54677788098915&SW_long=-63.62081766127057'
}

files = []
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Convert the response content to JSON
    data = response.json()

    # Specify the CSV file name
    csv_file = 'rentdonkey.csv'

    # Open the CSV file in write mode
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        # Create a CSV writer
        csv_writer = csv.writer(csvfile)

        # Write the header row
        header_row = [
            "listing_id", "st address", "lat", "long",  "bedroom", "rent", "Building type", "parking", "pets allowed", "balcony", "smoking", "laundry", "heat", "water", "electricity"
        ]
        csv_writer.writerow(header_row)

        # Write the data rows
        for item in data.values():
            if isinstance(item, dict):
                row = [
                    item.get("listing_id", ""),
                    item.get("st", ""),
                    item.get("la", ""),
                    item.get("lo", ""),
                    item.get("br", ""),
                    item.get("pr", ""),
                    "apartment" if item.get("dw", "") == 1 else "house",
                    item.get("pa", ""),
                    item.get("pe", ""),
                    item.get("bl", ""),
                    item.get("sm", ""),
                    item.get("ln", ""),
                    item.get("he", ""),
                    item.get("wa", ""),
                    item.get("el", "")
                ]
                csv_writer.writerow(row)

    print(f"Data saved to {csv_file}")
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)



df = pd.read_csv("rentdonkey.csv")

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
file_name_in_s3 = 'ScrapingInput/Rentdonkey/rentdonkey.csv'
upload_file_to_s3(bucket_name, file_name_in_s3, df)
print(f'File {file_name_in_s3} uploaded to {bucket_name}')

if True:
    config = {
        'user': '',
        'password': '',
        'host': '',
        'database': ''
    }


    table_name = 'rentdonkey'

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
