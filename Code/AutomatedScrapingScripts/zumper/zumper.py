import requests
import json
import pandas as pd
import mysql.connector
from mysql.connector import errorcode

url = "https://www.zumper.com/api/svc/inventory/v1/listables/maplist/search"

headers = {
    "authority": "www.zumper.com",
    "accept": "*/*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "content-type": "application/json",
    "origin": "https://www.zumper.com",
    "referer": "https://www.zumper.com/apartments-for-rent/halifax-ns",
    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "x-csrftoken": "9Gm1gZPWhuSLsRXPbY8tBSXcILgvWIQ4Aw05yZYlQfbwZGCnBACkI3oAYwZkfU7y6QqV9xOgK38krdGQ",
    "x-zumper-xz-token": "axebrc4orkx.25aqt42wu",
}


data = {
    "url": "halifax-ns",
    "limit": 50,
    "propertyTypes": {"exclude": [16, 17]},
    "external": True,
    "offset": 18,
    "descriptionLength": 580
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    json_data = response.json()
    print(json.dumps(json_data, indent=4))
    df = pd.json_normalize(json_data, record_path=['listables'])
    df = df.drop(columns=['listing_id','created_on','modified_on','listed_on','listing_status' ,'group_id','leasing_fee','building_id','feed_name','image_ids', 'neighborhood_id','neighborhood_name', 'brokerage_id', 'agent_id', 'tz', 'promotion',  'zappable' ,   'property_type' ,'amenities' ,  'building_amenities' , 'phone' ,  'listing_type', 'pb_id' , 'pb_url',  'url', 'previous_price' ,   'lease_type', 'features',  'is_pad' ,     'pl_id',   'pl_url',  'pa_url' , 'is_messageable' , 'provider_url' ,   'title' ,  'short_description',   'rating',  'pa_should_index' ,'integrated_tour_types'])
    df.to_csv('zumper_csv.csv', index=False)
    
else:
    print(f"Error {response.status_code}: {response.text}")


if True:
    config = {
        'user': '',
        'password': '',
        'host': '',
        'database': ''
    }


    table_name = 'zumper'

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

