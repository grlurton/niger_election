import pandas as pd
import os as os

resultat_premier_tour = pd.HDFStore('../../data/raw/data_resultats_premier_tour.h5')
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
out = premier_tour_departement.loc[: , ['Commune' , 'departement' , 'Inscrits', 'Inscrits ayant voté', 'Votants sur liste additive', 'Nbre total de votants', 'Bulletins blancs ou nuls', 'Suffrages exprimés valables' , 'Laouan Magagi', 'Mahaman Jean Philipe Padonou', 'Abdou Labo', 'Kassoum M. Moctar', 'Adal Rhoubeid', 'Mahamane Ousmane', 'Seyni Omar', 'Tahirou Guimba', 'Hama Amadou', 'Ibrahim Yacouba', 'Mahaman Hamissou Maman', 'Mahamadou Issoufou', 'Dr. Abdoulaye Amadou Traoré', 'Cheffou Amadou', 'Boubacar Cissé' ] ]

candidats = ['laouan_magagi', 'jean_philipe_padonou', 'abdou_labo', 'kassoum_moctar', 'adal_rhoubeid', 'mahamane_ousmane', 'seyni_omar', 'tahirou_guimba', 'hama_amadou', 'ibrahim_yacouba', 'mahaman_hamissou_maman', 'mahamadou_issoufou', 'abdoulaye_amadou_traore', 'cheffou_amadou', 'boubacar_cisse']

out.columns  = ['commune' , 'departement'  , 'registered' , 'registered_voting' , 'additional_list' , 'total_voting' , 'invalid_votes' , 'valid_votes'] + candidats

for can in candidats + ['registered_voting' , 'additional_list' , 'total_voting' , 'invalid_votes' , 'valid_votes'] :
    nam = can + '_prop'
    out[nam] = out[can] / out['registered']

out.to_csv('../../data/interim/voting_first_round.csv'  , index = False)
