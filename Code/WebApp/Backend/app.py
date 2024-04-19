from flask import Flask, jsonify, request, Response
from datetime import datetime, date
from sqlalchemy import create_engine,desc,cast,Numeric
from flask_cors import CORS, cross_origin
import boto3
import botocore
import requests
import pandas as pd
from geopy.distance import geodesic
from shapely.geometry import Point
import shapely.wkt
import json
import pickle
from sqlalchemy import create_engine, Column, Integer, String
from flask_sqlalchemy import SQLAlchemy
from io import StringIO
import threading


app = Flask(__name__)
CORS(app)



db = SQLAlchemy()

SQLALCHEMY_DATABASE_URI = ''
SQLALCHEMY_TRACK_MODIFICATIONS = False
S3_ACCESS_ID=''
S3_ACCESS_KEY=''
S3_BUCKET_NAME=''

# Expected columns (excluding 'listingAddress' and 'listingRent')
expected_columns = ['listingMajorRegion', 'listingMinorRegion', 'listingType',
                    'listingPropertyType', 'crimeScore', 'listingSizeSquareFeet',
                    'bedroomCount', 'listingLatitude', 'listingLongitude', 'bathroomCount',
                    'heatUtility', 'waterUtility', 'hydroUtility', 'furnishedUtility',
                    'petPolicy', 'smokingPolicy', 'gymAmenity', 'parkingAmenity', 'acAmenity',
                    'applianceAmenity', 'storageAmenity', 'transitScore', 'walkScore',
                    'bikeScore', 'retailGroceryScore', 'retailRecreationScore',
                    'educationCenterScore', 'emergencyCenterScore']




#database connection
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
db.init_app(app)

s3 = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_ID,
    aws_secret_access_key=S3_ACCESS_KEY,
    region_name='ca-central-1',
    config=boto3.session.Config(signature_version='s3v4')

)

bucket_name = S3_BUCKET_NAME





class ListingV1(db.Model):
    __tablename__ = 'mainWebAppTable'
    id = Column(Integer, primary_key=True, autoincrement=True)
    listingAddress = Column(String(255))
    listingMajorRegion = Column(String(255))
    listingMinorRegion = Column(String(255))
    listingLatitude = Column(String(255))
    listingLongitude = Column(String(255))
    listingType = Column(String(255))
    listingPropertyType = Column(String(255))
    listingSizeSquareFeet = Column(String(255))
    bedroomCount = Column(String(255))
    bathroomCount = Column(String(255))
    heatUtility = Column(String(255))
    waterUtility = Column(String(255))
    hydroUtility = Column(String(255))
    furnishedUtility = Column(String(255))
    petPolicy = Column(String(255))
    smokingPolicy = Column(String(255))
    gymAmenity = Column(String(255))
    parkingAmenity = Column(String(255))
    acAmenity = Column(String(255))
    applianceAmenity = Column(String(255))
    storageAmenity = Column(String(255))
    transitScore = Column(String(255))
    walkScore = Column(String(255))
    bikeScore = Column(String(255))
    crimeScore = Column(String(255))
    retailGroceryScore = Column(String(255))
    retailRecreationScore = Column(String(255))
    educationCenterScore = Column(String(255))
    emergencyCenterScore = Column(String(255))
    listingRent = Column(String(255))
    imageLink = Column(String(255))


def read_csv_from_s3(bucket_name, file_key):
    csv_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    body = csv_obj['Body']
    csv_string = body.read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_string))
    return df


def read_pkl_from_s3(bucket_name, file_key):
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    body = response['Body']
    pkl_string = body.read()
    try:
        data = pickle.loads(pkl_string)
    except Exception as e:
        print(f"Error during unpickling object (Possibly corrupted file): {e}")
        return None
    return data


#model stuff
# Load your preprocessor and model
preprocessor = read_pkl_from_s3('mcda-hackathon-s3-bucket', 'WebApp/preprocessor.pkl')

