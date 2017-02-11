from models import StatePolygon, CountyPolygon, PumaPolygon
from util import get_geometry_models, get_polygon_name

def get_geometry(geo_request, fidelity, fidelity_change):
  """Gets all the polygons specified by the geo_request.
  
  Args:
    geo_request: A dict that contains the bounds to find polygons within, and a
      list of polygon ids that are already on the map.
    fidelity: The fidelity to display the data, based on the current map view.
    fidelity_change: A bool that states if the currently requested fidelity is
      different from the last requested fidelity.
  
  Returns:
    A list of polygon dicts and a set of all the geo_codes. Each dict contains
    the id, the geo_code and a list of points that make up the polygon.
  """
  # Build and execute the SQL query.
  already_displayed = set()
  if not fidelity_change:
    for polygon_id in geo_request['existing_polygon_ids']:
      already_displayed.add(int(polygon_id))
  min_x = float(geo_request['min_long'])
  min_y = float(geo_request['min_lat'])
  max_x = float(geo_request['max_long'])
  max_y = float(geo_request['max_lat'])
  Polygon, Point = get_geometry_models(fidelity)
  results = Polygon.query.filter(
    Polygon.max_x > min_x,
    Polygon.min_x < max_x,
    Polygon.max_y > min_y,
    Polygon.min_y < max_y).all()
  
  # Synthesize the results.
  polygons = []
  geo_codes = set()
  for result in results:
    if result.id in already_displayed:
      continue
    name = get_polygon_name(result)
    geo_codes.add(result.geo_code)
    points = []
    for point in result.points.order_by(Point.id):
      points.append([point.latitude, point.longitude])
    polygon = {
      'id': result.id, 'geo_code': result.geo_code, 'name': name,
      'points': points}
    polygons.append(polygon)
    
  return polygons, geo_codes
