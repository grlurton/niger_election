# coding: utf-8

## Loading Relevant libraries
import pandas as pd
import os as os

## Setting working directory
os.chdir('c://users/grlurton/documents/niger_election_data')

## Getting full data in
renaloc = pd.read_csv('data/processed/renaloc_full.csv' , encoding = "ISO-8859-1" )

## Keeping only data with geolocation
geolocalized_data = renaloc[pd.isnull(renaloc.longitude) == False]
geolocalized_data.to_csv('data/processed/renaloc_geolocalized.csv')

## Other output for localities only
locality_data = renaloc[renaloc.level == 'Localite']
locality_data.to_csv('data/processed/renaloc_localities.csv')