model = read_pkl_from_s3('mcda-hackathon-s3-bucket', 'WebApp/best_xgb_model.pkl')



@app.route('/')


# Route to get all the listings
@app.route('/api/listings', methods=['GET'])
@cross_origin()
def list_projects():
    all_listings = ListingV1.query.all()
    listings = appendFunc(all_listings)
    response = jsonify(listings) 
    return response


@app.route('/api/csv_upload', methods=['POST'])
@cross_origin()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 404
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 403
    
    # Save file to S3
    try:
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H:%M:%S")
        file_name = now_str + ".csv"
        s3.upload_fileobj(file, bucket_name, "modelCSVInput/" +today_str + '/' + file_name )
        return jsonify({'message': 'File uploaded successfully'})

    except botocore.exceptions.ClientError as e:
        print(e)
        return jsonify({'error': 'Error uploading file to S3'})

    
# Route to predict rent forecast
@app.route('/api/forecast/results', methods=['GET'])
@cross_origin()
def list_files():
    try:
        # print(folder_name)
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix="modelOutput/")
        files = []

        # Check if there are any files in the bucket
        if 'Contents' in response:
            for file_obj in response['Contents']:
                files.append(file_obj['Key'])
        
        return jsonify({'files': files})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Error listing files'})
    

@app.route('/api/rent-forecast', methods=['POST'])
@cross_origin()
def rent_forecast():
    # Check for batch predictions (CSV file)
    if 'file' in request.files:
        file = request.files['file']
        if file:
            df = pd.read_csv(file)
            # Check if the DataFrame contains all expected columns
            if not all(column in df.columns for column in expected_columns):
                return jsonify({'message': 'Error: Missing one or more required columns in the CSV file.'}), 400

            if preprocessor is None:
                raise ValueError("Failed to load preprocessor from S3")
            prepared = preprocessor.transform(df)
            predictions = model.predict(prepared)
            df['PredictedListingRent'] = predictions
            result = df.to_json(orient='records')
            print(result)
            return jsonify({'message': 'Batch predictions made successfully!', 'data': str(result)}), 200

    else:
        data = request.json

        lat,lon = assignCoordinates(data.get("listingAddress"))
        # modelData = pd.read_csv("mainWebAppTable_data.csv")
        modelData = read_csv_from_s3("mcda-hackathon-s3-bucket", "WebApp/mainWebAppTable_data.csv")
        listing_data = modelData[(modelData['listingLatitude'] == lat) & (modelData['listingLongitude'] == lon)]
        if not listing_data.empty:

            listing_data = listing_data.head(1)
            listing_dict = {
            "listingMajorRegion":listing_data.iloc[0]['listingMajorRegion'],
            "listingMinorRegion": listing_data.iloc[0]['listingMinorRegion'],
            "listingLatitude": lat,
            "listingLongitude": lon,
            "listingType": "Management",
            "listingPropertyType": data.get("listingPropertyType"),
            "listingSizeSquareFeet": float(data.get("listingSizeSquareFeet")),
            "bedroomCount": float(data.get("bedroomCount")),
            "bathroomCount": float(data.get("bathroomCount")),
            "heatUtility": float(data.get("heatUtility")),
            "waterUtility": float(data.get("waterUtility")),
            "hydroUtility": float(data.get("hydroUtility")),
            "furnishedUtility": float(data.get("furnishedUtility")),
            "petPolicy": float(data.get("petPolicy")),
            "smokingPolicy": float(data.get("smokingPolicy")),
            "gymAmenity": float(data.get("gymAmenity")),
            "parkingAmenity": float(data.get("parkingAmenity")),
            "acAmenity": float(data.get("acAmenity")),
            "applianceAmenity": float(data.get("applianceAmenity")),
            "storageAmenity": float(data.get("storageAmenity")),
            "transitScore": listing_data.iloc[0]['transitScore'],
            "walkScore": listing_data.iloc[0]['walkScore'],
            "bikeScore": listing_data.iloc[0]['bikeScore'],
            "crimeScore": listing_data.iloc[0]['crimeScore'],
            "retailGroceryScore": listing_data.iloc[0]['retailGroceryScore'],
            "retailRecreationScore": listing_data.iloc[0]['retailRecreationScore'],
            "educationCenterScore": listing_data.iloc[0]['educationCenterScore'],
            "emergencyCenterScore": listing_data.iloc[0]['emergencyCenterScore'],
            }
            
        else:
            minorRegion = fetchMinorRegion(lat,lon)

            listing_dict = {
            "listingMajorRegion": fetchMajorRegion(lat,lon),
            "listingMinorRegion": minorRegion,
            "listingLatitude": lat,
            "listingLongitude": lon,
            "listingType": "Management",
            "listingPropertyType": data.get("listingPropertyType"),
            "listingSizeSquareFeet": float(data.get("listingSizeSquareFeet")),
            "bedroomCount": float(data.get("bedroomCount")),
            "bathroomCount": float(data.get("bathroomCount")),
            "heatUtility": float(data.get("heatUtility")),
            "waterUtility": float(data.get("waterUtility")),
            "hydroUtility": float(data.get("hydroUtility")),
            "furnishedUtility": float(data.get("furnishedUtility")),
            "petPolicy": float(data.get("petPolicy")),
            "smokingPolicy": float(data.get("smokingPolicy")),
            "gymAmenity": float(data.get("gymAmenity")),
            "parkingAmenity": float(data.get("parkingAmenity")),
            "acAmenity": float(data.get("acAmenity")),
            "applianceAmenity": float(data.get("applianceAmenity")),
            "storageAmenity": float(data.get("storageAmenity")),
            "transitScore": fetchTransitScore(lat, lon),
            "walkScore": fetchWalkScore(lat,lon),
            "bikeScore": fetchBikeScore(lat,lon),
            "crimeScore": fetchCrimeScore(minorRegion),
            "retailGroceryScore": fetchRetailGroceryScore(lat,lon),
            "retailRecreationScore": fetchRetailRecreationScore(lat,lon),
            "educationCenterScore": fetchEducationCenterScore(lat,lon),
            "emergencyCenterScore": fetchEmergencyCenterScore(lat,lon),
            }


        # Convert JSON to DataFrame and check columns
        df = pd.DataFrame([listing_dict])
        if not all(column in df.columns for column in expected_columns):
            return jsonify({'message': 'Error: Missing one or more required fields in JSON data.'}), 400
        prepared = preprocessor.transform(df)
        prediction = model.predict(prepared)
        rounded_number = int(round(prediction[0], 0))
        return jsonify({'message': 'Individual prediction made successfully!', 'predictedRent': str(rounded_number)}), 200



