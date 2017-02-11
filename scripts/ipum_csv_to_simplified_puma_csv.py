'''
From mapsite dir:
  python -m scripts/ipum_csv_to_simplified_puma_csv \
  demographic_data/ipums_by_puma_county_and_state_acs_2014/usa_00007.csv \
  temp_data/simplified_puma_data.csv
'''

import csv
import sys

from app.constants import *
from datetime import date

if len(sys.argv) != 3:
  print('python -m ipum_csv_to_simplified_puma_csv <path/to/input_data.csv> ' +
        '<path/to/output_data.csv>')
  exit()

def build_simplified_row_dict(row_dict):
  simplified_row = {}
  
  # Geocode (state fip + puma). (PUMA is a 5 digit int, hence why we multiply
  # STATEFIP by 100000.)
  simplified_row[GEO_CODE] = (
    100000 * int(row_dict['STATEFIP']) + int(row_dict['PUMA']))
  
  # Weight (how many people this row represents).
  simplified_row[PERSON_WEIGHT] = int(row_dict['PERWT'])
  
  # Sex.
  simplified_row[SEX] = int(row_dict['SEX'])
  
  # Marriage status.
  marriage_status = int(row_dict['MARST'])
  if marriage_status in (1, 2, 3):
    simplified_row[MARRIAGE_STATUS] = MARRIED
  elif marriage_status in (4, 5):
    simplified_row[MARRIAGE_STATUS] = SINGLE_PREVIOUSLY_MARRIED
  else:
    simplified_row[MARRIAGE_STATUS] = SINGLE_NEVER_MARRIED
  
  # Race.
  is_hispanic = int(row_dict['HISPAN']) > 0
  race = int(row_dict['RACESINGD'])
  if is_hispanic:
    simplified_row[RACE] = HISPANIC
  elif race == 10:
    simplified_row[RACE] = WHITE
  elif race == 20:
    simplified_row[RACE] = BLACK
  elif race in (30, 31, 32):
    simplified_row[RACE] = NATIVE_AMERICAN
  elif race == 40:
    simplified_row[RACE] = INDIAN
  elif race in (41, 43, 44):
    simplified_row[RACE] = EAST_ASIAN
  else:
    simplified_row[RACE] = OTHER
  
  # Education level.
  education = int(row_dict['EDUCD'])
  if education <= 100:
    simplified_row[EDUCATION] = NO_DEGREE
  elif education == 101:
    simplified_row[EDUCATION] = BACHELORS
  elif education == 114:
    simplified_row[EDUCATION] = MASTERS
  else:
    simplified_row[EDUCATION] = DOCTORATE
  
  # Housing status (whether or not they live alone).
  num_people_in_household = int(row_dict['NUMPREC'])
  num_fams_in_household = int(row_dict['NFAMS'])
  num_family_members_in_household = int(row_dict['FAMSIZE'])
  if(num_people_in_household > 1 or
     num_fams_in_household > 1 or
     num_family_members_in_household > 1):
    simplified_row[HOUSING_STATUS] = LIVES_WITH_OTHERS
  else:
    simplified_row[HOUSING_STATUS] = LIVES_ALONE
    
  # Children status (if the person has children at home with them or not).
  # Note that this does not distinguish between whether the person has never
  # had kids and has had kids, but the kids do not live at home. There seems
  # to be no way to get this from the underlying data.
  if int(row_dict['NCHILD']) == 0:
    simplified_row[CHILDREN_STATUS] = NO_CHILDREN_OR_NO_CHILDREN_AT_HOME
  else:
    simplified_row[CHILDREN_STATUS] = HAS_CHILDREN_AT_HOME
  
  # Age (have to add in the difference between the sample year and now).
  simplified_row[AGE] = (
    int(row_dict['AGE']) + date.today().year - int(row_dict['YEAR']))
  
  return simplified_row
  
def get_simplified_row_key(simplified_row_dict):
  return (
    format(simplified_row_dict[GEO_CODE], '07') +
    format(simplified_row_dict[SEX], '1') +
    format(simplified_row_dict[MARRIAGE_STATUS], '1') +
    format(simplified_row_dict[RACE], '1') +
    format(simplified_row_dict[EDUCATION], '1') +
    format(simplified_row_dict[HOUSING_STATUS], '1') +
    format(simplified_row_dict[CHILDREN_STATUS], '1') +
    format(simplified_row_dict[AGE], '03')
  )

with open(sys.argv[1], 'r') as in_file, open(sys.argv[2], 'wb') as out_file:
  # Make a CSV reader for the input file.
  # Format of input is:
  # YEAR DATANUM SERIAL NUMPREC HHWT STATEFIP COUNTYFIPS PUMA GQ NFAMS PERNUM
  # PERWT FAMSIZE NCHILD SEX AGE MARST MARRNO HISPAN HISPAND RACESING RACESINGD
  # EDUC EDUCD
  csv_reader = csv.DictReader(in_file)
  
  # Loop through each row in the input csv and merge simplified rows that are
  # the same.
  merged_rows = {}
  for row_dict in csv_reader:
    simplified_row_dict = build_simplified_row_dict(row_dict)
    key = get_simplified_row_key(simplified_row_dict)
    
    if key in merged_rows:
      merged_rows[key][PERSON_WEIGHT] += simplified_row_dict[PERSON_WEIGHT]
    else:
      merged_rows[key] = simplified_row_dict
  
  # Make a CSV writer for the output file.
  field_names = [
    GEO_CODE, PERSON_WEIGHT, SEX, MARRIAGE_STATUS, RACE, EDUCATION,
    HOUSING_STATUS, CHILDREN_STATUS, AGE]  
  csv_writer = csv.DictWriter(out_file, field_names)
  csv_writer.writeheader()
  
  # Write each row in the dict to the csv.
  for simplified_row in merged_rows.itervalues():
    csv_writer.writerow(simplified_row)
