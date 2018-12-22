import pandas as pd
import geopandas as gpd


# Load different data
renacom = pd.read_csv('~/data/niger_election_data/processed/renacom_full.csv',
                      encoding="ISO-8859-1")
renaloc = pd.read_csv('~/data/niger_election_data/processed/renaloc_full.csv',
                      encoding="ISO-8859-1")
renaloc = renaloc[renaloc.level == 'Localite']
renaloc.region = renaloc.region.str.lower()
renaloc.departement = renaloc.departement.str.lower()
renaloc.commune = renaloc.commune.str.lower()
osm = pd.read_csv('~/data/osm/niger.csv', encoding="ISO-8859-1")
bureaux = pd.read_csv('~/data/niger_election_data/raw/Niger_Bureaux.csv',
                      encoding='ISO-8859-1')
health_facilities = pd.read_csv('~/data/dhis/niger/org_units_description.csv')


# Standardize names in RENALOC and RENACOM
def change_number(name, suffix, changer):
    """Change suffixes in names."""
    len_suffix = len(suffix)
    to_change = (name.str[-len_suffix:] == suffix)
    changer = name[to_change].str[0:-len_suffix] + [changer]
    name.loc[to_change] = changer
    return name


change_number(renacom.commune, ' i', ' 1')
change_number(renacom.commune, ' ii', ' 2')
change_number(renacom.commune, ' iii', ' 3')
change_number(renacom.commune, ' iv', ' 4')
change_number(renacom.commune, ' v', ' 5')
change_number(renaloc.commune, ' i', ' 1')
change_number(renaloc.commune, ' ii', ' 2')


# Add region, departement, commune in bureaux
commune = pd.read_csv('~/data/niger_election_data/raw/Niger_Communes.csv',
                      encoding='ISO-8859-1')
bureaux = bureaux.drop('Unnamed: 0', axis=1)
commune = commune.drop('Unnamed: 0', axis=1)
bureaux = bureaux.merge(commune)
departement = pd.read_csv('~/data/niger_election_data/raw/Niger_Departements.csv',
                          encoding='ISO-8859-1')
departement = departement.drop('Unnamed: 0', axis=1)
bureaux = bureaux.merge(departement)
region = pd.read_csv('~/data/niger_election_data/raw/Niger_Regions.csv',
                     encoding='ISO-8859-1')
region = region.drop('Unnamed: 0', axis=1)
bureaux = bureaux.merge(region)

bureaux = bureaux[['ID_BUREAU', 'NOM_BUREAU', 'NOM_COMMUNE', 'NOM_DEPART',
                   'NOM_REGION']]
bureaux.columns = ['locality_id', 'locality', 'commune', 'departement',
                   'region']

bureaux.commune = bureaux.commune.str.lower()
bureaux.departement = bureaux.departement.str.lower()
bureaux.region = bureaux.region.str.lower()


change_number(bureaux.commune, ' i', ' 1')
change_number(bureaux.commune, ' ii', ' 2')
change_number(bureaux.commune, ' iii', ' 3')
change_number(bureaux.commune, ' iv', ' 4')
change_number(bureaux.commune, ' v', ' 5')
renacom.commune[~renacom.commune.isin(bureaux.commune)].unique()
bureaux.commune[bureaux.commune == 'tibiri (doutchi)'] = 'tibiri'
bureaux.commune[bureaux.commune == 'gangara (aguie)'] = 'gangara'
bureaux.commune[bureaux.commune == 'gangara (tanout)'] = 'gangara'
bureaux.commune[bureaux.commune == 'tibiri (maradi)'] = 'tibiri'
bureaux.commune[bureaux.commune == 'maradi arrondissement 1'] = 'arrondissement 1'
bureaux.commune[bureaux.commune == 'maradi arrondissement 2'] = 'arrondissement 2'
bureaux.commune[bureaux.commune == 'maradi arrondissement 3'] = 'arrondissement 3'
bureaux.departement[bureaux.departement == 'tibiri (doutchi)'] = 'tibiri'

# TODO Add region, departement, commune in dhis

health_facilities.name[health_facilities.name.str.contains('une')]

# TODO if needed geocache DHIS
# TODO Geocache osm
