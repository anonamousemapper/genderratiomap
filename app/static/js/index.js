function update_polygons_in_map(response, map) {
  // Update color and stats of each polygon.
  map.eachLayer(
    function(layer) {
      if ('geo_code' in layer) {
        layer['stats'] = response[layer['geo_code']];
        layer.setStyle({fillColor: get_color(layer['stats'])});
      }
    }
  );
}

function build_criteria_dict() {
  var all_inputs = $(":input");
  var criteria = {};
  for (i = 0; i < all_inputs.length; i++) {
    input = all_inputs[i];
    if (input.type == "text" || (input.type == "checkbox" && input.checked)) {
      if (!(input.name in criteria)) {
        criteria[input.name] = []
      }
      criteria[input.name].push(input.value);            
    }
  }
  return criteria;
}

function on_criteria_change(map) {
  var request = build_criteria_dict();
  
  request['geo_codes'] = [];
  map.eachLayer(
    function(layer) {
      if ('geo_code' in layer) {
        request['geo_codes'].push(layer['geo_code']);
      }
    }
  );
  request['fidelity'] = people_map.fidelity;
  
  // Request new polygons given the bounds of the map and the current
  // polygon ids.
  if (current_xhr != null) {
    current_xhr.abort();
  }
  current_xhr = $.ajax({
    url: '/json/update_criteria',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(request),
    dataType: 'json',
    success: function(response) {
       update_polygons_in_map(response, map);
    }
  });
}

function on_move_end(e) {      
  update_map_polygons(e.target);
}

function display_popup(e) {
  var stats = e.target.stats;
  var ratio = (e.target.stats.ratio).toFixed(2);
  var text = e.target.polygon_name + '<br />';
  if(ratio > 0) {
    text +=
       ratio + ' men per woman<br />' + stats.num_men + ' men, '
       + stats.num_women + ' women';
  } else {
    ratio *= -1;
    text += ratio + ' women per man<br />' + stats.num_women + ' women, '
       + stats.num_men + ' men';
  }
  e.target.bindTooltip(text, {'sticky': true}).openTooltip();
}

function hide_popup(e) {
  e.target.unbindTooltip();
}

function get_color(stats) {
  if (stats.num_men  + stats.num_women < 2500) {
    return '#939393';
  }
  
  // Input ratio is expected to be >= 1.0 if there are more men than women,
  // <= -1.0 if there are more women than men, and 0.0 if the ratios are
  // exactly equal. Subtract out the (-1.0, 1.0) that doesn't exist.
  // A ratio of 2.0 will now be 1.0.
  var ratio = stats.ratio;
  var new_ratio = ratio > 0 ? ratio - 1 : ratio + 1;
  if (ratio == 0) {
    new_ratio = 0.0;
  }
  
  // Apply the square root to the ratio to make the values near 0 have a
  // bigger change.
  // A ratio of 1.0 will now be 2.0.
  new_ratio *= 4;
  var mult = 1;
  if (new_ratio < 0) {
    mult = -1;
  }
  new_ratio = Math.sqrt(Math.abs(new_ratio)) * mult;

  // Want to make the color spectrum for an original ratio of [-2.0, 2.0].
  if (new_ratio > 2.0) {
    new_ratio = 2.0;
  }
  if (new_ratio < -2.0) {
    new_ratio = -2.0;
  }
  
  // Translate [-2.0, 2.0] to [120.0, 0.0].
  new_ratio += 2.0;
  new_ratio *= 30.0;
  new_ratio = 120.0 - new_ratio;
  
  // Convert new_ratio to a hex color representation.
  var color = tinycolor({ h: new_ratio, s: 100, v: 100 }).toHexString();
  return color;
}

function add_new_polygons_to_map(data, map) {
  // If the fidelity changed, remove all the old polygons.
  if (people_map.fidelity != data.fidelity) {
    people_map.fidelity = data.fidelity;
    map.eachLayer(
      function(layer) {
        if ('polygon_id' in layer) {
          layer.remove();
        }
      }
    );
  }
  
  // Build a set of all polygon ids in the map.
  var existing_polygon_ids = new Set();
  map.eachLayer(
    function(layer) {
      if ('polygon_id' in layer) {
        existing_polygon_ids.add(layer['polygon_id']);
      }
    }
  );
  
  // Add in polygons that aren't already in the map.
  for (i = 0; i < data.polygons.length; i++) {
    polygon_dict = data.polygons[i];
    if (existing_polygon_ids.has(polygon_dict.id)) {
      console.log('Tried to add a polygon that already exists in the map.');
      continue;
    }
    var color = get_color(polygon_dict.stats);
    polygon_dict.points = JSON.parse(polygon_dict.points);
    var polygon = L.polygon(
      polygon_dict.points,
      {
        color: '#939393',
        fillColor: color,
        weight: 2,
        fillOpacity: 0.4
      }
    );
    polygon['polygon_id'] = polygon_dict.id;
    polygon['polygon_name'] = polygon_dict.name;
    polygon['stats'] = polygon_dict.stats;
    polygon['geo_code'] = polygon_dict.geo_code;
    polygon.on({mouseover: display_popup, mouseout: hide_popup});
    polygon.addTo(map);
  }
}

function update_map_polygons(map) {
  // Start building our json request object.
  var map_bounds = map.getBounds().pad(0.5);
  var request = {
    min_lat: map_bounds.getSouth(),
    min_long: map_bounds.getWest(),
    max_lat: map_bounds.getNorth(),
    max_long: map_bounds.getEast(),
    existing_polygon_ids: [],
    criteria: build_criteria_dict(),
    zoom: map.getZoom(),
    fidelity: people_map.fidelity
  };
  
  // Remove polygons that are off map (determined by padded bounds) and add
  // all the on-map polygon ids to the request.
  var map_deletion_bounds = map.getBounds().pad(1.0);
  map.eachLayer(
    function(layer) {
      // Only deal with polygons we've added to the map.
      if ('polygon_id' in layer) {
        if (layer.getBounds().intersects(map_deletion_bounds)) {
          request['existing_polygon_ids'].push(layer['polygon_id']);
        } else {
          layer.remove();
        }
      }
    }
  );
  
  // Request new polygons given the bounds of the map and the current
  // polygon ids.
  if (current_xhr != null) {
    current_xhr.abort();
  }
  current_xhr = $.ajax({
    url: '/json/update_map',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(request),
    dataType: 'json',
    success: function(data) {
       add_new_polygons_to_map(data, map);
    }
  });
}

$(function() {
  $("#slider-range").slider({
    range: true,
    min: 0,
    max: 100,
    values: [24, 30],
    slide: function(event, ui) {
      $("#amount").val(ui.values[0] + " - " + ui.values[1]);
    },
    change: function(event, ui) {
      on_criteria_change(people_map);
    }
  });
  
  $("#amount").val($("#slider-range").slider("values", 0) +
    " - " + $("#slider-range").slider("values", 1));

  $("input:checkbox").checkboxradio({
    icon: false
  });
  
  update_map_polygons(people_map);
});
