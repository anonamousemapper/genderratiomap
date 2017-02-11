from constants import MALE, FEMALE
from models import db
from util import get_person_model
from collections import defaultdict

def get_stats(criteria, fidelity, geo_codes=None):
  """Gets new stats for each geographic area based the criteria.

  Args:
    criteria: A dict of lists for the various criteria that can be specified.
      The keys are as follows:
        geo_codes: Required unless the top level arg geo_codes is set. A list of
          geographic areas to get stats for.
        age: Optional. A list with one element that is a string of the form
          'x - y' where x is the minimum age and y is the maximum age.
        race: Optional. A list of races to filter down to.
        education: Optional. A list of education levels to filter down to.
        housing: Optional. A list of housing statuses to filter down to.
        children: Optional. A list of children statuses to filter down to.
        marriage_status: Optional. A list of marriage statuses to filter down
          to.
    fidelity: The correct level of detail to pull data for.
    geo_codes: A set of geo_codes to get stats for. Can be None if geo_codes is
      set in criteria.
        
  Returns:
    A dictionary of stats. Keys are geo_codes and values are stats for that
    geo_code.
  """
  # Get the right Person model.
  Person = get_person_model(fidelity)
  
  # Initialize the geo_codes set unless it was passed in.
  if not geo_codes:
      geo_codes = set()

  # Build up the WHERE clause of the SQL query.
  expressions_list = []
  for key, value in criteria.items():
    if key == 'geo_codes':
      for geo_code in value:
        geo_codes.add(int(geo_code))
      expressions_list.append(Person.geo_code.in_(geo_codes))
    elif key == 'age':
      youngest, oldest = value[0].split('-')
      expressions_list.append(Person.age >= int(youngest.strip()))
      expressions_list.append(Person.age <= int(oldest.strip()))
    elif key == 'race':
      races = set()
      for race in value:
        races.add(int(race))
      expressions_list.append(Person.race.in_(races))
    elif key == 'education':
      educations = set()
      for education in value:
        educations.add(int(education))
      expressions_list.append(Person.education.in_(educations))
    elif key == 'housing':
      housings = set()
      for housing in value:
        housings.add(int(housing))
      expressions_list.append(Person.housing_status.in_(housings))
    elif key == 'children':
      childrens = set()
      for children in value:
        childrens.add(int(children))
      expressions_list.append(Person.children_status.in_(childrens))
    elif key == 'marriage_status':
      marriage_statuses = set()
      for marriage_status in value:
        marriage_statuses.add(int(marriage_status))
      expressions_list.append(Person.marriage_status.in_(marriage_statuses))
  
  expressions = tuple(expressions_list)
  
  # Execute the SQL query.
  results = db.session.query(
    db.cast(Person.geo_code, db.Integer),
    db.cast(Person.sex, db.Integer),
    db.cast(db.func.sum(Person.person_weight), db.Integer)
  ).filter(
    *expressions
  ).group_by(
    Person.geo_code,
    Person.sex
  ).all()
  
  # Return the synthesized stats.
  return build_stats(geo_codes, results)


def build_stats(geo_codes, sql_results):
  """Takes a SQL result and generates a dictionary of stats.

  Args:
    geo_codes: An iterable object containing all the desired geo_codes.
    sql_results: An iterable object of SQL results. Each iteration is a tuple of
      (geo_code, sex, num_people) where the combination of (geo_code, sex) is
      guaranteed to be unique.

  Returns:
    A dictionary of stats. Keys are geo_codes and values are stats for that
    geo_code.
  """
  # Synthesize the stats from the SQL query.
  geo_code_stats = defaultdict(lambda: defaultdict(int))
  for geo_code, sex, num_people in sql_results:
    geo_code_stats[geo_code][sex] = num_people
  
  stats = {}
  for geo_code in geo_codes:
    num_men = geo_code_stats[geo_code][MALE]
    num_women = geo_code_stats[geo_code][FEMALE]
    # Ratio goes from 5 to -5 where 5 means five times as many men as women, 0
    # means an equal ratio and -5 means five times as many women as men.
    if num_women == 0 and num_men == 0:
      ratio = 0.0
    elif num_women == 0:
      ratio = 5.0
    elif num_men == 0:
      ratio = -5.0
    elif num_men > num_women:
      ratio = min(float(num_men) / num_women, 5.0)
    else:
      ratio = -1.0 * min(float(num_women) / num_men, 5.0)
    stats[geo_code] = {
      'num_men': num_men, 'num_women': num_women, 'ratio': ratio}

  return stats
