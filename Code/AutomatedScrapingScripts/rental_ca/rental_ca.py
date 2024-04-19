from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from bs4 import BeautifulSoup
import json
import re
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def fetch_html_data(url):
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    # Specify the path to chromedriver directly
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=chrome_options)


    driver.maximize_window()
    driver.get(url)

    # Wait for some time to ensure the page is loaded completely
    # You might need to adjust the sleep duration based on the page load time
    sleep(1)

    # Print the entire HTML source code of the page
    html_content = driver.page_source

    # print(html_content)

    # Close the webdriver
    driver.quit()

    return html_content

if __name__ == '__main__':

    home_page_data = fetch_html_data('https://rentals.ca/halifax')
    soup = BeautifulSoup(home_page_data, 'html.parser')

    script_tags = soup.find_all('script', {'type': 'application/ld+json'})


    json_objects = []


    # Find the script tag with type 'application/ld+json'
    for script_tag in script_tags:
        # Extract the JSON data inside each script tag
        json_data = json.loads(script_tag.string)
        
        # Check if the JSON data has '@type' as 'ApartmentComplex'
        if '@type' in json_data and json_data['@type'] == 'ApartmentComplex':
            # Extract the 'url' field
            url = json_data.get('url', '')
            print("fetching data from..." + url)
            listing_html = fetch_html_data(url)
            pattern = re.compile(r'App\.store\.listing\s*=\s*({.*})')

            # Search for the pattern in the HTML text
            match = re.search(pattern, listing_html)

            if match:
                # Extract the matched JSON data
                listing_json = match.group(1)
                # print(listing_json)
                json_objects.append(json.loads(listing_json))
            else:
                print("App.store.listing not found in HTML text.")


    dfs = []

    for listing in json_objects:
        listing.pop("parent_place")
        listing.pop("photo")
        # Create a DataFrame for each listing
        listing_df = pd.json_normalize(listing)
        columns_to_remove = [
            "company", "address2", "phone", "view_on_map_url", "format", "featured_status",
            "priority", "verified", "photo_count", "bookables", "photos", "has_tour", "has_3D_tour",
            "source", "vendor_bundle", "description", "description_blurb", "tag_line", "short_term",
            "review_state", "summary", "promotions", "tours", "tours_3d_url", "city.id", "city.slug",
            "city.url", "city.region.id", "city.region.code", "city.boundaries", "photo.id", "photo.url",
            "photo.width", "photo.height", "photo.priority", "photo.unit_id", "photo.scales.large.url",
            "photo.scales.large.width", "photo.scales.large.height", "photo.scales.medium.url",
            "photo.scales.medium.width", "photo.scales.medium.height", "photo.scales.small.url",
            "photo.scales.small.width", "photo.scales.small.height", "photo.alt", "owner.id",
            "featured.enabled", "featured.start", "featured.stop", "property_addons.active",
            "property_addons.pending"
        ]

        # Drop the specified columns from the DataFrame
        listing_df = listing_df.drop(columns=columns_to_remove, errors='ignore')
        
        dfs.append(listing_df)

    # Concatenate all DataFrames into a single DataFrame
    flattened_data = pd.concat(dfs, ignore_index=True)

    # Save the flattened data to a CSV file
    csv_filename = 'rental_ca.csv'
    flattened_data.to_csv(csv_filename, index=False)

    print(f'Data written to {csv_filename}')



if True:
    config = {
        'user': '',
        'password': '',
        'host': '',
        'database': ''
    }


    table_name = 'rental_ca'

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
