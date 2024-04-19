import requests
import json
import pandas as pd
import mysql.connector
from mysql.connector import errorcode


url = "https://api.theliftsystem.com/v2/search?locale=en&auth_token=sswpREkUtyeYjeoahA2i&geocode=&min_bed=-1&max_bed=100&min_bath=0&max_bath=10&min_rate=0&min_sqft=0&max_sqft=10000&show_custom_fields=true&show_promotions=true&region=&keyword=false&ownership_types=&exclude_ownership_types=&custom_field_key=&custom_field_values=&order=min_rate+ASC&limit=66&neighbourhood=&amenities=&promotions=&pet_friendly=&offset=0&count=false&client_id=584&city_id=1170&max_rate=5000&property_types=apartments%2C+houses%2C+commercial&city_ids="

payload = {'latitude': '44.64622549214262',
'longitude': '-63.632897449999994',
'radius': '7.226933805643282',
'page': '0',
'width': '1000'}
files=[

]
headers = {}

response = requests.request("GET", url, headers=headers, data=payload, files=files)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Convert the response content to JSON
    data = response.json()
    keys_to_remove = ["photo", "photo_path", "thumbnail_path", "details", "promotion", "contact", "website", "custom_fields"]

    dfs =[]

    for listing in data:
        listing = {key: value for key, value in listing.items() if key not in keys_to_remove}
        listing_df = pd.json_normalize(listing)

        dfs.append(listing_df)

    flattened_data = pd.concat(dfs, ignore_index=True)
    flattened_data = flattened_data.drop(columns=['promotions', 'id', 'permalink', 'building_header', 'office_hours', 'matched_suite_names', 'min_availability_date', 'availability_count', 'client.id', 'client.website', 'client.email', 'client.phone', 'address.intersection', 'address.city_id', 'address.province_code', 'address.country_code', 'geocode.distance' ])
    flattened_data.rename(columns={'name': "Building_Name", "matched_beds": 'Bedroom_Count', "matched_baths": 'Bathroom_Count'}, inplace = True)
    csv_filename = 'templeton.csv'
    flattened_data.to_csv(csv_filename, index=False)
    print(f'Data written to {csv_filename}')

    df = pd.read_csv("templeton.csv")

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

    bucket_name = 'mcda-hackathon-s3-bucket'
    file_name_in_s3 = 'ScrapingInput/Templeton/templeton.csv'
    upload_file_to_s3(bucket_name, file_name_in_s3, df)
    print(f'File {file_name_in_s3} uploaded to {bucket_name}')

else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)


if True:
    config = {
        'user': '',
        'password': '',
        'host': '',
        'database': ''
    }


    table_name = 'templeton'

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