@app.route('/api/download_file', methods=['GET'])
@cross_origin()
def download_file():
    file_name = request.args.get('file_name')  # Get the file name from query parameters
    # print(file_name)
    try:
        # Generate a pre-signed URL with no expiration time
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name}
        )
        return jsonify({'url': url})
    except botocore.exceptions.ClientError as e:
        print(e)
        return jsonify({'error': 'Error generating pre-signed URL'})



# route to filter the listings
@app.route('/api/listings/filter', methods=['POST'])
@cross_origin()
def all_listings_filter():
    try:
        filters = request.json

        if filters is None:
            return jsonify({"error": "No filters provided"}), 400

        # Construct the base query
        query = ListingV1.query

        # Apply filters dynamically based on parameters
        for attr, value in filters.items():
            
            if hasattr(ListingV1, attr):
                if attr=='listingRent':
                    min_rent = value['minVal']
                    max_rent = value['maxVal']
                    query = query.filter(ListingV1.listingRent >= min_rent, ListingV1.listingRent <= max_rent)
                elif attr == 'bathroomCount' or attr == 'bedroomCount':
                    print(value)
                    if value==4:
                        query = query.filter(getattr(ListingV1, attr) >= 4)
                    else:
                        query = query.filter(getattr(ListingV1, attr) == value)
                else:
                    query = query.filter(getattr(ListingV1, attr) == value)
            if attr == 'sortBy':
                print(value)
                if value == "asc":
                    query = query.order_by(cast(ListingV1.listingRent, Numeric))
                elif value == "desc":
                    query = query.order_by(desc(cast(ListingV1.listingRent, Numeric)))

        # Execute the query to get filtered listings
        filtered_listings = query.all()
        listings = appendFunc(filtered_listings)

        return jsonify(listings)
    
    except Exception as e:
        error_message = str(e)  
        return jsonify({"error": error_message}), 400
        


