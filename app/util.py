from constants import PUMA, STATE, COUNTY
from models import (
  PumaPolygon, PumaPerson, CountyPolygon, CountyPerson, StatePolygon,
  StatePerson)

def get_fidelity(min_x, max_x, zoom_level):
  """Decides at what fidelity to display the data based on the current map view.
  
  Args:
    min_x: The westmost longitude of the data asked for.
    max_x: The eastmost longitude of the data asked for.
    zoom_level: The current zoom level of the map.

  Returns:
    The fidelity (puma, county, state) to display data at.
  """
  width = max_x - min_x
  if width > 20 or zoom_level < 8:
    return STATE
  elif width > 2.5 or zoom_level < 11:
    return COUNTY
  else:
    return PUMA


def get_geometry_model(fidelity):
  """Returns the correct model to use based on the fidelity.

  Args:
    fidelity: The level of detail to display map data at.

  Returns:
    The correct version of XPolygon.
  """
  if fidelity == PUMA:
    return PumaPolygon
  elif fidelity == COUNTY:
    return CountyPolygon
  else:
    return StatePolygon


def get_person_model(fidelity):
  """Returns the correct models to use based on the fidelity.

  Args:
    fidelity: The level of detail to display map data at.

  Returns:
    The correct XPerson model to use.
  """
  if fidelity == PUMA:
    return PumaPerson
  elif fidelity == COUNTY:
    return CountyPerson
  else:
    return StatePerson


def get_polygon_name(polygon):
  """Returns the name for a given polygon.
  
  Since not all plygons store their name in the same field, we have to figure
  out what type of polygon it is first, then reference the right field.

  Args:
    polygon: The polygon object to get the name from.

  Returns:
    The name for that polygon object.
  """
  if isinstance(polygon, StatePolygon):
    name = polygon.name
  elif isinstance(polygon, CountyPolygon):
    if polygon.geo_code < 10000000:
      name = polygon.name[:-5]
    else:
      name = polygon.name + ' County'
  elif isinstance(polygon, PumaPolygon):
    name = polygon.puma_name[:-5]
  return name


# Turn the points list into something parsable by Javascript,
# and reorder lat and long.
def convert_and_round_points_list(points_list):
  simplified_points = []
  for point in points_list:
    lng = point[0]
    lat = point[1]
    simplified_points.append([round(lat, 5), round(lng, 5)])
  return simplified_points


# Get the boundary values for this set of points.
def get_boundary_points(points_list):
  min_lat, min_lng = points_list[0]
  max_lat, max_lng = points_list[0]
  for lat, lng in points_list:
    if lng < min_lng:
      min_lng = lng
    if lng > max_lng:
      max_lng = lng
    if lat < min_lat:
      min_lat = lat
    if lat > max_lat:
      max_lat = lat
  return min_lng, min_lat, max_lng, max_lat
