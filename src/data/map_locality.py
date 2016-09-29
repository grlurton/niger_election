import pandas as pd
import warnings
import os as os

renaloc = pd.read_csv('../../data/processed/renaloc_geolocalized.csv' , encoding = "ISO-8859-1" )
voting_centers = pd.read_csv('../../data/raw/Niger_Bureaux.csv' ,  encoding = "ISO-8859-1" )

names_ratios = {}
ratio_list = []
for i in voting_centers.ID_COMMUNE.unique() :
    if i < 90000 :
        rat  = len(voting_centers[voting_centers.ID_COMMUNE == i]) / len(renaloc[renaloc.commune_ID == i])
        names_ratios[i] = rat
        ratio_list.append(rat)

voting_centers.NOM_BUREAU = voting_centers.NOM_BUREAU.str.strip().str.lower()
renaloc.locality = renaloc.locality.str.strip().str.lower()

voting_centers.NOM_BUREAU = voting_centers.NOM_BUREAU.str.replace('ecole primaire' , '')
voting_centers.NOM_BUREAU = voting_centers.NOM_BUREAU.str.replace('ecole' , '')

voting_centers.NOM_BUREAU = voting_centers.NOM_BUREAU.str.strip().str.lower()
renaloc.locality = renaloc.locality.str.strip().str.lower()


exact_match = pd.merge(renaloc , voting_centers ,
                        left_on = ['commune_ID' , 'locality'] ,
                        right_on = ['ID_COMMUNE' , 'NOM_BUREAU'])

duplicate_bureaux  = list(exact_match.ID_BUREAU.value_counts()[(exact_match.ID_BUREAU.value_counts() > 1)].index)

geolocalized_bureaux = exact_match[~(exact_match.ID_COMMUNE.isin(duplicate_bureaux))]

## Mapping sur NOM
## Utilisation de covariates pour predire  ou son nom manquants

## Show

## W in renaloc can be OU in voting_centers
## Enlever ["ECOLE PRIMAIRE" , "ECOLE"] dans voting_centers

geolocalized_bureaux.to_csv('../../data/processed/geolocalized_bureaux.csv' , index = False)