# route to get a single listing
@app.route('/api/listing/<int:listing_id>', methods=['GET'])
@cross_origin()
def get_listing_by_id(listing_id):
    try:
        # Retrieve parameters from the request args
        listing = ListingV1.query.filter_by(id=listing_id).first()

        if listing is None:
            return jsonify({"error": "Listing not found"}), 404

        # Convert listing to a dictionary
        listing_dict = {
            'id': listing.id,
        'listingAddress': listing.listingAddress,
        'listingMajorRegion': listing.listingMajorRegion,
        'listingMinorRegion': listing.listingMinorRegion,
        'listingLatitude': listing.listingLatitude,
        'listingLongitude': listing.listingLongitude,
        'listingType': listing.listingType,
        'listingPropertyType': listing.listingPropertyType,
        'listingSizeSquareFeet': listing.listingSizeSquareFeet,
        'bedroomCount': listing.bedroomCount,
        'bathroomCount': listing.bathroomCount,
        'heatUtility': listing.heatUtility,
        'waterUtility': listing.waterUtility,
        'hydroUtility': listing.hydroUtility,
        'furnishedUtility': listing.furnishedUtility,
        'petPolicy': listing.petPolicy,
        'smokingPolicy': listing.smokingPolicy,
        'gymAmenity': listing.gymAmenity,
        'parkingAmenity': listing.parkingAmenity,
        'acAmenity': listing.acAmenity,
        'applianceAmenity': listing.applianceAmenity,
        'storageAmenity': listing.storageAmenity,
        'transitScore': listing.transitScore,
        'walkScore': listing.walkScore,
        'bikeScore': listing.bikeScore,
        'crimeScore': listing.crimeScore,
        'retailGroceryScore': listing.retailGroceryScore,
        'retailRecreationScore': listing.retailRecreationScore,
        'educationCenterScore': listing.educationCenterScore,
        'emergencyCenterScore': listing.emergencyCenterScore,
        'listingRent': listing.listingRent,
        'imageLink': listing.imageLink
        }

        return jsonify(listing_dict)

    except Exception as e:
        error_message = str(e)
        return jsonify({"error": error_message}), 400




#CSV to DB  
@app.route('/api/csv_import', methods=['POST'])
@cross_origin()
def import_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 404
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 403
    
    try:
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")

        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H:%M:%S")

        file_name = now_str + ".csv"

        s3.upload_fileobj(file, bucket_name, "newListingCSVInput/" +today_str + '/' + file_name )
        return jsonify({'message': 'File uploaded successfully'})
    except botocore.exceptions.ClientError as e:
        print(e)
        return jsonify({'error': 'Error uploading file to S3'})




