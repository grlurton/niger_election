import pandas as pd
import warnings
import os as os

renaloc = pd.read_csv('../../data/processed/renaloc_geolocalized.csv' , encoding = "ISO-8859-1" )
voting_list = pd.read_csv('../../data/processed/voters_list.csv' ,  encoding = "ISO-8859-1" )

voting_list = voting_list[voting_list.commune_ID < 90000]

voting_list.head()

def get_bureaux_size(data):
    name = data.bureau.iloc[0]
    pop = len(data)
    commune_ID = data.commune_ID.iloc[0]
    bureau_ID = data.bureau_ID.iloc[0]
    out = pd.DataFrame([{'commune_ID':commune_ID , 'bureau':name , 'N_voters':pop}])
    return out

voting_centers = voting_list.groupby('bureau_ID').apply(get_bureaux_size)
voting_centers = voting_centers.reset_index()
voting_centers = voting_centers[['bureau_ID' , 'commune_ID' , 'bureau' , 'N_voters']]

renaloc['renaloc_ID'] = range(len(renaloc))

voting_centers.bureau = voting_centers.bureau.str.strip().str.lower()
renaloc.locality = renaloc.locality.str.strip().str.lower()

voting_centers.bureau = voting_centers.bureau.str.replace('ecole primaire' , '')
voting_centers.bureau = voting_centers.bureau.str.replace('ecole' , '')

voting_centers.bureau = voting_centers.bureau.str.strip().str.lower()
renaloc.locality = renaloc.locality.str.strip().str.lower()


exact_match = pd.merge(renaloc , voting_centers ,
                        left_on = ['commune_ID' , 'locality'] ,
                        right_on = ['commune_ID' , 'bureau'])

duplicate_bureaux  = list(exact_match.bureau_ID.value_counts()[(exact_match.bureau_ID.value_counts() > 1)].index)
geolocalized_bureaux = exact_match[~(exact_match.commune_ID.isin(duplicate_bureaux))]

geolocalized_bureaux.columns


## Mapping sur NOM
## Show

## W in renaloc can be OU in voting_centers


geolocalized_bureaux.to_csv('../../data/processed/geolocalized_bureaux.csv' , index = False)


## Utilisation de covariates pour predire  ou son nom manquants
