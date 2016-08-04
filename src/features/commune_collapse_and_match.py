# coding: utf-8

import pandas as pd
import json
import warnings
import os as os

warnings.filterwarnings('ignore')

## Setting working directory
os.chdir('c://users/grlurton/documents/niger_election_data')

## Loading data from Renaloc
renaloc = pd.read_csv('data/processed/renaloc_localities.csv'  , encoding = "ISO-8859-1")

## Loading data from electoral lists
data_electeurs = pd.read_csv('data/processed/voters_list.csv'  , encoding = "ISO-8859-1")

## Droping data for electors from the Diaspora
data_electeurs = data_electeurs[~(data_electeurs['NOM_REGION'] == 'DIASPORA')]
data_electeurs.gps_ID = data_electeurs.gps_ID.astype(str)
## Compute population in each data source and merge sources
def sum_population(data):
    return data.population.sum(skipna = True)

def len_population(data) :
    return len(data)

pop_commune = renaloc.groupby([ 'region'  , 'departement' , 'gps_ID' , 'gps_name' , 'commune' ]).apply( sum_population ).reset_index()

vote_commune = data_electeurs.groupby(['NOM_REGION' , 'NOM_DEPART' ,'gps_ID' , 'gps_name' , 'NOM_COMMUNE' ]).apply( len_population ).reset_index( )
pop_commune.columns = vote_commune.columns = ['region' , 'departement'  , 'gps_ID' , 'gps_name' ,'commune' , 'population']
#vote_commune.gps_ID = vote_commune.gps_ID.astype(str)
merged_data = pd.merge(left = pop_commune , right = vote_commune ,
                       how = 'inner' , on = ['commune' , 'departement' , 'region' ,'gps_ID' , 'gps_name'] ,
                       suffixes = ['_census' , '_voting_list'])

## Get proportion of population on voting list
merged_data['prop_inscrits'] = merged_data.population_voting_list / merged_data.population_census

## Get mean age in each commune
def mean_age(data):
    return data.age.mean()

voters_age = data_electeurs.groupby(['NOM_REGION' , 'NOM_DEPART' ,'gps_ID' , 'gps_name' , 'NOM_COMMUNE' ]).apply(mean_age).reset_index()
voters_age.columns = ['region' , 'departement' ,'gps_ID' , 'gps_name' ,'commune' , 'mean_age']

merged_data = pd.merge(left = merged_data , right = voters_age ,
                       how = 'inner' , on = ['commune' , 'departement' , 'region' ,'gps_ID' , 'gps_name'] )


## Get proportion of women in each commune
def prop_women(data) :
    u = data.femmes.sum() / data.population.sum(skipna = True)
    return u

prop_women = renaloc.groupby(['region' , 'departement' , 'gps_ID' , 'gps_name', 'commune']).apply(prop_women).reset_index()
prop_women.columns = ['region' , 'departement' , 'gps_ID' , 'gps_name' , 'commune' , 'prop_women']

merged_data = pd.merge(left = merged_data , right = prop_women ,
                       how = 'inner' , on = ['commune' , 'departement' , 'region','gps_ID' , 'gps_name'] )


## Adding participation
participation_data = pd.read_csv('data/interim/voting_first_round.csv'  , encoding = "ISO-8859-1")

merged_data = pd.merge(merged_data , participation_data ,
                on = ['commune' , 'departement'])

## Output the resulting data
merged_data.to_csv('data/processed/commune_collapsed_matched.csv' , index = False)