#Add a new listing
@app.route('/api/listings', methods=['POST'])
@cross_origin()
def add_listing():
    # Extract JSON data from the request
    data = request.json
    
    # print(data)
    street_address= data.get('street_address')
    
    new_listing = ListingV1(
    listingAddress=str(data.get('street_address')),
    listingMajorRegion=None,
    listingMinorRegion=None,
    listingLatitude=None,
    listingLongitude=None,
    listingType=str(data.get('property_type')), 
    listingPropertyType=str(data.get('listing_property_type')), 
    listingSizeSquareFeet=str(data.get('square_feet')), 
    bedroomCount=str(data.get('bedroom')),
    bathroomCount=str(data.get('bathroom')),
    heatUtility=str(data.get('heat')),
    waterUtility=str(data.get('water')),
    hydroUtility=str(data.get('electricity')), 
    furnishedUtility=str(data.get('furnished')),
    petPolicy=str(data.get('pet')), 
    smokingPolicy=str(data.get('smoking')),
    gymAmenity=str(data.get('gym')),
    parkingAmenity=str(data.get('parking')),
    acAmenity=str(data.get('ac')), 
    applianceAmenity=str(data.get('appliance')),
    storageAmenity=str(data.get('storage')),
    transitScore=None,
    walkScore=None,
    bikeScore=None, 
    crimeScore=None,  
    retailGroceryScore=None, 
    retailRecreationScore=None, 
    educationCenterScore=None,
    emergencyCenterScore=None,
    listingRent=str(data.get('rent')),
    imageLink=str(data.get('imageLink'))
    )

    

    # Add the new listing to the session and commit it to the database
    db.session.add(new_listing)
    db.session.commit()

    thread = threading.Thread(target=processing_data, args=(app,new_listing.id,))
    thread.start()
    return jsonify({'message': 'Listing added successfully'}), 201



# Route to get all the listings
@app.route('/api/builders', methods=['GET'])
@cross_origin()
def list_builders():
    database_uri = SQLALCHEMY_DATABASE_URI

    # Create the SQLAlchemy engine
    engine = create_engine(database_uri)

    query = f"SELECT * FROM builders"
    df = pd.read_sql(query, engine)
    json_result = df.to_json(orient='records')
    return jsonify(json.loads(json_result))



#route to calculate transit score
@app.route('/api/transit-score/<lat>/<lon>', methods=['GET'])
@cross_origin()
def transit_score(lat,lon):
    transit_score = fetchTransitScore(float(lat),float(lon))
    return jsonify({'score':transit_score}), 200

#route to calculate bike score
@app.route('/api/bike-score/<lat>/<lon>', methods=['GET'])
@cross_origin()
def bike_score(lat,lon):
    bike_score = fetchBikeScore(float(lat),float(lon))
    return jsonify({'score':bike_score}), 200

#route to calculate transit score
@app.route('/api/walk-score/<lat>/<lon>', methods=['GET'])
@cross_origin()
def walk_score(lat,lon):
    walk_score = fetchWalkScore(float(lat),float(lon))
    return jsonify({'score':walk_score}), 200


#route to filter the upcoming projects
@app.route('/api/upcoming-project/filter', methods=['POST'])
@cross_origin()
def upcoming_project_filter():
    # JSON to class
    filter_data = request.json
    project_filter = ProjectFilter(**filter_data)

    # Filter listings based on the filter criteria
    filtered_projects = filter_projects(project_filter)

    # Convert filtered listings to dictionary format
    filtered_projects_dict = [project.__dict__ for project in filtered_projects]

    #set response
    response = jsonify(filtered_projects_dict)
    response.status_code = 200

    return response

#route to get the single upcoming project
@app.route('/api/upcoming-project/<string:project_id>', methods=['GET'])
@cross_origin()
def upcoming_project_detail(project_id):
    selected_project = None
    for project in projects:
        if(project.project_id == project_id):
            selected_project = project
            break

    if selected_project is None:
        return Response("Upcoming Project not found", 404)
    else:
        return jsonify(selected_project.__dict__) , 200


