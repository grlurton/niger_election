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

def keep_unique_voters(data):
    return data.iloc[0]

d = voters_data.groupby('unique_ID').apply(keep_unique_voters)
