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
  nwr["amenity"="drinking_water"][!"access"]{search};
  nwr["amenity"="drinking_water"]["access"="yes"]{search};
  
  // https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dwater_tap
  nwr["man_made"="water_tap"][!"access"]{search};
  nwr["man_made"="water_tap"]["access"="yes"]{search};
  
  // https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dwatering_place
  nwr["amenity"="watering_place"][!"access"]{search};
  nwr["amenity"="watering_place"]["access"="yes"]{search};
  
  // https://wiki.openstreetmap.org/wiki/Tag:natural%3Dspring
  nwr["natural"="spring"][!"access"]{search};
  nwr["natural"="spring"]["access"="yes"]{search};
);
out meta center qt;
// https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#out
