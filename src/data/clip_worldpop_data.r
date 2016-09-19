require(raster)
require(maptools)
library(rgdal)
library(plyr)
library(splines)
library(shapefiles)

gpclibPermit()

# INITIAL CROP of raw pfpr to country.
setwd('c://users/grlurton/documents/niger_election_data/')

popData <- readGDAL("data/external/WorldPop/NER-POP/NER14adjv1.tif")

communes_shp <- readShapePoly("data/external/commune_shp/nigcom.shp")

communes@proj4string <- popData@proj4string
popDataRaster <- raster(popData)


get_population_commune <- function(raster=popDataRaster , communes =communes_shp , gps_ID_num){
  print('starting')
  gps_ID = unique(communes$GPS_ID)[gps_ID_num]
  print(as.character(communes$GPS_NAME[communes$GPS_ID == gps_ID]))
  commune_polygon <- communes[communes$GPS_ID == gps_ID , ]
  commune_raster <- crop(raster , commune_polygon)
  
  ## Caching values outside of polygon
  NA_mask <- rasterize(commune_polygon , setValues(commune_raster, NA))
  commune_raster_masked <- mask(x = commune_raster , mask = NA_mask)
  
  ## Getting population in commune
  pop_commune <- extract(commune_raster_masked  , commune_polygon , fun=sum , na.rm=TRUE)
  
  #  ## checking size of outputs
  #  if (length(pop_commune) > 1){
  #    print(gps_ID)
  #    print(pop_commune)
  #  }
  
  ## output
  out = c(pop_commune , gps_ID)
  out  
}

library(snowfall)
cl <- snow::makeCluster(ifelse(Sys.info()['sysname']=='Windows',4,50))
snow::clusterExport(cl,list('communes_shp','popDataRaster','get_population_commune' , 'crop' , 'rasterize' , 
                            'setValues' , 'mask' , 'extract'))



test <- parLapply(cl=cl , x=1:length(unique(zones$GPS_ID)) , fun=function(x) get_population_commune(gps_ID_num=x) )
stopCluster(cl)
len <- unlist(lapply(test, length)) == 2
out <-  test[len]

out <- matrix(unlist(out) , ncol = 2 , byrow = TRUE)

out
write.csv(out , file = "data/processed/worldpop_communes.csv")
