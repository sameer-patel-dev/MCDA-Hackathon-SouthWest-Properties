from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ListingFilter:
    def __init__(self, neighbourhood=None, company_name=None, listing_name=None, min_rent=None, max_rent=None,
                 min_lat=None, max_lat=None, min_lon=None, max_lon=None, parking=None, heat=None, water=None,
                 electricity=None, city=None, property_type=None, street=None, sort=None):
        self.neighbourhood = neighbourhood
        self.company_name = company_name
        self.listing_name = listing_name
        self.min_rent = min_rent
        self.max_rent = max_rent
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon
        self.parking = parking
        self.heat = heat
        self.water = water
        self.electricity = electricity
        self.city = city
        self.property_type = property_type
        self.street = street
        self.sort = sort


class ProjectFilter:
    def __init__(self, neighbourhood=None, company_name=None, project_name=None, min_lat=None, min_lon=None,max_lat=None, max_lon=None,
                 city=None, property_type=None, street=None, sort=None):
        self.neighbourhood = neighbourhood
        self.company_name = company_name
        self.project_name = project_name
        self.min_lat = min_lat
        self.min_lon = min_lon
        self.max_lon = max_lon
        self.max_lat = max_lat
        self.city = city
        self.property_type = property_type
        self.street = street
        self.sort = sort


class ListingDto:
    def __init__(self, listing_name, company_name, property_type, rent, bedroom, bathroom,
                 street_address, neighbourhood, city, province,
                 parking, heat, water, electricity):
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
        self.parking = parking
        self.heat = heat
        self.water = water
        self.electricity = electricity


