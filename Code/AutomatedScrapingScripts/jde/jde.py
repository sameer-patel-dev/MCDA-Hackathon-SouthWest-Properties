import requests
import json
import pandas as pd
import mysql.connector
from mysql.connector import errorcode


url = "https://www.jdepropertymgt.ca/_api/dynamic-pages-router/v1/pages?gridAppId=31a1e7c9-ddb5-4db6-8f29-24c6c4ae75e4&viewMode=site&instance=wixcode-pub.aae5c75dd7b4f5129d7ff8018522c649d8c64f18.eyJpbnN0YW5jZUlkIjoiZmI0MjI1ODgtNDJhMi00MjMxLTgzYmItMGNjMjgyOWY3MWUyIiwiaHRtbFNpdGVJZCI6Ijc0NzE3YTRhLTlhN2YtNGVjYi1hMmYwLTQxNzEzMTM2ZjhlNCIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTcwOTgwOTE4NTczNywiYWlkIjoiYjZlYjRmYzEtMzNjZS00NDU2LWFjOTUtZWRmZWI3ZGZlODRjIiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6IjJjYzQ1ZTBjLTgyNjItNGM5ZS04ZjczLTlhZmJlNzc5NDVjZiIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IlNob3dXaXhXaGlsZUxvYWRpbmcsQWRzRnJlZSxIYXNEb21haW4iLCJ0ZW5hbnQiOm51bGwsInNpdGVPd25lcklkIjoiY2VlMGE4NjUtMWM1Ni00MGQ0LWI0NWYtMzkwYWQ2YWZmZTBiIiwiaW5zdGFuY2VUeXBlIjoicHViIiwic2l0ZU1lbWJlcklkIjpudWxsLCJwZXJtaXNzaW9uU2NvcGUiOm51bGwsImxvZ2luQWNjb3VudElkIjpudWxsLCJpc0xvZ2luQWNjb3VudE93bmVyIjpudWxsfQ%3D%3D"

payload = json.dumps({
  "routerPrefix": "/properties",
  "config": {
    "patterns": {
      "/{title}": {
        "pageRole": "fa69d9f5-cb8b-4a6e-8073-8988d910d18b",
        "title": "{title}",
        "config": {
          "collection": "Properties",
          "pageSize": 1,
          "lowercase": True,
          "sort": [
            {
              "title": "asc"
            }
          ]
        },
        "seoMetaTags": {
          "og:image": "{image}",
          "robots": "index"
        }
      },
      "/": {
        "pageRole": "2872b14e-7920-469a-879d-2d3fe97ffede",
        "title": "JDE Property Management Properties",
        "config": {
          "collection": "Properties",
          "pageSize": 15,
          "lowercase": True,
          "sort": [
            {
              "status": "asc"
            },
            {
              "listingNo": "desc"
            },
            {
              "moveinDate": "asc"
            }
          ]
        },
        "seoMetaTags": {
          "robots": "index",
          "description": "",
          "keywords": "house for rent, rental properties, for rent, halifax rentals",
          "og:image": ""
        }
      }
    }
  },
  "pageRoles": {
    "fa69d9f5-cb8b-4a6e-8073-8988d910d18b": {
      "id": "t5lhj",
      "title": "Properties (Title)"
    },
    "2872b14e-7920-469a-879d-2d3fe97ffede": {
      "id": "uozgu",
      "title": "Properties (All)"
    }
  },
  "requestInfo": {
    "env": "browser",
    "formFactor": "desktop"
  },
  "routerSuffix": "/",
  "fullUrl": "https://www.jdepropertymgt.ca/properties/"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Convert the response content to JSON
    data = response.json()

    # Extract 'items' part of the data
    items = data['result']['data']['items']

  
    # Flatten the 'items' JSON structure
    flattened_data = pd.json_normalize(items)

    unwanted_columns = [
        'image', '_id', '_owner', 'link-properties-title', 'gallery',
        'link-properties-all', 'mapLocation.subdivisions',
        'mapLocation.countryFullName', 'mapLocation.streetAddress.number',
        'mapLocation.streetAddress.name', 'mapLocation.streetAddress.apt',
        'description.nodes', 'description.metadata','applicationUrl',
        'mapLocation.streetAddress.formattedAddressLine','description.metadata.version',
        'description.metadata.createdTimestamp','description.metadata.updatedTimestamp',
        'description.metadata.id','_createdDate.$date','_updatedDate.$date','bookingUrl',
        'description.metadata.createdTimestamp.$date','description.metadata.updatedTimestamp.$date',
        'listingNo'
    ]
    flattened_data = flattened_data.drop(columns=unwanted_columns, errors='ignore')

    # Show the flattened data structure
    flattened_data.head()

    # Save the flattened data to a CSV file
    csv_filename = 'jdepropertymgt.csv'
    flattened_data.to_csv(csv_filename, index=False)

    print(f'Data written to {csv_filename}')

    df = pd.read_csv("jdepropertymgt.csv")

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
    file_name_in_s3 = 'ScrapingInput/JDE/jdepropertymgt.csv'
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


    table_name = 'jde'

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

