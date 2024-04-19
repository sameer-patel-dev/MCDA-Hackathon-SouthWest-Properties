from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import html
from time import sleep
from selenium.webdriver.chrome.options import Options
import re
import pandas as pd
import ast
import mysql.connector
from mysql.connector import errorcode
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.notifications": 1
})


places = ['Halifax', 'Dartmouth']
rows_to_add = []


mainResult = []
for place in places:
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=chrome_options)
    driver.maximize_window()
    driver.get('https://killamreit.com/apartments?region=' + place)
    sleep(1)


    #Count total number of searches
    parent_div = driver.find_element(By.ID, 'killam-search-result-cards')
    all_child_divs = parent_div.find_elements(By.CLASS_NAME, 'killam-search-result-card')
    child_divs = [div for div in all_child_divs if not div.find_elements(By.XPATH, "ancestor::details")]
    number_of_divs = len(child_divs)


    sleep(1)

    result = []
    for item in range(1, number_of_divs):

        row = {}
        row['Place'] = place

        itemresult = []
        button = driver.find_element(By.XPATH, "//div[@id='killam-search-result-cards']//div[" + str(item) + "]//a[1]//div[1]//div[4]//div[5]//i[1]")
        driver.execute_script("arguments[0].scrollIntoView();", button)
        sleep(1)
        button.click()
        sleep(1)

        elements = driver.find_elements(By.CSS_SELECTOR, ".c-property-heading__title")
        filtered_texts = [element.text for element in elements if element.text.strip()][0]
        itemresult.append(filtered_texts)
        row['Listing_Name'] = filtered_texts

        elements = driver.find_elements(By.CSS_SELECTOR, ".c-property-heading__address")
        filtered_texts = [element.text for element in elements if element.text.strip()][0]
        itemresult.append(filtered_texts)
        row['Listing_Address'] = filtered_texts
        

        desc_titles = driver.find_elements(By.CSS_SELECTOR, "div.c-amenity-item__desc > div.c-amenity-item__desc_title")
        thList = []
        for title in desc_titles:
            itemresult.append(title.text)
            thList.append(title.text)

        row['Amenities'] = thList


        elements = driver.find_elements(By.CLASS_NAME, 'c-unit-row__field_content')
        field_contents = [element.text for element in elements]
        thList = []
        for content in field_contents:
            itemresult.append(content)
            thList.append(content)

        row['Others'] = thList

        rows_to_add.append(row)
        
        result.append(itemresult)
        # print(result[-1])
        driver.get('https://killamreit.com/apartments?region=' + place)
        sleep(1)


    mainResult.append(result)

driver.close()


df = pd.DataFrame(rows_to_add)
expanded_df = pd.DataFrame()

for index, row in df.iterrows():
    # Get the list to be expanded
    list_to_expand = row['Others']
    
    # Calculate how many chunks there will be for this row
    num_chunks = len(list_to_expand) // 5
    
    # Create a DataFrame from the chunks
    for chunk_start in range(0, len(list_to_expand), 5):
        chunk_end = chunk_start + 5
        chunk = list_to_expand[chunk_start:chunk_end]
        
        # Create a dictionary for the new row, preserving other data from the original row
        new_row = {col: row[col] for col in df.columns if col != 'Others'}
        new_row.update({
            'Price': chunk[0],
            'Bedrooms': chunk[1],
            'Bathrooms': chunk[2],
            'Size': chunk[3],
            'Availability': chunk[4]
        })
        
        # Append the new row to the expanded DataFrame
        expanded_df = expanded_df.append(new_row, ignore_index=True)


print(expanded_df)

unique_amenities = set()

for amenities_list in expanded_df['Amenities']:
    unique_amenities.update(amenities_list)

# Now create columns for each unique amenity with binary values
for amenity in unique_amenities:
    # Each column will have a 1 if the amenity is present in the list, 0 otherwise
    expanded_df[amenity] = expanded_df['Amenities'].apply(lambda amenities: 1 if amenity in amenities else 0)

# Drop the original 'Amenities' column as it's no longer needed
expanded_df.drop('Amenities', axis=1, inplace=True)
expanded_df.to_csv("killam_csv.csv", index = False)


df = pd.read_csv("killam_csv.csv")

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
file_name_in_s3 = 'ScrapingInput/Killam/killam_csv.csv'
upload_file_to_s3(bucket_name, file_name_in_s3, df)
print(f'File {file_name_in_s3} uploaded to {bucket_name}')


if True:
    config = {
        'user': '',
        'password': '',
        'host': '',
        'database': ''
    }


    table_name = 'killam'

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
        create_table(cursor, table_name, expanded_df.columns)

        # Insert data into table
        insert_data(cursor, table_name, expanded_df)

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
