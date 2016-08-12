import json
import os as os
import pandas as pd

## Setting working directory
os.chdir('c://users/grlurton/documents/niger_election_data')

with open('data/external/communes_gps.json') as json_data:
    carto_commune = json.load(json_data)
    json_data.close()
carto_commune = pd.DataFrame(carto_commune).T

with open('data/dictionnaries/gps_communes_recodes.json') as json_data:
    correction_dictionnary = json.load(json_data)
    json_data.close()

communes_listing = pd.read_csv('data/processed/org_units_listing.csv' , encoding = "ISO-8859-1")
communes_listing = communes_listing[~(communes_listing.region == 'DIASPORA')]

## Get accents out
carto_commune.nom = carto_commune.nom.str.replace('É','E')

## Extra codes for grouped communes
extracode = {'MARADI':{'name':'MARADI I,II,III' , 'code':'MARADI_VILLE'} ,
            'TAHOUA':{'name':'TAHOUA I,II' , 'code':'TAHOUA_VILLE'} ,
            'ZINDER':{'name':'ZINDER I,II,III,IV,V' , 'code':'ZINDER_VILLE'}}

extracode = pd.DataFrame(extracode).T

communes_listing['gps_name'] = communes_listing['gps_ID'] = ''

out = {}
mem = []
for i in range(len(communes_listing)) :
    commune = communes_listing.commune[i]
    region = communes_listing.region[i]
    commune_id = communes_listing.commune_ID[i]
    gps = carto_commune[(carto_commune.nom == commune) & (carto_commune.region == region) ]
    if len(gps) >= 1 :
        for u in list(gps.index)  :
            entry = {'name' : commune ,
                    'region' : region ,
                    'coordinates' : gps.loc[u , 'coordinates']}
            out[str(commune_id)] = entry
    if len(gps) == 0 :
        if commune in list(correction_dictionnary[region].keys()) :
            corrected_name = correction_dictionnary[region][commune]
            if corrected_name in list(extracode.name) :
                commune_id = list(extracode.code[extracode.name == corrected_name])[0]
                commune = corrected_name
            if (corrected_name in mem) == False :
                gps = carto_commune[(carto_commune.nom == corrected_name) & (carto_commune.region == region) ]
                entry = {'name' : commune ,
                        'region' : region ,
                        'coordinates' : gps['coordinates'][0]}
                out[str(commune_id)] = entry
            mem = mem + [corrected_name]
    communes_listing.loc[i , 'gps_name'] = commune
    communes_listing.loc[i , 'gps_ID'] = commune_id

with open('data/processed/communes_gps.json', 'w') as outfile:
    json.dump(out, outfile)

communes_listing.to_csv('data/processed/org_units_listing.csv' , index = False )

###############################
## Add gps_ids to voters' data

## Loading data from electoral lists
data_electeurs = pd.read_csv('data/processed/voters_list.csv'  , encoding = "ISO-8859-1")
gps_ids = communes_listing.loc[:, ['ID_COMMUNE' , 'gps_name' , 'gps_ID']]
data_electeurs = pd.merge(data_electeurs , gps_ids , on = 'ID_COMMUNE' , how = 'left')
data_electeurs.to_csv('data/processed/voters_list.csv' , index = False )
