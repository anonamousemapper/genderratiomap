'''
From mapsite dir:
  python -m scripts.basic_shapefile_to_lat_long_csv \
  geo_polygons/county/2014_1to5m/cb_2014_us_county_5m \
  temp_data/county_boundaries_1to5m.csv
  
  OR
  
  python -m scripts.basic_shapefile_to_lat_long_csv \
  geo_polygons/state/2014_1to20m/cb_2014_us_state_20m \
  temp_data/state_boundaries_1to20m.csv
'''

import csv
import shapefile
import sys

from app.constants import *
from pyproj import Proj, transform

if len(sys.argv) != 3:
  print (
    'python -m basic_shapefile_to_lat_long_csv ' +
    '<path/to/shapefile> <path/to/output.csv>')
  exit()

# Get the boundary values for this set of points.
def get_boundary_points(points_list):
  min_lng, min_lat = points_list[0]
  max_lng, max_lat = points_list[0]
  for lng, lat in points_list:
    if lng < min_lng:
      min_lng = lng
    if lng > max_lng:
      max_lng = lng
    if lat < min_lat:
      min_lat = lat
    if lat > max_lat:
      max_lat = lat
  return min_lng, min_lat, max_lng, max_lat

with open(sys.argv[2], 'wb') as csv_file:
  # Get a pointer to the data.
  shape_file = shapefile.Reader(sys.argv[1])

  # Make a list of all the field names for the CSV.
  shape_fields = shape_file.fields[1:]
  field_names = []
  for field in shape_fields:
    field_names.append(field[0])
  field_names.append(FIELD_NAME_MIN_X)
  field_names.append(FIELD_NAME_MIN_Y)
  field_names.append(FIELD_NAME_MAX_X)
  field_names.append(FIELD_NAME_MAX_Y)
  field_names.append(FIELD_NAME_POINTS)

  # Create CSV with heading.
  csv_writer = csv.DictWriter(csv_file, field_names)
  csv_writer.writeheader()

  # Loop through each shape.
  for shape_data in shape_file.iterShapeRecords():
    record = shape_data.record
    shape = shape_data.shape
    # Check if the shape is a normal polygon.
    if shape.shapeType != 15:
      print 'Found a shape that is not a PolygonZ.'
      continue
    # Loop through each polygon within the shape.
    max_i = len(shape.parts) - 1
    for i, point_index in enumerate(shape.parts):
      fields_dict = {}
      # Copy over field data.
      for j, field_value in enumerate(record):
        fields_dict[field_names[j]] = field_value
      # Get points.
      if i < max_i:
        lat_lng_points = shape.points[point_index:shape.parts[i+1]]
      else:
        lat_lng_points = shape.points[point_index:]
      fields_dict[FIELD_NAME_POINTS] = str(lat_lng_points)
      # Calculate bounding box.
      (fields_dict[FIELD_NAME_MIN_X], fields_dict[FIELD_NAME_MIN_Y],
       fields_dict[FIELD_NAME_MAX_X], fields_dict[FIELD_NAME_MAX_Y]) = (
        get_boundary_points(lat_lng_points))
      csv_writer.writerow(fields_dict)
