// ({{bbox}}) is (south,west,north,east)
// https://wiki.openstreetmap.org/wiki/Overpass_API#The_map_query
// https://wiki.openstreetmap.org/wiki/Bounding_box

// (around:{{radius}},{{center}})
// https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#Relative_to_other_elements_(around)
// {{radius}} in meters
// {{center}} is lat,lng

// {{newer="2024-01-01T00:00:00Z"}}
// https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#newer
// https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#By_date_of_change_(changed)
// ({{bbox}})(newer:{{newer}})
// {search}(newer:{{newer}})
// updated since this datetime

// (area.searchArea)
// {{geocodeArea:Spain}}->.searchArea;

// {{timeout}} in seconds
// https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#timeout:
// {bbox} is [bbox:{{bbox}}] implicit global bounding box
// https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#Global_bounding_box_(bbox)
{bbox}[out:json][timeout:{timeout}];
// area(id:3601311341)->.searchArea;
{area_id}(
  // https://wiki.openstreetmap.org/wiki/Tag:amenity%3Ddrinking_water
  nwr["amenity"="drinking_water"]{search};
  
  // https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dwatering_place
  nwr["amenity"="watering_place"]{search};
  
  // https://wiki.openstreetmap.org/wiki/Tag:natural%3Dspring
  nwr["natural"="spring"]{search};

  // https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dwater_tap
  nwr["man_made"="water_tap"]{search};

  // https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dwater_point
  nwr["amenity"="water_point"]{search};
  
  // https://wiki.openstreetmap.org/wiki/Tag:waterway%3Dwater_point
  nwr["waterway"="water_point"]{search};
);
out meta center qt;
// https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#out
