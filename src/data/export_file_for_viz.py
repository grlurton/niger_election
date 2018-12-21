import pandas as pd

bureaux_loc = pd.read_csv('/Users/grlurton/Data/data_niger_election_data/processed/geolocalized_bureaux.csv' , encoding = "ISO-8859-1")

bureaux_loc.population_renacom = pd.to_numeric(bureaux_loc.population_renacom)
bureaux_loc.population_renaloc = pd.to_numeric(bureaux_loc.population_renaloc)


def collapse_data(data) :
    n_bureau = len(data)
    n_population_2001 = data['population_renacom'].unique()
    n_population_2012 = data['population_renaloc'].unique()[0]
    n_voters = data['N_voters'].sum()
    locality = data['localite_renacom'].unique()
    longitude = data['longitude_renacom'].unique()
    latitude = data['latitude_renacom'].unique()
    ID = data['localite_ID_renacom'].unique()
    loc_type = data['localite_type_renacom'].unique()
    return pd.DataFrame({'n_bureau':n_bureau ,
            'n_population_2001' : n_population_2001 ,
            'n_population_2012' : n_population_2012 ,
            'n_voters' : n_voters ,
            'locality' : locality ,
            'longitude' : longitude ,
            'latitude' : latitude ,
            'loc_type' : loc_type})

out = bureaux_loc.groupby('localite_ID_renacom').apply(collapse_data).reset_index()
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
if __name__ == '__main__' :
    collection.insert_many(out.to_dict('records'))


for obj in collection.find():
    print (obj)

out.to_csv('../../reports/dashboard/input/data_for_viz.csv' , index = False)
