'''
From mapsite dir:
  python -m scripts.create_db \
  temp_data/puma_boundaries_simplified_10.csv \
  temp_data/merged_county_and_puma_boundaries.csv \
  temp_data/state_boundaries_1to20m.csv \
  temp_data/simplified_puma_data.csv \
  temp_data/simplified_county_and_puma_data.csv \
  temp_data/simplified_state_data.csv
'''

from __future__ import print_function

import ast
import csv
import sys

from app.constants import *
from app.models import (
  db, PumaPolygon, PumaPoint, CountyPolygon, CountyPoint, StatePolygon,
  StatePoint, PumaPerson, CountyPerson, StatePerson)

csv.field_size_limit(sys.maxsize)

if len(sys.argv) != 7:
  print(
    'python -m create_db '
    '<path/to/puma_polygon_data.csv> '
    '<path/to/county_polygon_data.csv> '
    '<path/to/state_polygon_data.csv> '
    '<path/to/puma_demographic_data.csv>'
    '<path/to/county_demographic_data.csv>'
    '<path/to/state_demographic_data.csv>')
  exit()

with open(
    sys.argv[1]) as puma_polygon_csv_file, open(
    sys.argv[2]) as county_polygon_csv_file, open(
    sys.argv[3]) as state_polygon_csv_file, open(
    sys.argv[4]) as puma_demographics_csv_file, open(
    sys.argv[5]) as county_demographics_csv_file, open(
    sys.argv[6]) as state_demographics_csv_file:
  # Clear out all the old data in the database.
  answer = raw_input(
    'This will delete your database and recreate it. ' +
    'Do you want to continue? (y/N) ')
  if answer.lower() != 'y':
    exit()
  print('Dropping all tables')
  db.drop_all()

  # Recreate the database.
  print('Recreating table schema')
  db.create_all()

  # Add each PUMA polygon to the database.
  print('Begin reading PUMA polygon CSV file')
  csv_reader = csv.DictReader(puma_polygon_csv_file)
  for i, row in enumerate(csv_reader):
    geo_code = int(row['GEOID10'])
    polygon = PumaPolygon(
      geo_code, row['NAMELSAD10'].decode('utf-8', 'ignore'), row['STATE10'],
      row[FIELD_NAME_MIN_X], row[FIELD_NAME_MIN_Y], row[FIELD_NAME_MAX_X],
      row[FIELD_NAME_MAX_Y])
    points = ast.literal_eval(row[FIELD_NAME_POINTS])
    for point in points:
      polygon.points.append(PumaPoint(point[0], point[1]))
    db.session.add(polygon)
    if i % 1000 == 0:
      db.session.commit()
    print(str(i) + ' polygon rows completed', end='\r')
    sys.stdout.flush()
  # Commit the final rows before exiting.
  db.session.commit()
  print(str(i) + ' polygon rows completed')

  # Add each county polygon to the database.
  print('Begin reading county polygon CSV file')
  csv_reader = csv.DictReader(county_polygon_csv_file)
  for i, row in enumerate(csv_reader):
    polygon = CountyPolygon(
      row[GEO_CODE], row[NAME].decode('utf-8', 'ignore'), row[FIELD_NAME_MIN_X],
      row[FIELD_NAME_MIN_Y], row[FIELD_NAME_MAX_X], row[FIELD_NAME_MAX_Y])
    points = ast.literal_eval(row[FIELD_NAME_POINTS])
    for point in points:
      polygon.points.append(CountyPoint(point[0], point[1]))
    db.session.add(polygon)
    if i % 1000 == 0:
      db.session.commit()
    print(str(i) + ' polygon rows completed', end='\r')
    sys.stdout.flush()
  # Commit the final rows before exiting.
  db.session.commit()
  print(str(i) + ' polygon rows completed')

  # Add each state polygon to the database.
  print('Begin reading state polygon CSV file')
  csv_reader = csv.DictReader(state_polygon_csv_file)
  for i, row in enumerate(csv_reader):
    polygon = StatePolygon(
      row['STATEFP'], row['NAME'], row['STUSPS'], row[FIELD_NAME_MIN_X],
      row[FIELD_NAME_MIN_Y], row[FIELD_NAME_MAX_X], row[FIELD_NAME_MAX_Y])
    points = ast.literal_eval(row[FIELD_NAME_POINTS])
    for point in points:
      polygon.points.append(StatePoint(point[0], point[1]))
    db.session.add(polygon)
    if i % 1000 == 0:
      db.session.commit()
    print(str(i) + ' polygon rows completed', end='\r')
    sys.stdout.flush()
  # Commit the final rows before exiting.
  db.session.commit()
  print(str(i) + ' polygon rows completed')
  
  # Add all the PUMA demographics data to the database.
  print('Begin reading PUMA demographics CSV file')
  csv_reader = csv.DictReader(puma_demographics_csv_file)
  for i, row in enumerate(csv_reader):
    person = PumaPerson(
      row[GEO_CODE], row[PERSON_WEIGHT], row[SEX], row[MARRIAGE_STATUS],
      row[RACE], row[EDUCATION], row[HOUSING_STATUS], row[CHILDREN_STATUS],
      row[AGE])
    db.session.add(person)
    if i % 10000 == 0:
      db.session.commit()
    print(str(i) + ' ipums rows completed', end='\r')
    sys.stdout.flush()
  # Commit the final rows before exiting.
  db.session.commit()
  print(str(i) + ' ipums rows completed')

  # Add all the county demographics data to the database.
  print('Begin reading county demographics CSV file')
  csv_reader = csv.DictReader(county_demographics_csv_file)
  for i, row in enumerate(csv_reader):
    person = CountyPerson(
      row[GEO_CODE], row[PERSON_WEIGHT], row[SEX], row[MARRIAGE_STATUS],
      row[RACE], row[EDUCATION], row[HOUSING_STATUS], row[CHILDREN_STATUS],
      row[AGE])
    db.session.add(person)
    if i % 10000 == 0:
      db.session.commit()
    print(str(i) + ' ipums rows completed', end='\r')
    sys.stdout.flush()
  # Commit the final rows before exiting.
  db.session.commit()
  print(str(i) + ' ipums rows completed')

  # Add all the state demographics data to the database.
  print('Begin reading state demographics CSV file')
  csv_reader = csv.DictReader(state_demographics_csv_file)
  for i, row in enumerate(csv_reader):
    person = StatePerson(
      row[GEO_CODE], row[PERSON_WEIGHT], row[SEX], row[MARRIAGE_STATUS],
      row[RACE], row[EDUCATION], row[HOUSING_STATUS], row[CHILDREN_STATUS],
      row[AGE])
    db.session.add(person)
    if i % 10000 == 0:
      db.session.commit()
    print(str(i) + ' ipums rows completed', end='\r')
    sys.stdout.flush()
  # Commit the final rows before exiting.
  db.session.commit()
  print(str(i) + ' ipums rows completed')
