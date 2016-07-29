# coding: utf-8

## Loading Relevant libraries
import pandas as pd
import os as os

## Setting working directory
os.chdir('c://users/grlurton/documents/niger_election_data')

## Adding Unique IDs
communes_listing = pd.read_csv('data/raw/Niger_Communes.csv', encoding = "ISO-8859-1")
departements_listing = pd.read_csv('data/raw/Niger_Departements.csv' , encoding = "ISO-8859-1")
regions_listing = pd.read_csv('data/raw/Niger_Regions.csv', encoding = "ISO-8859-1")

store_electeurs = pd.HDFStore('data/raw/full_data.h5')
data_electeurs = store_electeurs['complete_data']
store_electeurs.close()


del communes_listing['N_COMMUNE'] , communes_listing['Unnamed: 0'] , departements_listing['N_DEPART'] , departements_listing['Unnamed: 0'] , regions_listing['Unnamed: 0']  , data_electeurs['N_COMMUNE'] , data_electeurs['N_DEPART']  , data_electeurs['N_BUREAU']


def correct_communes_names(data) :
    data.loc[data['NOM_COMMUNE'].isin(['TIBIRI (DOUTCHI)' , 'TIBIRI (MARADI)']), 'NOM_COMMUNE'] = 'TIBIRI'
    data.loc[data['NOM_COMMUNE'].isin(['GANGARA (AGUIE)' , 'GANGARA (TANOUT)']), 'NOM_COMMUNE'] = 'GANGARA'
    data.loc[data['NOM_COMMUNE'].isin(['MARADI ARRONDISSEMENT 1']), 'NOM_COMMUNE'] = 'ARRONDISSEMENT 1'
    data.loc[data['NOM_COMMUNE'].isin(['MARADI ARRONDISSEMENT 2']), 'NOM_COMMUNE'] = 'ARRONDISSEMENT 2'
    data.loc[data['NOM_COMMUNE'].isin(['MARADI ARRONDISSEMENT 3']), 'NOM_COMMUNE'] = 'ARRONDISSEMENT 3'
    return data


communes_listing = correct_communes_names(communes_listing)
data_electeurs = correct_communes_names(data_electeurs)

full_data = pd.merge(communes_listing , departements_listing , on = 'ID_DEPART' , how = 'inner')
full_data = pd.merge(full_data , regions_listing , on = 'ID_REGION' , how = 'inner')

full_data.to_csv('data/processed/org_units_listing.csv' , index = False)
data_electeurs.to_csv('data/processed/voters_list.csv' , index = False)
