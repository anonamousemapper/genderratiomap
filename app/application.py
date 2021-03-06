import datetime

from geometry import get_geometry
from models import application
from stats import get_stats
from util import get_fidelity
from flask import jsonify, render_template, request


@application.route('/')
def index():
	return render_template('index.html')

@application.route('/json/update_criteria', methods=['POST'])
def update_criteria():
  criteria_request = request.get_json()
  fidelity = int(criteria_request['fidelity'])
  
  # Get the stats for each geo_code in the request based on the criteria.
  response = get_stats(criteria_request, fidelity)

  return jsonify(response)

@application.route('/json/update_map', methods=['POST'])
def update_map():
  geo_request = request.get_json()
  
  # Get the fidelity to display data at.
  min_x = float(geo_request['min_long'])
  max_x = float(geo_request['max_long'])
  zoom_level = int(geo_request['zoom'])
  fidelity = get_fidelity(min_x, max_x, zoom_level)
  fidelity_change = fidelity != int(geo_request['fidelity'])
  
  # Get all the polygons inside the bounds that aren't already on the map.
  polygons, geo_codes = get_geometry(geo_request, fidelity, fidelity_change)
  
  # Get stats for each polygon.
  stats = get_stats(geo_request['criteria'], fidelity, geo_codes)
  
  # Build the response by adding stats data to each polygon.
  response = {
    'polygons' : [],
    'fidelity' : fidelity
  }
  for polygon in polygons:
    polygon['stats'] = stats[polygon['geo_code']]
    response['polygons'].append(polygon)

  return jsonify(response)

if __name__ == '__main__':
    application.run()
