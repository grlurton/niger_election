import pandas as pd

bureaux_loc = pd.read_csv('../../data/processed/geolocalized_bureaux.csv')

to_drop = ['milieu' , 'menages' , 'geoloc' , 'menages_agricoles' ,
            'Unnamed: 0' , "bureau_to_match" , "elec_name" , 'renaloc_name' ,
            'level' , 'GPS_NAME' , "locality_to_match"]

for var in to_drop :
    del bureaux_loc[var]


def collapse_data(data) :
    n_bureau = len(data)
    n_population = data['population'].unique()
    n_voters = data['N_voters'].sum()
    locality = data['locality'].unique()
    longitude = data['longitude'].unique()
    latitude = data['latitude'].unique()
    ID = data['renaloc_ID'].unique()
    return pd.DataFrame({'n_bureau':n_bureau ,
            'n_population' : n_population ,
            'n_voters' : n_voters ,
            'locality' : locality ,
            'longitude' : longitude ,
            'latitude' : latitude})

out = bureaux_loc.groupby('renaloc_ID').apply(collapse_data).reset_index()
del out['level_1']

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

out.to_csv('../../reports/dashboard/input/data_for_viz.csv' , index = False)
