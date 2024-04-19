import mysql.connector
from mysql.connector import errorcode
import os
import pandas as pd

config = {
    'user': '',
    'password': '',
    'host': '',
    'database': ''
}

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


def process_csv_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            table_name = filename[:-4]  # Remove the '.csv' extension to get the table name
            file_path = os.path.join(folder_path, filename)

            # Read CSV file into DataFrame
            df = pd.read_csv(file_path)

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
        else:
            continue


folder_path = 'CSV_FILES'
process_csv_files(folder_path)
