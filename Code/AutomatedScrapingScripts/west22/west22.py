import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import mysql.connector
from mysql.connector import errorcode


def fetch_html_data(url):
    # Make a request to the URL
    response = requests.get(url)
    html_content = response.text
    return html_content


if __name__ == '__main__':
    
    url = "https://west22living.com/availability/"
    html_content = fetch_html_data(url)
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    unit_links = []

    final_json =[]

    # Extracting unit links from the table
    availability_table = soup.find('table', class_='responsive')
    if availability_table:
        # Loop through rows in the table body
        for row in availability_table.tbody.find_all('tr'):
            # Extracting unit link
            unit_link = row.find('td', class_='table-unit-type').a['href']
            unit_links.append(unit_link)

    # Print or use the extracted unit links
    for unit_link in unit_links:
        print("extracting info from..." + unit_link)
        unit_html = fetch_html_data(unit_link)
        soup = BeautifulSoup(unit_html, 'html.parser')
        # Initialize a dictionary to store the extracted information
        property_info = {}
        property_info['Listing_Address'] = '7037 Mumford Road'

        # Extracting details from the unit-details section
        unit_details = soup.find('div', class_='unit-details')
        if unit_details:
            # Extracting specific details
            h1_tag = unit_details.find('h1')
            property_info['Price'] = h1_tag.find('span', class_='price').text

            property_info['Available Date'] = unit_details.find('h5', class_='available-date').text.replace('Available: ', '')
            property_info['Available Date'] = datetime.strptime(property_info['Available Date'], "%b %d, %Y")
            property_info['Available Date'] = property_info['Available Date'].strftime("%d-%m-%y")
            print(property_info['Available Date'])

            unit_type_tag = unit_details.find('h3', id='unit-type')
            property_info['Unit Type'] = unit_type_tag.text.split('\xa0')[0]

            area_tag = unit_type_tag.find('a', class_='unit-area')
            property_info['Area'] = area_tag.text.split()[0]  # Extracting the numerical part of the area

        # Extracting details from the leasing info section
        leasing_info_section = soup.find('div', class_='row page-section apply-info')
        if leasing_info_section:
            leasing_info = leasing_info_section.find('div', class_='large-8 columns')

            property_info['Leasing Information'] = {
                'Lease Term': leasing_info.find('th', string='Lease').find_next('td').strong.text.strip(),
                'Utilities Description': leasing_info.find('th', string='Utilities').find_next('td').p.text.strip(),
                'Utilities Included': [item.text.strip() for item in leasing_info.find('th', string='Utilities').find_next('td').find('ul', class_='basic included-list').find_all('li')],
                'Parking Info': leasing_info.find('th', string='Parking').find_next('td').p.text.strip(),
                'Deposit Info': leasing_info.find('th', string='Deposit').find_next('td').p.text.strip(),
                'Policy': [item.p.text.strip() for item in leasing_info.find('th', string='Policy').find_next('td').find('ul', class_='basic included-list').find_all('li')]
            }

        # Convert the dictionary to JSON
        property_json = json.dumps(property_info, indent=2)

        # Print or save the JSON object as needed
        final_json.append(property_json)
    json_string = final_json
    json_objects = [json.loads(json_str) for json_str in json_string]

    dfs = []

    for listing in json_objects:
        listing_df = pd.json_normalize(listing)
        # print(listing_df.columns.tolist())

        amenities = listing_df.get('Leasing Information.Utilities Included', [])
        # print(amenities)
        for amenity in amenities:
            listing_df[amenity] = True


        features = listing_df.get('Leasing Information.Policy', [])
        # print(amenities)
        for feature in features:
            listing_df[feature] = True
        
        dfs.append(listing_df)

    # Concatenate all DataFrames into a single DataFrame
    flattened_data = pd.concat(dfs, ignore_index=True)

    # Save the flattened data to a CSV file
    flattened_data = flattened_data.drop(columns=['Leasing Information.Utilities Included', 'Leasing Information.Policy'])

    csv_filename = 'west22living.csv'
    flattened_data.to_csv(csv_filename, index=False)


    df = pd.read_csv("west22living.csv")

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
    file_name_in_s3 = 'ScrapingInput/West22/west22living.csv'
    upload_file_to_s3(bucket_name, file_name_in_s3, df)
    print(f'File {file_name_in_s3} uploaded to {bucket_name}')


    config = {
        'user': '',
        'password': '',
        'host': '',
        'database': ''
    }


    table_name = 'west22'

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
