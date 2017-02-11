import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
  'mysql://anonamousemapper:'
  + os.environ['DB_PASS']
  +'@localhost/mapping_site')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Geo Data for PUMAs
class PumaPolygon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  geo_code = db.Column(db.Integer)
  puma_name = db.Column(db.String(255))
  state_name = db.Column(db.String(40))
  min_x = db.Column(db.Float, index=True)
  min_y = db.Column(db.Float, index=True)
  max_x = db.Column(db.Float, index=True)
  max_y = db.Column(db.Float, index=True)
  points = db.relationship('PumaPoint', backref='puma_polygon', lazy='dynamic')

  def __init__(
      self, geo_code, puma_name, state_name, min_x, min_y, max_x, max_y):
    self.geo_code = geo_code
    self.puma_name = puma_name
    self.state_name = state_name
    self.min_x = min_x
    self.min_y = min_y
    self.max_x = max_x
    self.max_y = max_y

  def __repr__(self):
    return '<PumaPolygon %s (%s)>' % (
      self.geo_code, self.puma_name)

class PumaPoint(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  longitude = db.Column(db.Float)
  latitude = db.Column(db.Float)
  puma_polygon_id = db.Column(
    db.Integer, db.ForeignKey('puma_polygon.id'), index=True)

  def __init__(self, longitude, latitude):
    self.longitude = longitude
    self.latitude = latitude

  def __repr__(self):
    return '<PumaPoint %f, %f>' % (self.longtiude, self.latitude)


# Geo Data for Counties and PUMAs combined
# (PUMAs are only included if they are not part of a county)
class CountyPolygon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  geo_code = db.Column(db.Integer)
  name = db.Column(db.String(255))
  min_x = db.Column(db.Float, index=True)
  min_y = db.Column(db.Float, index=True)
  max_x = db.Column(db.Float, index=True)
  max_y = db.Column(db.Float, index=True)
  points = db.relationship(
    'CountyPoint', backref='county_polygon', lazy='dynamic')

  def __init__(
      self, geo_code, name, min_x, min_y, max_x, max_y):
    self.geo_code = geo_code
    self.name = name
    self.min_x = min_x
    self.min_y = min_y
    self.max_x = max_x
    self.max_y = max_y

  def __repr__(self):
    return '<CountyPolygon %s (%s)>' % (
      self.geo_code, self.name)

class CountyPoint(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  longitude = db.Column(db.Float)
  latitude = db.Column(db.Float)
  county_polygon_id = db.Column(
    db.Integer, db.ForeignKey('county_polygon.id'), index=True)

  def __init__(self, longitude, latitude):
    self.longitude = longitude
    self.latitude = latitude

  def __repr__(self):
    return '<CountyPoint %f, %f>' % (self.longtiude, self.latitude)


# Geo Data for States
class StatePolygon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  geo_code = db.Column(db.Integer)
  name = db.Column(db.String(255))
  usps = db.Column(db.String(2))
  min_x = db.Column(db.Float, index=True)
  min_y = db.Column(db.Float, index=True)
  max_x = db.Column(db.Float, index=True)
  max_y = db.Column(db.Float, index=True)
  points = db.relationship(
    'StatePoint', backref='state_polygon', lazy='dynamic')

  def __init__(
      self, geo_code, name, usps, min_x, min_y, max_x, max_y):
    self.geo_code = geo_code
    self.name = name
    self.usps = usps
    self.min_x = min_x
    self.min_y = min_y
    self.max_x = max_x
    self.max_y = max_y

  def __repr__(self):
    return '<StatePolygon %s (%s)>' % (
      self.geo_code, self.name)

class StatePoint(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  longitude = db.Column(db.Float)
  latitude = db.Column(db.Float)
  state_polygon_id = db.Column(
    db.Integer, db.ForeignKey('state_polygon.id'), index=True)

  def __init__(self, longitude, latitude):
    self.longitude = longitude
    self.latitude = latitude

  def __repr__(self):
    return '<StatePoint %f, %f>' % (self.longtiude, self.latitude)


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
