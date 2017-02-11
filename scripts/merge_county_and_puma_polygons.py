'''
From mapsite dir:
  python -m scripts/merge_county_and_puma_polygons \
  temp_data/simplified_county_and_puma_data.csv \
  temp_data/county_boundaries_1to5m.csv \
  temp_data/puma_boundaries_simplified_100.csv \
  temp_data/merged_county_and_puma_boundaries.csv
'''

import csv
import sys

from app.constants import *

csv.field_size_limit(sys.maxsize)

if len(sys.argv) != 5:
  print(
    'python -m merge_county_and_puma_polygons ' +
    '<path/to/merged_county_puma_data.csv> <path/to/county_boundaries.csv> ' +
    '<path/to/puma_boundaries.csv> <path/to/output_file.csv>')
  exit()


# Create list of geo_codes that we want.
geo_codes = set()
with open(sys.argv[1], 'r') as in_file:
  # Make a CSV reader for the input file.
  csv_reader = csv.DictReader(in_file)
  
  # Loop through each row in the input csv and add a geo_code to the list.
  for row_dict in csv_reader:
    geo_codes.add(int(row_dict[GEO_CODE]))

# Go through county and puma polygon files and pull out the ones that are
# needed.
with open(sys.argv[2], 'r') as county_polygons_file, open(
    sys.argv[3], 'r') as puma_polygons_file, open(
    sys.argv[4], 'wb') as merged_polygons_file:
  # Make a CSV writer for the merged file.
  field_names = [
    GEO_CODE, NAME, FIELD_NAME_MIN_X, FIELD_NAME_MIN_Y, FIELD_NAME_MAX_X,
    FIELD_NAME_MAX_Y, FIELD_NAME_POINTS]
  csv_writer = csv.DictWriter(merged_polygons_file, field_names)
  csv_writer.writeheader()
  
  # Handle counties first.
  county_reader = csv.DictReader(county_polygons_file)
  for row_dict in county_reader:
    geo_code = (
      10000000 + int(row_dict['STATEFP']) * 100000 + int(row_dict['COUNTYFP']))
    if geo_code in geo_codes:
      csv_writer.writerow({
        GEO_CODE: geo_code,
        NAME: row_dict['NAME'],
        FIELD_NAME_MIN_X: row_dict[FIELD_NAME_MIN_X],
        FIELD_NAME_MIN_Y: row_dict[FIELD_NAME_MIN_Y],
        FIELD_NAME_MAX_X: row_dict[FIELD_NAME_MAX_X],
        FIELD_NAME_MAX_Y: row_dict[FIELD_NAME_MAX_Y],
        FIELD_NAME_POINTS: row_dict[FIELD_NAME_POINTS]})

  # Handle PUMAs next.
  puma_reader = csv.DictReader(puma_polygons_file)
  for row_dict in puma_reader:
    geo_code = int(row_dict['GEOID10'])
    if geo_code in geo_codes:
      csv_writer.writerow({
        GEO_CODE: geo_code,
        NAME: row_dict['NAMELSAD10'],
        FIELD_NAME_MIN_X: row_dict[FIELD_NAME_MIN_X],
        FIELD_NAME_MIN_Y: row_dict[FIELD_NAME_MIN_Y],
        FIELD_NAME_MAX_X: row_dict[FIELD_NAME_MAX_X],
        FIELD_NAME_MAX_Y: row_dict[FIELD_NAME_MAX_Y],
        FIELD_NAME_POINTS: row_dict[FIELD_NAME_POINTS]})
      
  
