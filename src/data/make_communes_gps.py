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
communes_listing = communes_listing[~(communes_listing.NOM_REGION == 'DIASPORA')]

## Enlever accents dans json
out = {}
for i in range(len(communes_listing)) :
    commune = communes_listing.NOM_COMMUNE[i]
    region = communes_listing.NOM_REGION[i]
    commune_id = communes_listing.ID_COMMUNE[i]
    gps = carto_commune[(carto_commune.nom == commune) & (carto_commune.region == region) ]
    if len(gps) == 1 :
        entry = {'name' : commune ,
                'region' : region ,
                'coordinates' : gps['coordinates'][0]}
        out[str(commune_id)] = entry
    if len(gps) == 0 :
        if commune in list(correction_dictionnary[region].keys()) :
            corrected_name = correction_dictionnary[region][commune]
            gps = carto_commune[(carto_commune.nom == corrected_name) & (carto_commune.region == region) ]
            entry = {'name' : commune ,
                    'region' : region ,
                    'coordinates' : gps['coordinates'][0]}
            out[str(commune_id)] = entry

with open('data/processed/communes_gps.json', 'w') as outfile:
    json.dump(out, outfile)
