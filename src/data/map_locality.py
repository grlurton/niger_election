import pandas as pd
import warnings
import os as os

renaloc = pd.read_csv('../../data/processed/renaloc_geolocalized.csv' , encoding = "ISO-8859-1" )
voting_list = pd.read_csv('../../data/processed/voters_list.csv' ,  encoding = "ISO-8859-1" )
dico_data = pd.read_csv('../../data/dictionnaries/locality_name_map.csv')


## Drop bureaux of the diaspora
voting_list = voting_list[voting_list.commune_ID < 90000]

## making bureaux size => deserves to be in another script
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

## Make RENALOC ID for each locality
renaloc['renaloc_ID'] = range(len(renaloc))

##  Make variables on which to match
voting_centers['bureau_to_match'] = voting_centers.bureau.str.strip().str.lower()
renaloc['locality_to_match'] = renaloc.locality.str.strip().str.lower()

voting_centers.bureau_to_match = voting_centers.bureau_to_match.str.replace('ecole primaire' , '')
voting_centers.bureau_to_match = voting_centers.bureau_to_match.str.replace('ecole' , '')

voting_centers.bureau_to_match = voting_centers.bureau_to_match.str.replace('1|2' , '').str.strip()
voting_centers.loc[voting_centers.bureau_to_match.str[-2:-1] == ' ' ,
                    'bureau_to_match'] = voting_centers.bureau_to_match[voting_centers.bureau_to_match.str[-2:-1] == ' '].str[:-2]
voting_centers.bureau_to_match = voting_centers.bureau_to_match.str.replace('-' , ' ').str.strip()

renaloc.loc[renaloc.locality_to_match.str[-2:-1] == ' ' ,
                    'locality'] = renaloc.locality_to_match[renaloc.locality_to_match.str[-2:-1] == ' '].str[:-2]

renaloc.locality_to_match = renaloc.locality_to_match.str.replace('\\/' , ' ')

voting_centers.bureau_to_match = voting_centers.bureau_to_match.str.strip().str.lower()
renaloc.locality_to_match = renaloc.locality_to_match.str.strip().str.lower()

## Loading approximate manual matching
voting_centers = pd.merge(voting_centers , dico_data ,
                        right_on = 'elec_name' ,
                        left_on = 'bureau_to_match' ,
                        how = 'left')

voting_centers.loc[pd.isnull(voting_centers.renaloc_name) , 'renaloc_name'] = voting_centers.bureau_to_match[pd.isnull(voting_centers.renaloc_name)]

exact_match = pd.merge(renaloc , voting_centers ,
                        left_on = ['commune_ID' , 'locality_to_match'] ,
                        right_on = ['commune_ID' , 'renaloc_name'])

#duplicate_bureaux  = list(exact_match.bureau_ID.value_counts()[(exact_match.bureau_ID.value_counts() > 1)].index)
geolocalized_bureaux = exact_match#[~(exact_match.commune_ID.isin(duplicate_bureaux))]

print(len(geolocalized_bureaux))

## Look at unmatched bureaux
u = sorted(voting_centers.bureau_to_match[(~(voting_centers.bureau_ID.isin(geolocalized_bureaux.bureau_ID))) & (voting_centers.commune_ID == 10201)])

len(u)

u

v = sorted(renaloc.locality_to_match[~renaloc.renaloc_ID.isin(geolocalized_bureaux.renaloc_ID)  & (renaloc.commune_ID == 10201)])

len(v)
v

voting_centers.commune_ID.unique()

## Mapping sur NOM
## Show

## W in renaloc can be OU in voting_centers


geolocalized_bureaux.to_csv('../../data/processed/geolocalized_bureaux.csv' , index = False)


## Utilisation de covariates pour predire  ou son nom manquants
