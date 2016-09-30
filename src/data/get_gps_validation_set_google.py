from geopy import geocoders
import pandas as pd
import time
from multiprocessing.pool import ThreadPool
import os
from math import radians, cos, sin, asin, sqrt



renaloc_data = pd.read_csv('../../data/processed/renaloc_geolocalized.csv' , encoding = "ISO-8859-1")
g = geocoders.GoogleV3(api_key='AIzaSyCuRsxyHe0MIBQndHtaJ59s1xQ4E-Cedu0')

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
renaloc_data['region'] = renaloc_data['region'].str.lower().replace('tillaberi' , 'tillabéri')


def get_long_lat(coordinates):
    long = coordinates[0][0]
    lat = coordinates[0][1]
    return {'long':long , 'lat':lat}

def get_validation_set(u) :
    names = []
    coordinates = []
    regions = []
    ID = []
    departements = []
    matching_how = []
    renaloc_latitude = []
    renaloc_longitude = []
    print(u)
    locality = renaloc_data.loc[u , 'locality']
    region = renaloc_data.loc[u , 'region']
    while True :
        try :
            response = g.geocode(locality, timeout=10 , exactly_one = False)
        except :
            print('pausing')
            time.sleep(10)
            continue
        break
    if (response is not None) :
        for i in range(len(response)) :
            location = response[i]
            in_Niger = False
            for j in range(len(location.raw['address_components'])):
                long_name = location.raw['address_components'][j]['long_name']
                if "niger" in long_name.lower() :
                    in_Niger = True
        dist = haversine([renaloc_data.loc[i , 'longitude'] , renaloc_data.loc[i , 'latitude']] ,
                    [location.raw['geometry']['location']['lng'] , location.raw['geometry']['location']['lat'] ])

        if in_Niger == True :
            print('in Niger')
            print('dist ' + str(dist) + ' km')
            in_region = False
            for i in range(len(location.raw['address_components'])):
                long_name = location.raw['address_components'][i]['long_name']
                if region in long_name.lower() :
                    in_region = True
            if in_region == True :
                print(locality + '       -       ' + region)
                names = names + [locality]
                coordinates = coordinates + [location.raw['geometry']['location']]
                ID = ID + [renaloc_data.loc[i , 'locality_ID']]
                departements = departements + [renaloc_data.loc[i , 'departement']]
                regions = regions + [region]
                matching_how = matching_how + ["in Region"]
                renaloc_latitude = renaloc_latitude + [renaloc_data.loc[i , 'latitude']]
                renaloc_longitude = renaloc_longitude + [renaloc_data.loc[i , 'longitude']]
            elif dist < 40 :
                print(locality + '       -       ' + str(dist) + ' km')
                names = names + [locality]
                coordinates = coordinates + [location.raw['geometry']['location']]
                ID = ID + [renaloc_data.loc[i , 'locality_ID']]
                departements = departements + [renaloc_data.loc[i , 'departement']]
                regions = regions + [region]
                matching_how = matching_how + ['Based on Distance']
                renaloc_latitude = renaloc_latitude + [renaloc_data.loc[i , 'latitude']]
                renaloc_longitude = renaloc_longitude + [renaloc_data.loc[i , 'longitude']]
    coordinates = pd.DataFrame(coordinates)
    out = pd.DataFrame(coordinates)
    out['ID'] = ID
    out['locality'] = names
    out['departement'] = departements
    out['region'] = regions
    out['matching_how'] = matching_how
    out['renaloc_latitude'] = renaloc_latitude
    out['renaloc_longitude'] = renaloc_longitude
    return out



n_processes = os.cpu_count()
threadPool = ThreadPool(n_processes)
extracted_validation = threadPool.map(get_validation_set , list(range(1,2500)))

validation_total = pd.concat(extracted_validation, axis=0)
validation_total = validation_total.reset_index()
del validation_total['index']



validation_total['departement'] = validation_total['departement'].str.lower().str.title()
for i in range(len(validation_total)):
    dist_i = haversine([validation_total.lng.iloc[i] , validation_total.lat.iloc[i]] , [validation_total.renaloc_longitude.iloc[i] , validation_total.renaloc_latitude.iloc[i]])
    validation_total.loc[i , 'dist_validation'] = dist_i

g.geocode('test', timeout=10 , exactly_one = False)
