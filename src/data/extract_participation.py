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


## getting everything out
out = premier_tour_departement.loc[: , ['Commune' , 'departement' , 'Suffrages exprimés valables']]
out.columns  = ['commune' , 'departement' , 'voting']

out.to_csv('data/interim/voting_first_round.csv')
