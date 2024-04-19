import requests
import json
import pandas as pd
import mysql.connector
from mysql.connector import errorcode

url = "https://8hvk5i2wd9-dsn.algolia.net/1/indexes/rentseeker_prod_properties/query?x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser&x-algolia-application-id=8HVK5I2WD9&x-algolia-api-key=68a749c1cd4aff1ca2c87a160617bd61"

payload = json.dumps({
  "params": "query=&hitsPerPage=1000&page=0&numericFilters=%5B%5B%22type%3D2%22%5D%5D&insideBoundingBox=%5B%5B44.56969497195948%2C-63.667592520800774%2C44.727724389401565%2C-63.48288487919921%5D%5D"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

# print(response.text)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Convert the response content to JSON
    data = response.json()
    listings = data['hits']

    keys_to_remove = ["_highlightResult"]

    
    dfs = []

    for listing in listings:
        # Create a DataFrame for each listing
        listing = {key: value for key, value in listing.items() if key not in keys_to_remove}

        listing_df = pd.json_normalize(listing)
        fields_to_drop = ['id', 'prices_low.1+','type','image_url','company_id','company_name','company_image_url','company_phone','company_verified','featured','url','created_at_int','objectID','prices_low.2+','prices_low.3+','prices_high.1+','prices_high.2+','prices_high.3+']

        listing_df = listing_df.drop(columns=fields_to_drop, errors='ignore')
        

        dfs.append(listing_df)

    # Concatenate all DataFrames into a single DataFrame
    flattened_data = pd.concat(dfs, ignore_index=True)

    # Save the flattened data to a CSV file
    csv_filename = 'rent_seeker.csv'
    flattened_data.to_csv(csv_filename, index=False)

    print(f'Data written to {csv_filename}')
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)


    df = pd.read_csv("rent_seeker.csv")

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
    file_name_in_s3 = 'ScrapingInput/Rent_Seeker/rent_seeker.csv'
    upload_file_to_s3(bucket_name, file_name_in_s3, df)
    print(f'File {file_name_in_s3} uploaded to {bucket_name}')


if True:
    config = {
        'user': '',
        'password': '',
        'host': '',
        'database': ''
    }


    table_name = 'rent_seeker'

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
        create_table(cursor, table_name, flattened_data.columns)

        # Insert data into table
        insert_data(cursor, table_name, flattened_data)

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
