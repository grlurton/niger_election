library(dhisextractr)
library(RCurl)
library(XML)
library(plyr)
library(maptools)
library(shapefiles)


setwd('~/Documents/niger_election/')

base_url = 'https://dhisniger.ne'
userID = 'grlurton' 
password = 'F5p5!^WF^x'

all <- extract_dhis_content(base_url = base_url, userID = userID, password = password)

data_sets <- extracted_content[[1]]
data_elements <- extracted_content[[2]]
data_categories <- extracted_content[[3]]
org_units <- extracted_content[[4]]
org_units_description <- extracted_content[[5]]
org_units_groups <- extracted_content[[6]]
org_units_data_sets <- extracted_content[[7]]


write.csv(data_sets , 'data_sets.csv')
write.csv(data_elements , 'data_elements.csv')
write.csv(data_categories , 'data_categories.csv')
write.csv(org_units_list , 'org_units.csv')
write.csv(org_units_data_sets , 'org_units_data_sets.csv')
write.csv(org_units_groups, 'org_units_groups.csv')
write.csv(org_units_description, 'org_units_description.csv')



shapefiles <- extract_geolocalisation(org_units_description)

write.shapefile(shapefiles[[1]], 'map_points', arcgis=T)
write.shapefile(shapefiles[[2]], 'map_polygons', arcgis=T)
