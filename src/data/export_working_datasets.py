# coding: utf-8

## Loading Relevant libraries
import pandas as pd

## Setting working directory

## Getting full data in
renaloc = pd.read_csv('../../data/processed/renaloc_full.csv' , encoding = "ISO-8859-1" )

## Keeping only data with geolocation
geolocalized_data = renaloc[pd.isnull(renaloc.longitude) == False]
geolocalized_data.to_csv('../../data/processed/renaloc_geolocalized.csv' , index = False)

## Other output for localities only
locality_data = renaloc[renaloc.level == 'Localite']
locality_data.to_csv('../../data/processed/renaloc_localities.csv' , index = False)

## TAKE OUT DUPLICATE VOTERS
voters_data = pd.read_csv('../../data/processed/voters_list.csv' , encoding = "ISO-8859-1")
len(voters_data)

n_ids = voters_data['unique_ID'].value_counts()
doublons = n_ids[n_ids > 1]

doub_data = voters_data[voters_data.unique_ID.isin(list(doublons.keys()))]
unique_data = voters_data[~(voters_data.unique_ID.isin(list(doublons.keys())))]

d = doub_data.groupby('unique_ID').apply(keep_unique_voters)

dedoubled = d.reset_index(drop = True)

final = unique_data.append(dedoubled)
final = final.reset_index(drop = True)

final.to_csv('../../data/processed/voters_list.csv' , index = False)
