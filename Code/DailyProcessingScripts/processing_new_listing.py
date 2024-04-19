import pandas as pd
import boto3
from shapely.geometry import Point
import shapely.wkt
from geopy.distance import geodesic
import requests
from io import StringIO,BytesIO
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from datetime import datetime, date



# Define a function that will be applied to each row
def add_columns(row):
    lat, lon = assignCoordinates(row['listingAddress'])
    minorRegion = fetchMinorRegion(lat, lon)
    row['listingMajorRegion'] = fetchMajorRegion(lat, lon)
    row['listingMinorRegion'] = minorRegion
    row['listingLatitude'] = lat
    row['listingLongitude'] = lon
    row['transitScore'] = fetchTransitScore(lat, lon)
    row['walkScore'] = fetchWalkScore(lat, lon)
    row['bikeScore'] = fetchBikeScore(lat, lon)
    row['crimeScore'] = fetchCrimeScore(minorRegion)
    row['retailGroceryScore'] = fetchRetailGroceryScore(lat, lon)
    row['retailRecreationScore'] = fetchRetailRecreationScore(lat, lon)
    row['educationCenterScore'] = fetchEducationCenterScore(lat, lon)
    row['emergencyCenterScore'] = fetchEmergencyCenterScore(lat, lon)
    return row

def assignCoordinates(street_address):
    street_address = street_address.replace(' ', '+')
    province = ",+Nova+Scotia,+"
    country = "CA"
    formatted_address = street_address+province+country
    API_Key=""
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+formatted_address+'&key='+API_Key)
    response_data= response.json()
    latitude = response_data['results'][0]['geometry']['location']['lat']
    longitude = response_data['results'][0]['geometry']['location']['lng']
    return latitude,longitude

def fetchMajorRegion(latitude, longitude):
    # Load the CSV file
    file_path = 'MajorRegion.csv'
    df = pd.read_csv(file_path)

    # Convert the WKT column to Shapely geometries
    df['geometry'] = df['WKT'].apply(shapely.wkt.loads)
    point = Point(longitude, latitude)
    
    for index, row in df.iterrows():
        if row['geometry'].contains(point):
            return row['name']
    
    return 'Not in any region'

def fetchMinorRegion(latitude, longitude):
    # Load the CSV file
    file_path = 'MinorRegion.csv'
    df = pd.read_csv(file_path)

    # Convert the WKT column to Shapely geometries
    df['geometry'] = df['WKT'].apply(shapely.wkt.loads)
    point = Point(longitude, latitude)
    
    for index, row in df.iterrows():
        if row['geometry'].contains(point):
            return row['name']
    
    return 'Not in any region'

def fetchCrimeScore(minor_region):
    file_path = 'MinorRegion.csv'
    df = pd.read_csv(file_path)
    for index, row in df.iterrows():
        if (row['name'] == minor_region):
            return df.at[index,'crimeScoreLabel']

    return 'Safe'

