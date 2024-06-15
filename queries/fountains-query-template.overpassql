// ({{bbox}}) is (south,west,north,east)
// https://wiki.openstreetmap.org/wiki/Overpass_API#The_map_query
// https://wiki.openstreetmap.org/wiki/Bounding_box

// (around:{{radius}},{{center}})
// https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#Relative_to_other_elements_(around)
// {{radius}} in meters
// {{center}} is lat,lng

// (area.searchArea)
// {{geocodeArea:Spain}}->.searchArea;

// {{timeout}} in seconds
[out:json][timeout:{timeout}];
// area(id:3601311341)->.searchArea;
{area_id}(
  // https://wiki.openstreetmap.org/wiki/Tag:amenity%3Ddrinking_water
  nwr["amenity"="drinking_water"][!"access"]{bbox};
  nwr["amenity"="drinking_water"]["access"="yes"]{bbox};
  
  // https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dwater_tap
  nwr["man_made"="water_tap"][!"access"]{bbox};
  nwr["man_made"="water_tap"]["access"="yes"]{bbox};
  
  // https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dwatering_place
  nwr["amenity"="watering_place"][!"access"]{bbox};
  nwr["amenity"="watering_place"]["access"="yes"]{bbox};
  
  // https://wiki.openstreetmap.org/wiki/Tag:natural%3Dspring
  nwr["natural"="spring"][!"access"]{bbox};
  nwr["natural"="spring"]["access"="yes"]{bbox};
);
out meta center qt;
// https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#out
