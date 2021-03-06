import pandas as pd
import warnings
import os as os

renaloc = pd.read_csv('../../data/processed/renaloc_geolocalized.csv' , encoding = "ISO-8859-1" )
renaloc = renaloc[['locality' , 'population' , 'hommes' , 'femmes' , 'menages' , 'menages_agricoles' ,
                    'locality_type' , 'region' , 'departement' , 'commune' , 'milieu' ,
                    'longitude' , 'latitude' , 'commune_ID' , 'GPS_NAME' , 'GPS_ID']]
renaloc.columns = ['localite' , 'population' , 'hommes' , 'femmes' , 'menages' , 'menages_agricoles' ,
                    'localite_type' , 'region' , 'departement' , 'commune' , 'milieu' ,
                    'longitude' , 'latitude' , 'commune_ID' , 'GPS_NAME' , 'GPS_ID']

renacom = pd.read_csv('../../data/processed/renacom_full.csv' , encoding = 'ISO-8859-1')
renacom = renacom[['MILIEU' , 'REGION' , 'DEPARTEMENT' , 'COMMUNE' , 'LOCALITE' ,
                    'TYPELOCALITE' , 'MASCULIN' , 'FEMININ' , 'TOTAL' , 'MENAGE' , 'LONGITUDE' ,
                    'LATITUDE' , 'commune_ID']]
renacom.columns = ['milieu' , 'region' , 'departement' , 'commune' , 'locality' , 'locality_type' ,
                    'hommes' , 'femmes' , 'population' , 'menages' , 'longitude' , 'latitude' ,
                    'commune_ID']
renacom = renacom[renacom.latitude != ' ']

voting_centers = pd.read_csv('../../data/processed/voting_bureaux_size.csv' ,  encoding = "ISO-8859-1" )
voting_centers = voting_centers[['bureau_ID' , 'commune_ID' , 'bureau' , 'N_voters']]
## Drop bureaux of the diaspora
voting_centers = voting_centers[voting_centers.commune_ID < 90000]

dico_data = pd.read_csv('../../data/dictionnaries/locality_name_map.csv' ,  encoding = "ISO-8859-1" )

## Make RENALOC ID for each locality
renaloc['localite_ID'] = range(len(renaloc))
renacom['localite_ID'] = range(len(renacom))

##  standardize variables on which to match
voting_centers['bureau_to_match'] = voting_centers.bureau.str.strip().str.lower()

renaloc['locality_to_match'] = renaloc.localite.str.strip().str.lower()
renaloc['region'] = renaloc.region.str.strip().str.lower()
renaloc['departement'] = renaloc.departement.str.strip().str.lower()
renaloc['commune'] = renaloc.commune.str.strip().str.lower()

renacom['locality_to_match'] = renacom.localite.str.strip().str.lower()
renacom['region'] = renacom.region.str.strip().str.lower()
renacom['departement'] = renacom.departement.str.strip().str.lower()
renacom['commune'] = renacom.commune.str.strip().str.lower()

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
#voting_centers = pd.merge(voting_centers , dico_data ,
#                        right_on = ['commune_ID' , 'elec_name'] ,
#                        left_on = ['commune_ID' , 'bureau_to_match'] ,
#                        how = 'left')

#voting_centers.loc[pd.isnull(voting_centers.renaloc_name) , 'renaloc_name'] = voting_centers.bureau_to_match[pd.isnull(voting_centers.renaloc_name)]

############
### MATCHING

## First Match Bureaux and RENACOM
renacom_bureaux = pd.merge(renacom , voting_centers ,
                        left_on = ['commune_ID' , 'locality_to_match'] ,
                        right_on = ['commune_ID' , 'bureau_to_match'] ,
                        how = 'left')

## Then Match the result with RENALOC where possible
renacom_bureaux_renaloc = pd.merge(renacom_bureaux , renaloc ,
                                        left_on = ['region' , 'departement' , 'commune' , 'commune_ID' , 'locality_to_match'] ,
                                        right_on = ['region' , 'departement' , 'commune' , 'commune_ID' , 'locality_to_match'] ,
                                        how = 'left' ,
                                        suffixes = ['_renacom' , '_renaloc'])