def find_place_nearby(latitude, longitude, keyword, radius=5000):
    api_key = ""
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
    "location": f"{latitude},{longitude}",
    "radius": radius,
    "keyword": keyword,
    "key": api_key
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if 'results' in data:
        result = data['results']
        for place in result:
            name = place['name']
            location = place['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            return lat, lng
    return None, None

def calculateDistance(listingLatitude, listingLongitude, place_lat, place_lon):

    if pd.isna(place_lat):
      return None

    Latitude = float(place_lat)
    Longitude = float(place_lon)

    distance = geodesic((listingLatitude, listingLongitude), (Latitude, Longitude)).kilometers
    return distance

def calculateDistanceScore(distance):
    if distance is None:
        return 0
    if distance < 1:
        return 99
    elif 1 <= distance < 3:
        return 75
    elif 3 <= distance < 5:
        return 50
    elif 5 <= distance < 7:
        return 25
    elif distance >= 7:
        return 0
    else:
        return 0


def fetchTransitScore(lat,lon):
    api_key = ""
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
    "location": f"{lat},{lon}",
    "radius": 200,
    "keyword": 'Transit',
    "key": api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()
    results = []

    if "results" in data:
      bus_stops = [(place["name"], place.get("vicinity")) for place in data["results"]]

      results = []
      for name, location in bus_stops:
        results.append([name, location])


    
    transitScore = len(results)
    max_count_expected = 20
    transitScore = (transitScore / max_count_expected) * 100
    if transitScore > 99:
        transitScore = 99

    return transitScore

def fetchRetailGroceryScore(lat,lon):
    nearby_df = pd.read_csv("nearbyPlaces.csv")
    filtered_df = nearby_df[nearby_df['type'] == 'Grocery']
    lat_lon_df = pd.DataFrame(columns=['location', 'lat', 'lon'])
    for _, row in filtered_df.iterrows():
        place_lat , place_lon = find_place_nearby(lat,lon,row['location'])
        new_row = [row['location'], place_lat, place_lon]
        lat_lon_df.loc[len(lat_lon_df)] = new_row

    lat_lon_df['Distance'] = lat_lon_df.apply(lambda row: calculateDistance(lat, lon, row['lat'],row['lon']), axis=1)
    lat_lon_df['DistanceScore'] = lat_lon_df.apply(lambda row: calculateDistanceScore(row['Distance']),axis=1)

    mode_value = lat_lon_df['DistanceScore'].mode()[0]
    return mode_value

def fetchRetailRecreationScore(lat,lon):
    nearby_df = pd.read_csv("nearbyPlaces.csv")
    filtered_df = nearby_df[nearby_df['type'] == 'Recreation']
    lat_lon_df = pd.DataFrame(columns=['location', 'lat', 'lon'])
    for _, row in filtered_df.iterrows():
        place_lat , place_lon = find_place_nearby(lat,lon,row['location'])
        new_row = [row['location'], place_lat, place_lon]
        lat_lon_df.loc[len(lat_lon_df)] = new_row

    lat_lon_df['Distance'] = lat_lon_df.apply(lambda row: calculateDistance(lat, lon, row['lat'],row['lon']), axis=1)
    lat_lon_df['DistanceScore'] = lat_lon_df.apply(lambda row: calculateDistanceScore(row['Distance']),axis=1)

    mode_value = lat_lon_df['DistanceScore'].mode()[0]
    return mode_value

def fetchEducationCenterScore(lat,lon):
    nearby_df = pd.read_csv("nearbyPlaces.csv")
    filtered_df = nearby_df[nearby_df['type'] == 'EducationCenter']
    lat_lon_df = pd.DataFrame(columns=['location', 'lat', 'lon'])
    for _, row in filtered_df.iterrows():
        place_lat , place_lon = find_place_nearby(lat,lon,row['location'])
        new_row = [row['location'], place_lat, place_lon]
        lat_lon_df.loc[len(lat_lon_df)] = new_row

    lat_lon_df['Distance'] = lat_lon_df.apply(lambda row: calculateDistance(lat, lon, row['lat'],row['lon']), axis=1)
    lat_lon_df['DistanceScore'] = lat_lon_df.apply(lambda row: calculateDistanceScore(row['Distance']),axis=1)

    mode_value = lat_lon_df['DistanceScore'].mode()[0]
    return mode_value

def fetchEmergencyCenterScore(lat,lon):
    nearby_df = pd.read_csv("nearbyPlaces.csv")
    filtered_df = nearby_df[nearby_df['type'] == 'Emergency']
    lat_lon_df = pd.DataFrame(columns=['location', 'lat', 'lon'])
    for _, row in filtered_df.iterrows():
        place_lat , place_lon = find_place_nearby(lat,lon,row['location'])
        new_row = [row['location'], place_lat, place_lon]
        lat_lon_df.loc[len(lat_lon_df)] = new_row

    lat_lon_df['Distance'] = lat_lon_df.apply(lambda row: calculateDistance(lat, lon, row['lat'],row['lon']), axis=1)
    lat_lon_df['DistanceScore'] = lat_lon_df.apply(lambda row: calculateDistanceScore(row['Distance']),axis=1)

    mode_value = lat_lon_df['DistanceScore'].mode()[0]
    return mode_value

def calculateWalkingTime(listingLatitude, listingLongitude, place_lat, place_lon):
    api_key = ""
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    # Parameters should be passed as a dictionary to the `params` argument
    params = {
        "origins": f"{listingLatitude},{listingLongitude}",
        "destinations": f"{place_lat},{place_lon}",
        "mode": "walking",
        "key": api_key
    }

    response = requests.get(url, params=params)

    # It's always a good idea to check the response status code to ensure the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        response_json = response.json()
        print(response_json)  # Add this line before time_seconds = data["rows"][0]["elements"][0]["duration"]["value"]
        if response_json['rows'] and response_json['rows'][0]['elements']:
            elements = response_json['rows'][0]['elements'][0]
            # Ensure the 'duration' key is present in the element
            if 'duration' in elements:
                time_seconds = elements['duration']['value']
                time_minutes = time_seconds / 60.0
                return time_minutes
            
    return None
def calculateBikeTime(listingLatitude, listingLongitude, place_lat, place_lon):
    api_key = ""
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    # Parameters should be passed as a dictionary to the `params` argument
    params = {
        "origins": f"{listingLatitude},{listingLongitude}",
        "destinations": f"{place_lat},{place_lon}",
        "mode": "bicycling",
        "key": api_key
    }

    response = requests.get(url, params=params)

    # It's always a good idea to check the response status code to ensure the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        response_json = response.json()
        print(response_json)  # Add this line before time_seconds = data["rows"][0]["elements"][0]["duration"]["value"]
        if response_json['rows'] and response_json['rows'][0]['elements']:
            elements = response_json['rows'][0]['elements'][0]
            # Ensure the 'duration' key is present in the element
            if 'duration' in elements:
                time_seconds = elements['duration']['value']
                time_minutes = time_seconds / 60.0
                return time_minutes
    return None

def fetchWalkScore(lat,lon):
    nearby_df = pd.read_csv("nearbyPlaces.csv")
    types_to_filter = ['Grocery', 'Recreation']
    filtered_df = nearby_df[nearby_df['type'].isin(types_to_filter)]
    lat_lon_df = pd.DataFrame(columns=['location', 'lat', 'lon'])
    for _, row in filtered_df.iterrows():
        place_lat , place_lon = find_place_nearby(lat,lon,row['location'])
        new_row = [row['location'], place_lat, place_lon]
        lat_lon_df.loc[len(lat_lon_df)] = new_row
    
    lat_lon_df['Time'] = lat_lon_df.apply(lambda row: calculateWalkingTime(lat, lon, row['lat'],row['lon']), axis=1)

    if not lat_lon_df.empty and 'Time' in lat_lon_df:
        # Calculate the 25th and 75th percentiles
        p25_time = lat_lon_df['Time'].quantile(0.25)
        p75_time = lat_lon_df['Time'].quantile(0.75)

        # Define maximum time considered ideal for walking (in minutes)
        ideal_time = 30

        # Calculate scores based on how the percentiles compare to the ideal walking time
        score_p25 = max(0, 100 - (p25_time / ideal_time) * 100)
        score_p75 = max(0, 100 - (p75_time / ideal_time) * 100)

        # Combine the scores, with more weight on the 25th percentile
        walk_score = (score_p25 * 0.75 + score_p75 * 0.25) / 2

        return walk_score
    return 0  # Default score if data is empty

def fetchBikeScore(lat,lon):
    nearby_df = pd.read_csv("nearbyPlaces.csv")
    types_to_filter = ['Grocery', 'Recreation']
    filtered_df = nearby_df[nearby_df['type'].isin(types_to_filter)]
    lat_lon_df = pd.DataFrame(columns=['location', 'lat', 'lon'])
    for _, row in filtered_df.iterrows():
        place_lat , place_lon = find_place_nearby(lat,lon,row['location'])
        new_row = [row['location'], place_lat, place_lon]
        lat_lon_df.loc[len(lat_lon_df)] = new_row
    
    lat_lon_df['Time'] = lat_lon_df.apply(lambda row: calculateBikeTime(lat, lon, row['lat'],row['lon']), axis=1)
    
    if not lat_lon_df.empty and 'Time' in lat_lon_df:
        # Calculate the 25th and 75th percentiles
        p25_time = lat_lon_df['Time'].quantile(0.25)
        p75_time = lat_lon_df['Time'].quantile(0.75)

        # Define maximum time considered ideal for walking (in minutes)
        ideal_time = 30

        # Calculate scores based on how the percentiles compare to the ideal walking time
        score_p25 = max(0, 100 - (p25_time / ideal_time) * 100)
        score_p75 = max(0, 100 - (p75_time / ideal_time) * 100)

        # Combine the scores, with more weight on the 25th percentile
        bike_score = (score_p25 * 0.75 + score_p75 * 0.25) / 2

        return bike_score
    return 0  # Default score if data is empty


# Load the CSV file
# Read from s3 instead of local

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('S3_ACCESS_ID'),
    aws_secret_access_key=os.getenv('S3_ACCESS_KEY'),
    region_name='ca-central-1',
    config=boto3.session.Config(signature_version='s3v4')

)

print(os.getenv('S3_ACCESS_ID'))
print(os.getenv('S3_ACCESS_KEY'))


bucket_name = ''
# file_key = 'newListingCSVInput/dummy_listing_data.csv'

folder = 'newListingCSVInput/'
today = date.today()
today_str = today.strftime("%Y-%m-%d")

prefix = folder+today_str+"/"

# List objects within the specified bucket and prefix
response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

print(response)

# Filter for CSV files
csv_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.csv')]
print(csv_files)

# Define a list to hold your DataFrames
dfs = []

# Loop through the list of CSV files
for file_key in csv_files:
    # Get the object from S3
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    
    # Read the object's content into a DataFrame
    temp = pd.read_csv(BytesIO(obj['Body'].read()))
    
    # Append the DataFrame to your list
    dfs.append(temp)


df = pd.concat(dfs, ignore_index=True)

# df = df.head()



# Apply the function to each row
df = df.apply(add_columns, axis=1)

# Display the first few rows of the updated dataframe to verify the additions
print(df.head())

#code for pushing to SQL


engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'))


df.to_sql('mainWebAppTableTest', con=engine, index=False, if_exists='append')

