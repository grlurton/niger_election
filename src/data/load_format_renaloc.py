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
            if len(out.columns) < 10 :
                out = out.iloc[: , [1,2,3,4,5,6,7,8]]
            if len(out.columns) >= 10 :
                out = out.iloc[: , [0,1,3,4,5,6,7,8]]
            out.columns = ['locality' , 'population' , 'hommes', 'femmes' , 'menages' , 'menages_agricoles' , 'geoloc','settlement_type']
            #print(out.head())
            ## Excluding tables that pass the column count test but are improper
            if out.loc[1 , 'locality'].__class__.__name__ in ['int64' , 'float'] :
                out = float('nan')
        return out

    except (ValueError , IndexError) :
        print(out.head())
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
        if (len(renaloc) > 0) :
            renaloc = renaloc.append(dat , ignore_index = True)
        if (len(renaloc) == 0) :
            renaloc = dat


## Ad hoc corrections of problematic values
dak_list = renaloc[renaloc.locality == 'DAKORO (DÃ©partement)'].index.tolist()
renaloc.loc[dak_list[0],'locality'] = 'DAKORO : Urbain'
renaloc.loc[dak_list[1],'locality'] = 'DAKORO : Rural'
renaloc.loc[renaloc.locality == 'DEPARTEMENT : TESSAOUA'] = 'DEPARTEMENT DE : TESSAOUA'

sarkin_haoussa = renaloc[renaloc.locality == 'SARKIN HAOUSSA : Rural'].index
renaloc.loc[(sarkin_haoussa[0] - 1),'locality'] = 'COMMUNE DE : SARKIN HAOUSSA'

sarkin_yamma = renaloc[renaloc.locality == 'SARKIN YAMMA : Rural'].index
renaloc.loc[(sarkin_yamma[0] - 1),'locality'] = 'COMMUNE DE : SARKIN YAMMA'

akoubounou = renaloc[renaloc.locality == 'AKOUBOUNOU: Rural'].index
renaloc.loc[(akoubounou[0] - 1),'locality'] = 'COMMUNE DE : AKOUBOUNOU'

## Transforming document hierarchical structure into covariables for Geographical zones
renaloc['level']  = renaloc['region'] = renaloc['departement'] = renaloc['commune'] = renaloc['milieu'] =         region = departement = commune = level = ''
for i in range(1,len(renaloc)) :
    u = renaloc.iloc[i]
    name = u.locality
    try :
        if 'REGION DE' in name :
            print(name)
            level = 'Region'
            renaloc.loc[i,'level'] = level
            region = name.split('REGION DE')[1]
            departement = ''
            commune = ''
            renaloc.loc[i,'region'] = region
        elif 'DEPARTEMENT DE' in name :
            level = 'Departement'
            renaloc.loc[i,'level']=  'level'
            departement = name.split('DEPARTEMENT DE')[1]
            renaloc.loc[i,'region'] = region
            renaloc.loc[i,'departement'] = departement
            commune = ''
        elif 'COMMUNE DE' in name :
            level = 'Commune'
            renaloc.loc[i,'level']= level
            commune = name.split('COMMUNE DE')[1]
            renaloc.loc[i,'region'] = region
            renaloc.loc[i,'departement'] = departement
            renaloc.loc[i,'commune'] = commune
        elif 'VILLE DE' in name :
            if level != 'Ville' :
                level = 'Ville'
                arr = ''
                departement = name.split('VILLE DE')[1]

            renaloc.loc[i,'level'] = level
            renaloc.loc[i,'region'] = region
            renaloc.loc[i,'departement'] = departement
        elif 'ARRONDISSEMENT' in name :
            if level != 'arrondissement' :
                level = 'arrondissement'
                commune = 'ARRONDISSEMENT' + name.split('ARRONDISSEMENT')[1]

            renaloc.loc[i,'region'] = region
            renaloc.loc[i,'departement'] = departement
            renaloc.loc[i , 'commune'] = commune
            renaloc.loc[i , 'level'] = level

        else :
            level = 'Localite'
            renaloc.loc[i , 'level'] = 'Localite'
            renaloc.loc[i , 'region'] = region
            renaloc.loc[i , 'departement'] = departement
            renaloc.loc[i , 'commune'] = commune

        if (' Urbain' in name) or (' Rural' in name) :
            if ' Urbain' in name :
                renaloc.loc[i ,'milieu'] = 'Urbain'
            if ' Rural' in name :
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
                renaloc.loc[i , 'level'] = level
            if (level == 'Ville') :
                renaloc.loc[i , 'region'] = region
                renaloc.loc[i , 'departement'] = departement
                renaloc.loc[i , 'level'] = level



    except (RuntimeError, TypeError, NameError , AttributeError):
        pass


## Taking out some special characters
renaloc['region'] = renaloc['region'].str.replace('\r|\n|:' , '').str.strip()
renaloc['departement'] = renaloc['departement'].str.replace('\r|\n|:' , '').str.strip()
renaloc['commune'] = renaloc['commune'].str.replace('\r|\n|:|Rural|' , '').str.strip()
renaloc['locality'] = renaloc['locality'].str.replace('\r|\n|:' , '').str.strip()

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


renaloc.loc[(renaloc['commune'] == 'KORE') & (renaloc['region'] == 'DOSSO') , 'commune'] = "KORE MAIROUA"
renaloc.loc[(renaloc['commune'] == 'GUIDAN') & (renaloc['region'] == 'MARADI') , 'commune'] = "GUIDAN AMOUMOUNE"
renaloc.loc[(renaloc['commune'] == 'BIRNI') & (renaloc['region'] == 'TAHOUA') , 'commune'] = "BIRNI N'KONNI"
renaloc.loc[(renaloc['commune'] == 'GALMA') & (renaloc['region'] == 'TAHOUA') , 'commune'] = "GALMA KOUDAWATCHE"
renaloc.loc[(renaloc['commune'] == 'KOURFEYE') & (renaloc['region'] == 'TILLABERI') , 'commune'] = "KOURFEYE CENTRE"
renaloc.loc[(renaloc['commune'] == 'OURO') & (renaloc['region'] == 'TILLABERI') , 'commune'] = "OURO GUELADJO"
renaloc.loc[(renaloc['commune'] == 'ARRONDISSEMENT  3') , 'commune'] = "ARRONDISSEMENT 3"
renaloc.loc[(renaloc['commune'].isin(['KAO' , 'TCHINTABARADEN'])) , 'departement'] = "TCHINTABARADEN"
renaloc.loc[((renaloc['departement'] == 'BIRNI') & (renaloc['region'] == 'TAHOUA') ) , 'departement'] = "BIRNI N'KONNI"


## Adding Unique IDs
communes_listing = pd.read_csv('data/processed/org_units_listing.csv')

renaloc_full = pd.merge(renaloc , communes_listing ,
                            on = ['region' , 'commune'] ,
                            how = 'left')

## Outputting the full data
renaloc_full.to_csv('data/processed/renaloc_full.csv' , index = False)
