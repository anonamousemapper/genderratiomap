'''
From mapsite dir:
  ogr2ogr \
  ./geo_polygons/puma/2010_simplified_100/PUMA_2010_simplified_100.shp \
  ./geo_polygons/puma/2010/PUMA_2010.shp -simplify 100.0

  python -m scripts.puma_shapefile_to_lat_long_csv \
  geo_polygons/puma/2010_simplified_100/PUMA_2010_simplified_100 \
  temp_data/puma_boundaries_simplified_100.csv

OR

  ogr2ogr \
  ./geo_polygons/puma/2010_simplified_10/PUMA_2010_simplified_10.shp \
  ./geo_polygons/puma/2010/PUMA_2010.shp -simplify 10.0

  python -m scripts.puma_shapefile_to_lat_long_csv \
  geo_polygons/puma/2010_simplified_10/PUMA_2010_simplified_10 \
  temp_data/puma_boundaries_simplified_10.csv
'''

import csv
import shapefile
import sys

from app.constants import *
from app.util import convert_and_round_points_list, get_boundary_points
from pyproj import Proj, transform

if len(sys.argv) != 3:
  print (
    'python -m puma_shapefile_to_lat_long_csv ' +
    '<path/to/shapefile> <path/to/output.csv>')
  exit()

# USA Contiguous Albers Equal Area Conic
inProj = Proj(
  '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 '
  '+ellps=GRS80 +datum=NAD83 +units=m +no_defs')
# WGS 84 (Lat Long)
outProj = Proj(init='epsg:4326')

# Converts a list of points in place from USA Contiguous Albers Equal Area Conic
# to WGS 84.
def convert_point_type(points_list):
  converted_points = []
  for point in points_list:
    converted_points.append(transform(inProj, outProj, point[0], point[1]))
  return converted_points

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
    if shape.shapeType != 5:
      print 'Found a shape that is not a Polygon.'
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
        lat_lng_points = (
          convert_and_round_points_list(
            convert_point_type(shape.points[point_index:shape.parts[i+1]])))
      else:
        lat_lng_points = (
          convert_and_round_points_list(
            convert_point_type(shape.points[point_index:])))
      fields_dict[FIELD_NAME_POINTS] = str(lat_lng_points)
      # Calculate bounding box.
      (fields_dict[FIELD_NAME_MIN_X],
       fields_dict[FIELD_NAME_MIN_Y],
       fields_dict[FIELD_NAME_MAX_X],
       fields_dict[FIELD_NAME_MAX_Y]) = (
        get_boundary_points(lat_lng_points))
      csv_writer.writerow(fields_dict)
