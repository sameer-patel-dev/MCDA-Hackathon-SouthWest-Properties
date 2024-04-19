import requests
import json
import pandas as pd
import mysql.connector
from mysql.connector import errorcode

url = "https://www.rentfaster.ca/api/map.json"

payload = {'l': '12,44.6489,-63.5753',
'city_id': 'ns/halifax'}
files=[

]
headers = {
  'Cookie': 'PHPSESSID=5aa04fbf8ada62580dabad7676535dc8; RFUUID=e473cfda-e475-4929-bed6-10b10d41b023; lastcity=ns%2Fhalifax'
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

# print(response.text)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Convert the response content to JSON
    data = response.json()

    listings = data['listings']

    dfs = []

    for listing in listings:
        # Create a DataFrame for each listing
        listing_df = pd.json_normalize(listing)
        fields_to_drop = ['userId', 'phone', 'phone_2', 'email', 'community', 'marker', 'thumb2', 'preferred_contact', 'ref_id', 'id', 'a', 'f', 's', 'address', 'link', 'utilities_included', 'price2', 'bed2', 'sq_feet2', 'bath2']


        amenities = listing.get('utilities_included', [])
        for amenity in amenities:
            listing_df[amenity] = True

        listing_df = listing_df.drop(columns=fields_to_drop, errors='ignore')
        
        dfs.append(listing_df)

    # Concatenate all DataFrames into a single DataFrame
    flattened_data = pd.concat(dfs, ignore_index=True)

    flattened_data.rename(columns={'v': "Vacancy", "title": 'Building_Name', "intro": 'Building_Location', '': "test"}, inplace = True)
    flattened_data = flattened_data.drop(columns=['test'])

    # Save the flattened data to a CSV file
    csv_filename = 'rent_fast.csv'
    flattened_data.to_csv(csv_filename, index=False)

    print(f'Data written to {csv_filename}')


    df = pd.read_csv("rent_fast.csv")

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
    file_name_in_s3 = 'ScrapingInput/Rent_Fast/rent_fast.csv'
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


    table_name = 'rent_fast'

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
