import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import TEXT


application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = (
  'postgresql://'
  + os.environ['RDS_USERNAME']
  + ':'
  + os.environ['RDS_PASSWORD']
  + '@'
  + os.environ['RDS_HOSTNAME']
  + '/'
  + os.environ['RDS_DB_NAME'])
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)


# Geo Data for PUMAs
class PumaPolygon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  geo_code = db.Column(db.Integer)
  puma_name = db.Column(db.String(255))
  state_name = db.Column(db.String(40))
  min_long = db.Column(db.Float, index=True)
  min_lat = db.Column(db.Float, index=True)
  max_long = db.Column(db.Float, index=True)
  max_lat = db.Column(db.Float, index=True)
  points = db.Column(TEXT)

  def __init__(
      self, geo_code, puma_name, state_name, min_long, min_lat, max_long,
      max_lat, points):
    self.geo_code = geo_code
    self.puma_name = puma_name
    self.state_name = state_name
    self.min_long = min_long
    self.min_lat = min_lat
    self.max_long = max_long
    self.max_lat = max_lat
    self.points = points

  def __repr__(self):
    return '<PumaPolygon %s (%s)>' % (
      self.geo_code, self.puma_name)


# Geo Data for Counties and PUMAs combined
# (PUMAs are only included if they are not part of a county)
class CountyPolygon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  geo_code = db.Column(db.Integer)
  name = db.Column(db.String(255))
  min_long = db.Column(db.Float, index=True)
  min_lat = db.Column(db.Float, index=True)
  max_long = db.Column(db.Float, index=True)
  max_lat = db.Column(db.Float, index=True)
  points = db.Column(TEXT)

  def __init__(
      self, geo_code, name, min_long, min_lat, max_long, max_lat, points):
    self.geo_code = geo_code
    self.name = name
    self.min_long = min_long
    self.min_lat = min_lat
    self.max_long = max_long
    self.max_lat = max_lat
    self.points = points

  def __repr__(self):
    return '<CountyPolygon %s (%s)>' % (
      self.geo_code, self.name)


# Geo Data for States
class StatePolygon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  geo_code = db.Column(db.Integer)
  name = db.Column(db.String(255))
  usps = db.Column(db.String(2))
  min_long = db.Column(db.Float, index=True)
  min_lat = db.Column(db.Float, index=True)
  max_long = db.Column(db.Float, index=True)
  max_lat = db.Column(db.Float, index=True)
  points = db.Column(TEXT)

  def __init__(
      self, geo_code, name, usps, min_long, min_lat, max_long, max_lat, points):
    self.geo_code = geo_code
    self.name = name
    self.usps = usps
    self.min_long = min_long
    self.min_lat = min_lat
    self.max_long = max_long
    self.max_lat = max_lat
    self.points = points

  def __repr__(self):
    return '<StatePolygon %s (%s)>' % (
      self.geo_code, self.name)


# Demographic Data for PUMAs
class PumaPerson(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  geo_code = db.Column(db.Integer, index=True)
  person_weight = db.Column(db.Integer)
  sex = db.Column(db.Integer, index=True)
  marriage_status = db.Column(db.Integer, index=True)
  race = db.Column(db.Integer, index=True)
  education = db.Column(db.Integer, index=True)
  housing_status = db.Column(db.Integer, index=True)
  children_status = db.Column(db.Integer, index=True)
  age = db.Column(db.Integer, index=True)

  def __init__(
      self, geo_code, person_weight, sex, marriage_status, race, education,
      housing_status, children_status, age):
    self.geo_code = geo_code
    self.person_weight = person_weight
    self.sex = sex
    self.marriage_status = marriage_status
    self.race = race
    self.education = education
    self.housing_status = housing_status
    self.children_status = children_status
    self.age = age

  def __repr__(self):
    return '<PumaPerson %d, %d>' % (self.age, self.sex)


# Demographic Data for Counties and PUMAs
class CountyPerson(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  geo_code = db.Column(db.Integer, index=True)
  person_weight = db.Column(db.Integer)
  sex = db.Column(db.Integer, index=True)
  marriage_status = db.Column(db.Integer, index=True)
  race = db.Column(db.Integer, index=True)
  education = db.Column(db.Integer, index=True)
  housing_status = db.Column(db.Integer, index=True)
  children_status = db.Column(db.Integer, index=True)
  age = db.Column(db.Integer, index=True)

  def __init__(
      self, geo_code, person_weight, sex, marriage_status, race, education,
      housing_status, children_status, age):
    self.geo_code = geo_code
    self.person_weight = person_weight
    self.sex = sex
    self.marriage_status = marriage_status
    self.race = race
    self.education = education
    self.housing_status = housing_status
    self.children_status = children_status
    self.age = age

  def __repr__(self):
    return '<CountyOrPumaPerson %d, %d>' % (self.age, self.sex)


# Demographic Data for States
class StatePerson(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  geo_code = db.Column(db.Integer, index=True)
  person_weight = db.Column(db.Integer)
  sex = db.Column(db.Integer, index=True)
  marriage_status = db.Column(db.Integer, index=True)
  race = db.Column(db.Integer, index=True)
  education = db.Column(db.Integer, index=True)
  housing_status = db.Column(db.Integer, index=True)
  children_status = db.Column(db.Integer, index=True)
  age = db.Column(db.Integer, index=True)

  def __init__(
      self, geo_code, person_weight, sex, marriage_status, race, education,
      housing_status, children_status, age):
    self.geo_code = geo_code
    self.person_weight = person_weight
    self.sex = sex
    self.marriage_status = marriage_status
    self.race = race
    self.education = education
    self.housing_status = housing_status
    self.children_status = children_status
    self.age = age

  def __repr__(self):
    return '<StatePerson %d, %d>' % (self.age, self.sex)
