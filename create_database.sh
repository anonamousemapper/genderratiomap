# Delete all the old data.
rm -r geo_polygons/puma/2010_simplified_10
rm -r geo_polygons/puma/2010_simplified_100
rm temp_data/*

# Create the simplified puma polygons from the full resolution ones.
mkdir geo_polygons/puma/2010_simplified_10
ogr2ogr \
  geo_polygons/puma/2010_simplified_10/PUMA_2010_simplified_10.shp \
  geo_polygons/puma/2010/PUMA_2010.shp -simplify 10.0

mkdir geo_polygons/puma/2010_simplified_100
ogr2ogr \
  geo_polygons/puma/2010_simplified_100/PUMA_2010_simplified_100.shp \
  geo_polygons/puma/2010/PUMA_2010.shp -simplify 100.0

# Create all the demographic data.
python -m scripts.ipum_csv_to_simplified_puma_csv \
  demographic_data/ipums_by_puma_county_and_state_acs_2014/usa_00007.csv \
  temp_data/simplified_puma_data.csv

python -m scripts.ipum_csv_to_simplified_county_and_puma_csv \
  demographic_data/ipums_by_puma_county_and_state_acs_2014/usa_00007.csv \
  temp_data/simplified_county_and_puma_data.csv

python -m scripts.ipum_csv_to_simplified_state_csv \
  demographic_data/ipums_by_puma_county_and_state_acs_2014/usa_00007.csv \
  temp_data/simplified_state_data.csv

# Create all the polygon data.
python -m scripts.puma_shapefile_to_lat_long_csv \
  geo_polygons/puma/2010_simplified_10/PUMA_2010_simplified_10 \
  temp_data/puma_boundaries_simplified_10.csv

python -m scripts.puma_shapefile_to_lat_long_csv \
  geo_polygons/puma/2010_simplified_100/PUMA_2010_simplified_100 \
  temp_data/puma_boundaries_simplified_100.csv

python -m scripts.basic_shapefile_to_lat_long_csv \
  geo_polygons/county/2014_1to5m/cb_2014_us_county_5m \
  temp_data/county_boundaries_1to5m.csv

python -m scripts.basic_shapefile_to_lat_long_csv \
  geo_polygons/state/2014_1to20m/cb_2014_us_state_20m \
  temp_data/state_boundaries_1to20m.csv

# Delete the intermediate shapefiles.
rm -r geo_polygons/puma/2010_simplified_10
rm -r geo_polygons/puma/2010_simplified_100

# Merge the low res puma data (puma_boundaries_simplified_100.csv) and
# county data (county_boundaries_1to5m.csv) together based on the
# simplified_county_and_puma_data.csv file.
python -m scripts.merge_county_and_puma_polygons \
  temp_data/simplified_county_and_puma_data.csv \
  temp_data/county_boundaries_1to5m.csv \
  temp_data/puma_boundaries_simplified_100.csv \
  temp_data/merged_county_and_puma_boundaries.csv

# Delete the now unnecessary files.
rm temp_data/county_boundaries_1to5m.csv
rm temp_data/puma_boundaries_simplified_100.csv

# Build the database with the final output.
python -m scripts.create_db \
  temp_data/puma_boundaries_simplified_10.csv \
  temp_data/merged_county_and_puma_boundaries.csv \
  temp_data/state_boundaries_1to20m.csv \
  temp_data/simplified_puma_data.csv \
  temp_data/simplified_county_and_puma_data.csv \
  temp_data/simplified_state_data.csv

# Delete all the temp data now that it has been added to the database.
rm temp_data/*
