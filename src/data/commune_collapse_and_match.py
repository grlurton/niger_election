# coding: utf-8

import pandas as pd
import warnings
import os as os

warnings.filterwarnings('ignore')

## Loading data from Renaloc
renaloc = pd.read_csv('../../data/processed/renaloc_localities.csv'  , encoding = "ISO-8859-1")

## Loading data from electoral lists
data_electeurs = pd.read_csv('../../data/processed/voters_list.csv'  , encoding = "ISO-8859-1")

## Droping data for electors from the Diaspora
data_electeurs = data_electeurs[~(data_electeurs['region'] == 'DIASPORA')]

data_electeurs.GPS_ID = data_electeurs.GPS_ID.astype(str)
renaloc.GPS_ID = renaloc.GPS_ID.astype(str)

## Compute population in each data source and merge sources
def sum_population(data):
    return data.population.sum(skipna = True)

pop_commune = renaloc.groupby([ 'region'  , 'departement' , 'GPS_ID' , 'GPS_NAME']).apply( sum_population ).reset_index()

vote_commune = data_electeurs.groupby(['region' , 'departement' ,'GPS_ID' , 'GPS_NAME']).apply( len ).reset_index( )

pop_commune.columns = vote_commune.columns = ['region' , 'departement'  , 'GPS_ID' , 'GPS_NAME' , 'population']
vote_commune.GPS_ID = vote_commune.GPS_ID.astype(str)
pop_commune.GPS_ID = pop_commune.GPS_ID.astype(str)

merged_data = pd.merge(left = pop_commune , right = vote_commune ,
                       how = 'inner' , on = ['GPS_NAME' , 'departement' , 'region', 'GPS_ID'] ,
                       suffixes = ['_census' , '_voting_list'])

## Get proportion of population on voting list
merged_data['prop_inscrits'] = merged_data.population_voting_list / merged_data.population_census

renaloc.GPS_ID.nunique()

## Get mean age in each commune
def mean_age(data):
    return data.age.mean()

voters_age = data_electeurs.groupby(['region' , 'departement' ,'GPS_ID' , 'GPS_NAME' ]).apply(mean_age).reset_index()
voters_age.columns = ['region' , 'departement' ,'GPS_ID' , 'GPS_NAME' , 'mean_age']

merged_data = pd.merge(left = merged_data , right = voters_age ,
                       how = 'inner' , on = ['departement' , 'region' ,'GPS_ID' , 'GPS_NAME'] )

## Get proportion of women in each commune
def prop_women(data) :
    u = data.femmes.sum() / data.population.sum(skipna = True)
    return u

prop_women = renaloc.groupby(['region' , 'departement' , 'GPS_ID' , 'GPS_NAME']).apply(prop_women).reset_index()
prop_women.columns = ['region' , 'departement' , 'GPS_ID' , 'GPS_NAME' , 'prop_women']

merged_data = pd.merge(left = merged_data , right = prop_women ,
                       how = 'inner' , on = ['departement' , 'region','GPS_ID' , 'GPS_NAME'] )



## Adding participation
participation_data = pd.read_csv('../../data/interim/voting_first_round.csv'  , encoding = "ISO-8859-1")
participation_data.GPS_ID = participation_data.GPS_ID.astype(str)



merged_data = pd.merge(merged_data , participation_data ,
                on = ['GPS_ID' , 'GPS_NAME' , 'departement' , 'region'])

merged_data['urbain'] = list((merged_data['commune'].str[0:14] == 'ARRONDISSEMENT') | (merged_data['commune'] == merged_data['region']))

## Output the resulting data

len(merged_data)
merged_data.to_csv('../../data/processed/commune_collapsed_matched.csv' , index = False)
