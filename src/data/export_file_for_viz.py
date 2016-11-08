import pandas as pd

bureaux_loc = pd.read_csv('../../data/processed/geolocalized_bureaux.csv')

to_drop = ['milieu' , 'menages' , 'geoloc' , 'menages_agricoles' ,
            'Unnamed: 0' , "bureau_to_match" , "elec_name" , 'renaloc_name' ,
            'level' , 'GPS_NAME' , "locality_to_match"]

for var in to_drop :
    del bureaux_loc[var]

bureaux_loc.to_csv('../../data/processed/data_for_viz.csv')
