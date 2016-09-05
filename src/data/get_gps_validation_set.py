import overpass
import pandas as pd
import time
from multiprocessing.pool import ThreadPool
import os
from math import radians, cos, sin, asin, sqrt


api = overpass.API()
renaloc_data = pd.read_csv('../../data/processed/renaloc_geolocalized.csv' , encoding = "ISO-8859-1")


def get_long_lat(coordinates):
    long = coordinates[0][0]
    lat = coordinates[0][1]
    return {'long':long , 'lat':lat}

def haversine(gps1,gps2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1 = gps1[0]
    lat1 = gps1[1]
    lon2 = gps2[0]
    lat2 = gps2[1]
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km

renaloc_data['locality_ID'] = range(len(renaloc_data))
renaloc_data['locality'] = renaloc_data['locality'].str.replace(' Urbain' , '').str.lower().str.title().str.strip()
renaloc_data['NOM_REGION'] = renaloc_data['NOM_REGION'].str.lower().replace('tillaberi' , 'tillabéri').str.title()


def get_validation_set(i) :
    names = []
    coordinates = []
    regions = []
    ID = []
    departements = []
    osm_is_in = []
    renaloc_latitude = []
    renaloc_longitude = []
    print(i)
    locality = renaloc_data.loc[i , 'locality']
    region = renaloc_data.loc[i , 'NOM_REGION']
    while True :
        try :
            response = api.Get('node["name"="' + locality +'"]')
        except :
            time.sleep(60)
            continue
        break
    if len(response['features']) > 0 :
        to_parse = pd.DataFrame(response["features"])["properties"]
        for u in range(len(to_parse)) :
            if 'is_in' in to_parse[u].keys() :
                print(locality + '       ' + to_parse[u]['is_in'] , '       ' + region)
                if region in to_parse[u]['is_in'] :
                    names = names + [locality]
                    coordinates = coordinates + [response['features'][u]['geometry']]
                    ID = ID + [renaloc_data.loc[i , 'locality_ID']]
                    departements = departements + [renaloc_data.loc[i , 'NOM_DEPART']]
                    regions = regions + [region]
                    osm_is_in = osm_is_in + [to_parse[u]['is_in'] ]
                    renaloc_latitude = renaloc_latitude + [renaloc_data.loc[i , 'latitude']]
                    renaloc_longitude = renaloc_longitude + [renaloc_data.loc[i , 'longitude']]
                elif 'Niger' in to_parse[u]['is_in'] :
                    names = names + [locality]
                    coordinates = coordinates + [response['features'][u]['geometry']]
                    ID = ID + [renaloc_data.loc[i , 'locality_ID']]
                    departements = departements + [renaloc_data.loc[i , 'NOM_DEPART']]
                    regions = regions + [region]
                    osm_is_in = osm_is_in + ['Region not ok']
                    renaloc_latitude = renaloc_latitude + [renaloc_data.loc[i , 'latitude']]
                    renaloc_longitude = renaloc_longitude + [renaloc_data.loc[i , 'longitude']]
            elif (haversine([renaloc_data.loc[i , 'longitude'] , renaloc_data.loc[i , 'latitude']] , [response['features'][u]['geometry']['coordinates'][0] , response['features'][u]['geometry']['coordinates'][1] ]) < 40) :
                    names = names + [locality]
                    coordinates = coordinates + [response['features'][u]['geometry']]
                    ID = ID + [renaloc_data.loc[i , 'locality_ID']]
                    departements = departements + [renaloc_data.loc[i , 'NOM_DEPART']]
                    regions = regions + [region]
                    osm_is_in = osm_is_in + ['Based on Distance']
                    renaloc_latitude = renaloc_latitude + [renaloc_data.loc[i , 'latitude']]
                    renaloc_longitude = renaloc_longitude + [renaloc_data.loc[i , 'longitude']]
    coordinates = pd.DataFrame(coordinates)
    coords = []
    for i in range(len(coordinates)):
        c = get_long_lat(coordinates.iloc[i])
        coords = coords + [c]
    out = pd.DataFrame(coords)
    out['ID'] = ID
    out['locality'] = names
    out['departement'] = departements
    out['region'] = regions
    out['osm_is_in'] = osm_is_in
    out['renaloc_latitude'] = renaloc_latitude
    out['renaloc_longitude'] = renaloc_longitude
    return out

n_processes = os.cpu_count()
threadPool = ThreadPool(n_processes)
extracted_validation = threadPool.map(get_validation_set , list(range(len(renaloc_data))))



validation_total = pd.concat(extracted_validation, axis=0)
validation_total = validation_total.reset_index()
del validation_total['index']

validation_total['departement'] = validation_total['departement'].str.lower().str.title()
validation_total['osm_is_in'] = validation_total['osm_is_in'].str.replace('Tânout' , 'Tanout')


for i in range(len(validation_total)):
    dist_i = haversine([validation_total.long.iloc[i] , validation_total.lat.iloc[i]] , [validation_total.renaloc_longitude.iloc[i] , validation_total.renaloc_latitude.iloc[i]])
    validation_total.loc[i , 'dist_validation'] = dist_i


validation_total.to_csv('../../data/external/gps_validation_set.csv' , index = False)