def filter_projects(project_filter):
    filtered_projects = []

    for project in projects:
        # Apply filtering conditions based on ProjectFilter attributes
        if (project_filter.neighbourhood is None or project.neighbourhood == project_filter.neighbourhood) and \
           (project_filter.company_name is None or project.company_name == project_filter.company_name) and \
           (project_filter.project_name is None or project.project_name == project_filter.listing_name) and \
           (project_filter.min_lat is None or project.lat >= project_filter.min_lat) and \
           (project_filter.min_lon is None or project.lon >= project_filter.min_lon) and \
           (project_filter.max_lat is None or project.lat <= project_filter.max_lat) and \
           (project_filter.max_lon is None or project.lon <= project_filter.max_lon) and \
           (project_filter.city is None or project.city == project_filter.city) and \
           (project_filter.property_type is None or project.property_type == project_filter.property_type) and \
           (project_filter.street is None or project.street == project_filter.street):
            filtered_projects.append(project)

    return filtered_projects

def appendFunc(listings):
    result = []

    for listing in listings:
        result.append({
        'id': listing.id,
        'listingAddress': listing.listingAddress,
        'listingMajorRegion': listing.listingMajorRegion,
        'listingMinorRegion': listing.listingMinorRegion,
        'listingLatitude': listing.listingLatitude,
        'listingLongitude': listing.listingLongitude,
        'listingType': listing.listingType,
        'listingPropertyType': listing.listingPropertyType,
        'listingSizeSquareFeet': listing.listingSizeSquareFeet,
        'bedroomCount': listing.bedroomCount,
        'bathroomCount': listing.bathroomCount,
        'heatUtility': listing.heatUtility,
        'waterUtility': listing.waterUtility,
        'hydroUtility': listing.hydroUtility,
        'furnishedUtility': listing.furnishedUtility,
        'petPolicy': listing.petPolicy,
        'smokingPolicy': listing.smokingPolicy,
        'gymAmenity': listing.gymAmenity,
        'parkingAmenity': listing.parkingAmenity,
        'acAmenity': listing.acAmenity,
        'applianceAmenity': listing.applianceAmenity,
        'storageAmenity': listing.storageAmenity,
        'transitScore': listing.transitScore,
        'walkScore': listing.walkScore,
        'bikeScore': listing.bikeScore,
        'crimeScore': listing.crimeScore,
        'retailGroceryScore': listing.retailGroceryScore,
        'retailRecreationScore': listing.retailRecreationScore,
        'educationCenterScore': listing.educationCenterScore,
        'emergencyCenterScore': listing.emergencyCenterScore,
        'listingRent': listing.listingRent,
        'imageLink': listing.imageLink

        })
    
    return result

def assignCoordinates(street_address):
    street_address = street_address.replace(' ', '+')
    province = ",+Nova+Scotia,+"
    country = "CA"
    formatted_address = street_address+province+country
    API_Key="AIzaSyBS9AngpJ44EHDtufErkq0TN-BHDphhofk"
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+formatted_address+'&key='+API_Key)
    response_data= response.json()
    latitude = response_data['results'][0]['geometry']['location']['lat']
    longitude = response_data['results'][0]['geometry']['location']['lng']
    return latitude,longitude

def fetchMajorRegion(latitude, longitude):
    # Load the CSV file
    # file_path = 'MajorRegion.csv'
    df = read_csv_from_s3("mcda-hackathon-s3-bucket", "WebApp/MajorRegion.csv")
    # df = pd.read_csv(file_path)

    # Convert the WKT column to Shapely geometries
    df['geometry'] = df['WKT'].apply(shapely.wkt.loads)
    point = Point(longitude, latitude)
    
    for index, row in df.iterrows():
        if row['geometry'].contains(point):
            return row['name']
    
    return 'Not in any region'

def fetchMinorRegion(latitude, longitude):
    # Load the CSV file
    # file_path = 'MinorRegion.csv'
    # df = pd.read_csv(file_path)
    df = read_csv_from_s3("mcda-hackathon-s3-bucket", "WebApp/MinorRegion.csv")
    

    # Convert the WKT column to Shapely geometries
    df['geometry'] = df['WKT'].apply(shapely.wkt.loads)
    point = Point(longitude, latitude)
    
    for index, row in df.iterrows():
        if row['geometry'].contains(point):
            return row['name']
    
    return 'Not in any region'

