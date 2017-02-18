import datetime

from geometry import get_geometry
from models import app
from stats import get_stats
from util import get_fidelity
from flask import jsonify, render_template, request


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/json/update_criteria', methods=['POST'])
def update_criteria():
  start = datetime.datetime.now()
  
  criteria_request = request.get_json()
  fidelity = int(criteria_request['fidelity'])
  
  # Get the stats for each geo_code in the request based on the criteria.
  response = get_stats(criteria_request, fidelity)

  duration = datetime.datetime.now() - start
  print('update_criteria took ' + str(duration))
  return jsonify(response)

@app.route('/json/update_map', methods=['POST'])
def update_map():
  start = datetime.datetime.now()
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

  duration = datetime.datetime.now() - start
  print('update_map took ' + str(duration))
  return jsonify(response)

if __name__ == '__main__':
    app.run()
