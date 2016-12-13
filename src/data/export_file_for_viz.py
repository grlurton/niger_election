import pandas as pd

bureaux_loc = pd.read_csv('../../data/processed/geolocalized_bureaux.csv')

bureaux_loc.columns

to_drop = ['CodeRegion' , 'CodeDepartement' , 'CodeCommune' ,
            'MILIEU' , 'TYPECOM' , 'REGION' , 'DEPARTEMENT' , 'COMMUNE' ,
            'MASCULIN' , 'FEMININ' , 'MENAGE' , 'CODEIRHVIL' , 'CODEAP3AVI' , 'CodeCanton' ,
            'Unnamed: 0' , "bureau_to_match" , "elec_name" , 'renaloc_name' ,
            "locality_to_match"]



for var in to_drop :
    del bureaux_loc[var]

bureaux_loc.TOTAL = pd.to_numeric(bureaux_loc.TOTAL)

def collapse_data(data) :
    n_bureau = len(data)
    n_population = data['TOTAL'].unique()
    n_voters = data['N_voters'].sum()
    locality = data['LOCALITE'].unique()
    longitude = data['LONGITUDE'].unique()
    latitude = data['LATITUDE'].unique()
    ID = data['CodeLocalite'].unique()
    loc_type = data['TYPELOCALITE'].unique()
    return pd.DataFrame({'n_bureau':n_bureau ,
            'n_population' : n_population ,
            'n_voters' : n_voters ,
            'locality' : locality ,
            'longitude' : longitude ,
            'latitude' : latitude ,
            'loc_type' : loc_type})

out = bureaux_loc.groupby('CodeLocalite').apply(collapse_data).reset_index()
del out['level_1']

out.head()


## Export the data in MongoDB and csv
from pymongo import MongoClient
from ipykernel import kernelapp as app
import json

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'voter'
COLLECTION_NAME = 'project'

connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
collection = connection[DBS_NAME][COLLECTION_NAME]

## Empty MongoDB from current data
result = collection.delete_many({})

records = json.loads(out.T.to_json()).values()

if __name__ == '__main__' :
    collection.insert(records)

out.head()

out.to_csv('../../reports/dashboard/input/data_for_viz.csv' , index = False)
