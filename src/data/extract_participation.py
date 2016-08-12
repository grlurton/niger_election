import pandas as pd
import os as os


## Setting working directory
os.chdir('c://users/grlurton/documents/niger_election_data')

resultat_premier_tour = pd.HDFStore('data/raw/data_resultats_premier_tour.h5')
premier_tour_commune = resultat_premier_tour['data_communes']
premier_tour_departement = resultat_premier_tour['data_departements']
resultat_premier_tour.close()

premier_tour_departement['departement' \
                            ] = premier_tour_departement.ID.str.split('Departement de :').str.get(1)

premier_tour_departement.head()

premier_tour_departement.loc[premier_tour_departement['departement'].isin(['TIBIRI (DOUTCHI)']), 'departement'] = 'TIBIRI'
premier_tour_departement.loc[premier_tour_departement['Commune'].isin(['MARADI ARRONDISSEMENT 1']), 'Commune'] = 'ARRONDISSEMENT 1'
premier_tour_departement.loc[premier_tour_departement['Commune'].isin(['MARADI ARRONDISSEMENT 2']), 'Commune'] = 'ARRONDISSEMENT 2'
premier_tour_departement.loc[premier_tour_departement['Commune'].isin(['MARADI ARRONDISSEMENT 3']), 'Commune'] = 'ARRONDISSEMENT 3'


## getting everything out
out = premier_tour_departement.loc[: , ['Commune' , 'departement' , 'Suffrages exprimés valables' , 'Mahamadou Issoufou' , 'Hama Amadou' , 'Ibrahim Yacouba' , 'Seyni Omar' , 'Mahamane Ousmane']]
out.columns  = ['commune' , 'departement' , 'voting'  , 'Mahamadou Issoufou' , 'Hama Amadou' , 'Ibrahim Yacouba' , 'Seyni Omar' , 'Mahamane Ousmane']

out.to_csv('data/interim/voting_first_round.csv'  , index = False)