def fetchCrimeScore(minor_region):
    # file_path = 'MinorRegion.csv'
    # df = pd.read_csv(file_path)
    df = read_csv_from_s3("mcda-hackathon-s3-bucket", "WebApp/MinorRegion.csv")
    for index, row in df.iterrows():
        if (row['name'] == minor_region):
            return df.at[index,'crimeScoreLabel']

    return 'Safe'

def find_place_nearby(latitude, longitude, keyword, radius=5000):
    api_key = "AIzaSyBS9AngpJ44EHDtufErkq0TN-BHDphhofk"
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
    api_key = "AIzaSyBS9AngpJ44EHDtufErkq0TN-BHDphhofk"
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
    # nearby_df = pd.read_csv("nearbyPlaces.csv")
    nearby_df = read_csv_from_s3("mcda-hackathon-s3-bucket", "WebApp/nearbyPlaces.csv")
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
    # nearby_df = pd.read_csv("nearbyPlaces.csv")
    nearby_df = read_csv_from_s3("mcda-hackathon-s3-bucket", "WebApp/nearbyPlaces.csv")
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
    # nearby_df = pd.read_csv("nearbyPlaces.csv")
    nearby_df = read_csv_from_s3("mcda-hackathon-s3-bucket", "WebApp/nearbyPlaces.csv")
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
    # nearby_df = pd.read_csv("nearbyPlaces.csv")
    nearby_df = read_csv_from_s3("mcda-hackathon-s3-bucket", "WebApp/nearbyPlaces.csv")
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
    api_key = "AIzaSyBS9AngpJ44EHDtufErkq0TN-BHDphhofk"
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
    api_key = "AIzaSyBS9AngpJ44EHDtufErkq0TN-BHDphhofk"
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
    # nearby_df = pd.read_csv("nearbyPlaces.csv")
    nearby_df = read_csv_from_s3("mcda-hackathon-s3-bucket", "WebApp/nearbyPlaces.csv")
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
    # nearby_df = pd.read_csv("nearbyPlaces.csv")
    nearby_df = read_csv_from_s3("mcda-hackathon-s3-bucket", "WebApp/nearbyPlaces.csv")
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

def processing_data(app,new_listing_id):
    with app.app_context():
        listing = ListingV1.query.filter_by(id=new_listing_id).first()
        if listing:
            # print(f"Doing something with the new listing ID: {new_listing_id}")

            # Assign new values
            lat, lon = assignCoordinates(listing.listingAddress)
            listing.listingMajorRegion = str(fetchMajorRegion(lat, lon))
            listing.listingMinorRegion = str(fetchMinorRegion(lat, lon))
            listing.listingLatitude = str(lat)
            listing.listingLongitude = str(lon)
            listing.transitScore = str(fetchTransitScore(lat, lon))
            listing.walkScore = str(fetchWalkScore(lat, lon))
            listing.bikeScore = str(fetchBikeScore(lat, lon))
            listing.crimeScore = str(fetchCrimeScore(listing.listingMinorRegion))
            listing.retailGroceryScore = str(fetchRetailGroceryScore(lat, lon))
            listing.retailRecreationScore = str(fetchRetailRecreationScore(lat, lon))
            listing.educationCenterScore = str(fetchEducationCenterScore(lat, lon))
            listing.emergencyCenterScore = str(fetchEmergencyCenterScore(lat, lon))

            # Commit changes to the database
            try:
                db.session.commit()
                print(f"Listing ID {new_listing_id} updated successfully.")
            except Exception as e:
                db.session.rollback()  # Roll back in case of error
                print(f"Error updating listing ID {new_listing_id}: {e}")



# Run the application
if __name__ == '__main__':
    app.run(debug=True)

