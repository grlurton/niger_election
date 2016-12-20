import pandas as pd
import warnings
import os as os

renaloc = pd.read_csv('../../data/processed/renaloc_geolocalized.csv' , encoding = "ISO-8859-1" )
renaloc = renaloc[['locality' , 'commune_ID']]
renaloc.columns = ['localite' , 'commune_ID']

renacom = pd.read_csv('../../data/processed/renacom_full.csv' , encoding = 'ISO-8859-1')
renacom = renacom[['LOCALITE' , 'commune_ID']]
renacom.columns = ['localite' , 'commune_ID']

voting_centers = pd.read_csv('../../data/processed/voting_bureaux_size.csv' ,  encoding = "ISO-8859-1" )
voting_centers = voting_centers[['bureau_ID' , 'commune_ID' , 'bureau']]
voting_centers.columns = ['localite_ID' , 'commune_ID' , 'localite']
## Drop bureaux of the diaspora
voting_centers = voting_centers[voting_centers.commune_ID < 90000]

## Make RENALOC ID for each locality
renaloc['localite_ID'] = range(len(renaloc))
renacom['localite_ID'] = range(len(renacom))

renaloc['localite_ID'] = 'RENALOC_' + renaloc['localite_ID'].astype(str)
renacom['localite_ID'] = 'RENACOM_' + renacom['localite_ID'].astype(str)
voting_centers['localite_ID'] = 'bureau_' + voting_centers['localite_ID'].astype(str)


##  standardize variables on which to match
voting_centers['localite'] = voting_centers.localite.str.strip().str.lower()
renaloc['localite'] = renaloc.localite.str.strip().str.lower()
renacom['localite'] = renacom.localite.str.strip().str.lower()

renaloc['source'] = 'RENALOC'
renacom['source'] = 'RENACOM'
voting_centers['source'] = 'voting_lists'

print(len(renaloc))
renaloc = renaloc.append(renacom)
print(len(renaloc))
renaloc = renaloc.append(voting_centers)
print(len(renaloc))

renaloc.to_csv('../../data/processed/names_list.csv')
