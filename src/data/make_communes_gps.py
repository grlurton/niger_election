import json
import pandas as pd
import cartopy


## Loading shapefile and getting records list
## Nota : dbf for this shapefile was edited to be read without problem + have extra GPS_ID column
carto_commune = cartopy.io.shapereader.Reader('../../data/external/commune_shp/nigcom.shp')
records = list(carto_commune.records())

## Loading commune listing to be completed with GPS ids
communes_listing = pd.read_csv('../../data/processed/org_units_listing.csv' , encoding = "ISO-8859-1")
communes_listing = communes_listing[~(communes_listing.region == 'DIASPORA')]
communes_listing['GPS_NAME'] = communes_listing['GPS_ID'] = ''

## Loading commune names correspondence between GPS source and voters source
with open('../../data/dictionnaries/gps_communes_recodes.json') as json_data:
    correction_dictionnary = json.load(json_data)
    json_data.close()

## Adding gps ids into the communes listing
for i in range(len(list(carto_commune.records()))) :
    record = records[i].attributes
    commune = record['GPS_NAME']
    region = record['REGION']
    commune_id = record['GPS_ID']
    com = communes_listing[(communes_listing.region == region) & (communes_listing.commune == commune)]
    if len(com) >= 1 :
        communes_listing.loc[(communes_listing.region == region) & (communes_listing.commune == commune) , 'GPS_NAME'] = commune
        communes_listing.loc[(communes_listing.region == region) & (communes_listing.commune == commune) , 'GPS_ID'] = commune_id
    if len(com) == 0 :
        commune_correc = correction_dictionnary[region][commune]
        communes_listing.loc[(communes_listing.region == region) & (communes_listing.commune == commune_correc) , 'gps_name'] = commune
        communes_listing.loc[(communes_listing.region == region) & (communes_listing.commune == commune_correc) , 'gps_ID'] = commune_id

communes_listing.to_csv('../../data/processed/org_units_listing.csv' , index = False )

###############################
## Add gps_ids to voters' data
data_electeurs = pd.read_csv('../../data/processed/voters_list.csv'  , encoding = "ISO-8859-1")
gps_ids = communes_listing.loc[:, ['commune_ID' , 'GPS_NAME' , 'GPS_ID']]
data_electeurs = pd.merge(data_electeurs , gps_ids , on = 'commune_ID' , how = 'left')
data_electeurs.to_csv('../../data/processed/voters_list.csv' , index = False )