renacom_bureaux_renaloc.to_csv('../../data/processed/geolocalized_bureaux.csv' , index = False)

renacom_bureaux_renaloc.locality_to_match.value_counts()

from difflib import SequenceMatcher

def similar(a , b):
    return SequenceMatcher(None, a, b).ratio()

out_dico  = dico_data

communes_to_read = [20301]
for commune in communes_to_read :
    print(commune)
    renacom_matched_bureau = list(renacom_bureaux_renaloc.locality_to_match[pd.isnull(renacom_bureaux_renaloc.bureau_to_match)])
    renacom_to_match_bureau = renacom_bureaux_renaloc.locality_to_match[(~renacom_bureaux_renaloc.locality_to_match.isin(renacom_matched_bureau)) & (renacom_bureaux_renaloc.commune_ID == commune)].tolist()
    print(str(len(renacom_to_match_bureau)) + ' localities in RENACOM to match with bureaux')
    bur_to_match =  list(set(sorted(voting_centers.bureau_to_match[((~voting_centers.bureau_to_match.isin(renacom_bureaux_renaloc.bureau_to_match)  ) & (voting_centers.commune_ID == commune))])))
    print(str(len(bur_to_match)) + ' bureaux to match with RENACOM')

    renacom_matched_renaloc = list(renacom_bureaux_renaloc.locality_to_match[~pd.isnull(renacom_bureaux_renaloc.localite_renaloc)])
    renacom_to_match_renaloc = renacom_bureaux_renaloc.locality_to_match[(~renacom_bureaux_renaloc.locality_to_match.isin(renacom_matched_renaloc)) & (renacom_bureaux_renaloc.commune_ID == commune)].tolist()
    print(str(len(renacom_to_match_renaloc)) + ' localities in RENACOM to match with RENALOC')
    renaloc_to_match = list(set(sorted(renaloc.locality_to_match[~renaloc.locality_to_match.isin(renacom_matched_renaloc)  & (renaloc.commune_ID == commune)])))
    print(str(len(renaloc_to_match)) + ' localities in RENALOC to match with RENACOM')
    out_renacom = []
    out_matched = []
    out_match_type = []

    for j in range(len(renacom_to_match)) :
        renacom_to_test = renacom_to_match[j]
        matched = []
        match_type = []
        bureaux_matched = renaloc_matched = []
        for i in range(len(bur_to_match)):
            dist = similar(renacom_to_test, bur_to_match[i])
            if dist > 0.7 :
                bureaux_matched = bureaux_matched + [bur_to_match[i]]
        if len(bureaux_matched) > 0 :
            n_match = input("Which of: " + str(bureaux_matched) + " for " + renacom_to_test)
            if len(n_match) > 0 :
                n_match = n_match.split(',')
                n_match = [int(l[0]) for l in n_match]
                for i in n_match :
                    out_renacom = out_renacom + [renacom_to_test]
                    out_matched = out_matched + [bureaux_matched[i]]
                    out_match_type = out_match_type + ['bureau']

        for i in range(len(renaloc_to_match)):
            dist = similar(renacom_to_test, renaloc_to_match[i])
            if dist > 0.7 :
                renaloc_matched = renaloc_matched + [renaloc_to_match[i]]
        if len(renaloc_matched) > 0 :
            n_match = input("Which of: " + str(renaloc_matched) + " for " + renacom_to_test)
            if len(n_match) > 0 :
                n_match = n_match.split(',')
                n_match = [int(l[0]) for l in n_match]
                for i in n_match :
                    out_renacom = out_renacom + [renacom_to_test]
                    out_matched = out_matched + [renaloc_matched[i]]
                    out_match_type = out_match_type + ['RENALOC']
    for_out = pd.DataFrame({'commune_ID':commune ,
                            'out_renacom':out_renacom ,
                            'out_matched':out_matched ,
                            'out_match_type':out_match_type})
    out_dico = out_dico.append(for_out)

out_dico.to_csv('../../data/dictionnaries/locality_name_map.csv' , index = False)
