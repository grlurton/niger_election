# coding: utf-8

## Loading Relevant libraries
import pandas as pd
import os as os
import numpy as np
from io import StringIO
import warnings

## Setting working directory
os.chdir('c://users/grlurton/documents/niger_election_data')

## Mapping to data directory
data_dir = os.listdir('data/raw/tabula-RENALOC_Niger_733/')

## Function to load csv files from tabula, and properly format them for aggregation
def get_data(adress) :
    url = 'data/raw/tabula-RENALOC_Niger_733/' + adress
    try :
        liste_depts = pd.read_csv( url , encoding = "ISO-8859-1" )
        ## Table with too few columns are ignored
        if len(liste_depts.columns) < 7:
            out = float('nan')
        if len(liste_depts.columns) >= 8 :
            out = liste_depts.reset_index()
            out = out.drop(0)
            if len(out.columns) >= 9 :
                out = out.iloc[: , [0,1,3,4,5,6,7]]
            out.columns = ['locality' , 'population' , 'hommes', 'femmes' , 'menages' , 'menages_agricoles' , 'geoloc']
            ## Excluding tables that pass the column count test but are improper
            if out.loc[1 , 'locality'].__class__.__name__ in ['int64' , 'float'] :
                out = float('nan')
            return out

    except (ValueError , IndexError) :
        out = float('nan')


## Ordering the tables in their original order, as we will be imputing geographical zones from line position in tables
order = []
for n in range(len(data_dir)) :
    u = data_dir[n].split('-')[2].split('.')[0]
    order = order + [int(u)]
order = sorted(order)

## Importing all relevant Tabula csv files in one data frame
renaloc = []
for i in order :
    addresse = 'tabula-RENALOC_Niger_733-' + str(i) + '.csv'
    dat = get_data(addresse)
    if (dat.__class__.__name__ == 'DataFrame') :
        print(addresse)
        if (len(renaloc) == 0) :
            renaloc = dat
        if (len(renaloc) > 0) :
            renaloc = renaloc.append(dat , ignore_index = True)


## Transforming document hierarchical structure into covariables for Geographical zones
renaloc['level']  = renaloc['region'] = renaloc['departement'] = renaloc['commune'] = renaloc['milieu'] =         region = departement = commune = nom_sup = level = ''
for i in range(1,len(renaloc)) :

    u = renaloc.iloc[i]
    name = u.locality
    try :
        splitted = name.split(':')
        if (len(splitted) >= 2) :
            splitted[0] = splitted[0].replace(' ' , '')
            if (splitted[0] == 'REGIONDE') :
                renaloc.loc[i,'level']= level = 'Region'
                region = splitted[1]
                renaloc.loc[i,'region'] = region
            if (splitted[0] == 'DEPARTEMENTDE') :
                renaloc.loc[i,'level']= level = 'Departement'
                departement = splitted[1]

                renaloc.loc[i,'region'] = region
                renaloc.loc[i,'departement'] = departement
            if (splitted[0] == 'COMMUNEDE') :
                renaloc.loc[i,'level']= level = 'Commune'
                commune = splitted[1]

                renaloc.loc[i,'region'] = region
                renaloc.loc[i,'departement'] = departement
                renaloc.loc[i,'commune'] = commune
            if (splitted[1] == ' Urbain') :
                renaloc.loc[i ,'milieu'] = 'Urbain'
            if (splitted[1] == ' Rural') :
                renaloc.loc[i, 'milieu'] = 'Rural'
            if (level == 'Region'):
                renaloc.loc[i , 'region'] = region

                renaloc.loc[i , 'level'] = level
            if (level == 'Departement') :
                renaloc.loc[i , 'region'] = region
                renaloc.loc[i , 'departement'] = departement

                renaloc.loc[i , 'level'] = level
            if (level == 'Commune') :
                renaloc.loc[i , 'region'] = region
                renaloc.loc[i , 'departement'] = departement
                renaloc.loc[i , 'commune'] = commune

                renaloc.loc[i , 'level'] = level
        else :
            renaloc.loc[i , 'level'] = 'Localite'
            renaloc.loc[i , 'region'] = region
            renaloc.loc[i , 'departement'] = departement
            renaloc.loc[i , 'commune'] = commune
    except (RuntimeError, TypeError, NameError , AttributeError):
        pass



## Function to convert GPS coordinates into Lat / long
## Note : this is ad hoc for GPS coordinates in Niger (ie all GPS coordinates are North East)
def conversion(old):
    new = old.replace(u'°',' ').replace('\'',' ').replace('"',' ')
    new = new.split()
    #new_dir = new.pop()
    new.extend([0,0,0])
    return (int(new[0])+int(new[1])/60.0+int(new[2])/3600.0)



## Function to parse GPS coordinates as they appear in the Tabula extracted csv
def extract_gps(pdf_string):
    long = pdf_string.split(';')[0]

    coord1 = long.split(':')[1].split("Â°")[0]
    coord2 = long.split('Â')[1].split(',')[0]
    coord3 = long.split(',')[1].split(';')[0]

    long = coord1 + coord2 + coord3

    long = long.replace('\\' , '').replace('"','').replace(' ',"")

    lat = pdf_string.split(';')[1]
    coord4 = lat.split("Â°")[0]
    coord4 = coord4.replace("l" , "").replace(':','')
    coord5 = lat.split('Â')[1].split(",")[0]
    coord6 = lat.split(',')[1].split(")")[0]

    lat =  coord4 + coord5 + coord6

    return [long , lat]

# Function to force float all variables supposed to be numeric
def float_all(data):
    if (data.__class__.__name__ != 'float') :
        try :
            data = data.split('\r')[0]
            data = float(data)
        except (ValueError) :
            data = float('nan')

    return data

## Taking out some special characters
renaloc['departement'] = renaloc['departement'].str.replace('\r' , '')
renaloc['locality'] = renaloc['locality'].str.replace('\r' , '')

## Now going through all loaded data and parsing coordinates and putting all variables into numeric
renaloc['longitude'] = renaloc['latitude'] = ''
num_variables = ['hommes' , 'femmes' , 'menages' , 'menages_agricoles' , 'population']

for i in range(len(renaloc)):

    for var in range(len(num_variables)):
        variable = num_variables[var]
        renaloc.loc[i , variable] = float_all(renaloc.loc[i , variable])


    gps = renaloc.loc[i , 'geoloc']
    if pd.isnull(gps) == False :
        try :
            gps_list = extract_gps(gps)
            if (conversion(gps_list[0]) > 0) & (conversion(gps_list[1]) > 10) :
                renaloc.loc[i , 'longitude'] = conversion(gps_list[0])
                renaloc.loc[i , 'latitude'] = conversion(gps_list[1])
        except (IndexError) :
            print('Index Error at ' + str(i))


## Keeping only data with geolocation
geolocalized_data = renaloc[~(renaloc.longitude == '')]


geolocalized_data.to_csv('data/processed/renaloc_geolocalized.csv')
