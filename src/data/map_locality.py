import pandas as pd
import warnings
import os as os

renaloc = pd.read_csv('../../data/processed/renaloc_geolocalized.csv' , encoding = "ISO-8859-1" )
renacom = pd.read_csv('../../data/external/2006 - RENACOM.csv' , encoding = 'ISO-8859-1')
voting_centers = pd.read_csv('../../data/processed/voting_bureaux_size.csv' ,  encoding = "ISO-8859-1" )
dico_data = pd.read_csv('../../data/dictionnaries/locality_name_map.csv' ,  encoding = "ISO-8859-1" )

voting_centers.head()


## Drop bureaux of the diaspora
voting_centers = voting_centers[voting_centers.commune_ID < 90000]

## Make RENALOC ID for each locality
renaloc['renaloc_ID'] = range(len(renaloc))


##  Make variables on which to match
voting_centers['bureau_to_match'] = voting_centers.bureau.str.strip().str.lower()
renaloc['locality_to_match'] = renaloc.locality.str.strip().str.lower()
renacom['locality_to_match'] = renacom.LOCALITE.str.strip().str.lower()

## Format voting centers bureaux names
voting_centers.bureau_to_match = voting_centers.bureau_to_match.str.replace('ecole primaire' , '')
voting_centers.bureau_to_match = voting_centers.bureau_to_match.str.replace('ecole' , '')
voting_centers.bureau_to_match = voting_centers.bureau_to_match.str.replace('quartier' , '')

voting_centers.bureau_to_match = voting_centers.bureau_to_match.str.replace('1|2' , '').str.strip()
voting_centers.loc[voting_centers.bureau_to_match.str[-2:-1] == ' ' ,
                    'bureau_to_match'] = voting_centers.bureau_to_match[voting_centers.bureau_to_match.str[-2:-1] == ' '].str[:-2]
voting_centers.bureau_to_match = voting_centers.bureau_to_match.str.replace('-' , ' ').str.strip()
voting_centers.bureau_to_match = voting_centers.bureau_to_match.str.strip().str.lower()


## Format renaloc names
renaloc.loc[renaloc.locality_to_match.str[-2:-1] == ' ' ,
                    'locality'] = renaloc.locality_to_match[renaloc.locality_to_match.str[-2:-1] == ' '].str[:-2]
renaloc.locality_to_match = renaloc.locality_to_match.str.replace('\\/' , ' ')
renaloc.locality_to_match = renaloc.locality_to_match.str.strip().str.lower()

## Format renaloc names
renacom.loc[renaloc.locality_to_match.str[-2:-1] == ' ' ,
                    'locality'] = renacom.locality_to_match[renacom.locality_to_match.str[-2:-1] == ' '].str[:-2]
renacom.locality_to_match = renacom.locality_to_match.str.replace('\\/' , ' ')
renacom.locality_to_match = renacom.locality_to_match.str.strip().str.lower()



## Loading approximate manual matching
voting_centers = pd.merge(voting_centers , dico_data ,
                        right_on = ['commune_ID' , 'elec_name'] ,
                        left_on = ['commune_ID' , 'bureau_to_match'] ,
                        how = 'left')

voting_centers.loc[pd.isnull(voting_centers.renaloc_name) , 'renaloc_name'] = voting_centers.bureau_to_match[pd.isnull(voting_centers.renaloc_name)]


############
### MATCHING

### check and Mapping
from difflib import SequenceMatcher


def similar(a , b):
    return SequenceMatcher(None, a, b).ratio()

out_dico  = dico_data

renaloc[renaloc.commune_ID == 10101]

communes_to_read = [10101]
for commune in communes_to_read :
    out_bureau = []
    out_renaloc = []
    print(commune)
    bur_to_match = list(set(sorted(voting_centers.bureau_to_match[(~voting_centers.bureau_to_match.isin(geolocalized_bureaux.renaloc_ID)  ) & (voting_centers.commune_ID == commune)])))
    ren_to_match = list(set(sorted(renaloc.locality_to_match[~renaloc.renaloc_ID.isin(geolocalized_bureaux.renaloc_ID)  & (renaloc.commune_ID == commune)])))
    for j in range(len(bur_to_match)) :
        bur_test = bur_to_match[j]
        matches = []
        for i in range(len(ren_to_match)):
            dist = similar(bur_test, ren_to_match[i])
            if dist > 0.7 :
                matches = matches + [ren_to_match[i]]
        if len(matches) > 0 :
            n_match = input("Which of: " + str(matches) + " for " + bur_test)
            if len(n_match) > 0 :
                out_bureau = out_bureau + [bur_test]
                out_renaloc = out_renaloc + [matches[int(n_match)]]
    for_out = pd.DataFrame({'commune_ID':commune , 'elec_name':out_bureau , 'renaloc_name':out_renaloc})
    out_dico = out_dico.append(for_out)

out_dico.to_csv('../../data/dictionnaries/locality_name_map.csv' , index = False)

geolocalized_bureaux = pd.merge(renaloc , voting_centers ,
                        left_on = ['commune_ID' , 'locality_to_match'] ,
                        right_on = ['commune_ID' , 'renaloc_name'])
print(len(geolocalized_bureaux))

## Look at unmatched bureaux
u = sorted(voting_centers.bureau_to_match[(~voting_centers.bureau_to_match.isin(geolocalized_bureaux.renaloc_ID)  ) & (voting_centers.commune_ID == 70101)])
print(len(u))
u

v = sorted(renaloc.locality_to_match[~renaloc.renaloc_ID.isin(geolocalized_bureaux.renaloc_ID)  & (renaloc.commune_ID == 70101)])
print(len(v))
v

geolocalized_bureaux.to_csv('../../data/processed/geolocalized_bureaux.csv' , index = False)





## Utilisation de covariates pour predire  ou son nom manquants
