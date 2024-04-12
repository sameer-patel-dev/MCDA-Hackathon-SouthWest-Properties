from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# # Create an engine to connect to the MySQL database
# # Replace 'mysql+mysqlconnector://username:password@hostname:port/databasename' with your MySQL connection string
# engine = create_engine('mysql+mysqlconnector://username:password@hostname:port/databasename')


class Listing:
    def __init__(self, listing_id, created_on, listing_name, company_name, property_type, rent, bedroom, bathroom, 
                 street_address, city, neighbourhood, province, lat, lon, parking, heat, water, electricity):
        self.listing_id = listing_id
        self.created_on = created_on
        self.listing_name = listing_name
        self.company_name = company_name
        self.property_type = property_type
        self.rent = rent
        self.bedroom = bedroom
        self.bathroom = bathroom
        self.street_address = street_address
        self.neighbourhood = neighbourhood
        self.city = city
        self.province = province
        self.lat = lat
        self.lon = lon
        self.parking = parking
        self.heat = heat
        self.water = water
        self.electricity = electricity
        
class Project:
    def __init__(self, project_id, created_on, project_name, company_name, property_type,
                 street_address, neighbourhood, city, province, lat, lon):
        self.project_id = project_id
        self.created_on = created_on
        self.project_name = project_name
        self.company_name = company_name
        self.property_type = property_type
        self.street_address = street_address
        self.neighbourhood = neighbourhood
        self.city = city
        self.province = province
        self.lat = lat
        self.lon = lon

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
    
# class ListingImages(db.model):
    # __tablename__ = 'mainWebAppTable'
