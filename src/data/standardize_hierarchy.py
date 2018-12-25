import pandas as pd
import geopandas as gpd

pd.options.mode.chained_assignment = None

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

# Standardize GPS communes names

fp = '/Users/grlurton/data/niger_election_data/external/commune_shp/nigcom.shp'
commune_gps = gpd.read_file(fp)

commune_gps.GPS_NAME = commune_gps.GPS_NAME.str.lower()

renaloc_no_match = renaloc[~renaloc.commune.isin(commune_gps.GPS_NAME)]
gps_no_match = commune_gps[~commune_gps.GPS_NAME.isin(renaloc.commune)]


def standardize_name(var, pattern, replace):
    out = var.loc[:].str.replace(pattern, replace)
    return out.values


gps_no_match.loc[:, 'standard_name'] = standardize_name(gps_no_match['GPS_NAME'], "'", "")
renaloc_no_match.loc[:, 'standard_name'] = standardize_name(renaloc_no_match['commune'], "'", "")


dico = {}

for idx in gps_no_match.index:
    standard_name = gps_no_match.loc[idx, 'standard_name']
    if standard_name in renaloc_no_match.standard_name.tolist():
        print(standard_name)
        ren_name = renaloc_no_match.loc[renaloc_no_match['standard_name'] == standard_name,'commune'].unique()[0]
        dico[ren_name] = gps_no_match.loc[idx, 'GPS_NAME']
        commune_gps.loc[idx, 'GPS_NAME'] = ren_name

dico


renaloc_no_match = renaloc[~renaloc.commune.isin(commune_gps.GPS_NAME)]
gps_no_match = commune_gps[~commune_gps.GPS_NAME.isin(renaloc.commune)]

gps_no_match.loc[:, 'standard_name'] = standardize_name(gps_no_match['GPS_NAME'], "-", " ")
renaloc_no_match.loc[:, 'standard_name'] = standardize_name(renaloc_no_match['commune'], "-", " ")


for idx in gps_no_match.index:
    standard_name = gps_no_match.loc[idx, 'standard_name']
    if standard_name in renaloc_no_match.standard_name.tolist():
        print(standard_name)
        ren_name = renaloc_no_match.loc[renaloc_no_match['standard_name'] == standard_name,'commune'].unique()[0]
        dico[ren_name] = gps_no_match.loc[idx, 'GPS_NAME']
        commune_gps.loc[idx, 'GPS_NAME'] = ren_name

renaloc_no_match = renaloc[~renaloc.commune.isin(commune_gps.GPS_NAME)]
gps_no_match = commune_gps[~commune_gps.GPS_NAME.isin(renaloc.commune)]


gps_no_match.loc[:, 'standard_name'] = standardize_name(gps_no_match['GPS_NAME'], " ", "")
renaloc_no_match.loc[:, 'standard_name'] = standardize_name(renaloc_no_match['commune'], " ", "")


for idx in gps_no_match.index:
    standard_name = gps_no_match.loc[idx, 'standard_name']
    if standard_name in renaloc_no_match.standard_name.tolist():
        print(standard_name)
        ren_name = renaloc_no_match.loc[renaloc_no_match['standard_name'] == standard_name,'commune'].unique()[0]
        dico[ren_name] = gps_no_match.loc[idx, 'GPS_NAME']
        commune_gps.loc[idx, 'GPS_NAME'] = ren_name

renaloc_no_match = renaloc[~renaloc.commune.isin(commune_gps.GPS_NAME)]
gps_no_match = commune_gps[~commune_gps.GPS_NAME.isin(renaloc.commune)]


dico["attantane"] = "attatane"
dico["bankilare"] = "bankillare"
dico['birni lalle'] = 'birni nlalle'
dico['damagaram takaya'] = "damagaram-t"
dico['dan-goulbi'] = 'dan goulgi'
dico['diagourou'] = 'diagorou'
dico["dingazi"] = 'dingazi banda'
dico["djiratawa"] = 'djirataoua'
dico["dogonkiria"] = "dogon kirya"
dico['el allassane maireyrey'] = 'alhassane  mairerey'
dico['falmey/falmey haoussa'] = 'falmey'
dico['farey'] = 'farrey'
dico['galma koudawatche'] = "galma"
dico['goroubankassam'] = 'goroun bakassam'
dico['guidan amoumoune'] = 'guidan amoumane'
dico['guilladje'] = 'guiladje'
dico['kablewa'] = 'kabalewa'
dico['kourfeye centre'] = 'kourfey centre'
dico['kourteye'] = 'kourtey'
dico['makalondi'] = "parc w"
dico['matamey'] = "matameye"
dico["n'guelbely"] = 'nguel bely'
dico['ouro gueladjo'] = 'ouro gueladio'
dico['roumbou 1'] = 'roumbou i'
dico['sakoira'] = 'sakouara'
dico['sarkin haoussa'] = "serkin haoussa"
dico['sarkin yamma'] = 'sarkin yama'
dico['tagriss'] = 'tagris'
dico['tombokoirey 1'] = 'tombokoarey 1'
dico['tombokoirey 2'] = 'tombokoarey 2'
dico['tondikiwindi'] = 'tondikwindi'
dico['tsernaoua'] = 'tsernawa'


for comm in dico.keys():
    commune_gps.GPS_NAME[commune_gps.GPS_NAME == dico[comm]] = comm

renaloc_no_match = renaloc[~renaloc.commune.isin(commune_gps.GPS_NAME)]
gps_no_match = commune_gps[~commune_gps.GPS_NAME.isin(renaloc.commune)]


# [k for k, v in dico.items() if 'dogo dogo' in v]

# Geocache OSM

# OSM data from https://download.geofabrik.de/africa/niger.html

fp = '/Users/grlurton/data/osm/niger-latest-free.shp/gis_osm_places_free_1.shp'
osm_data = gpd.read_file(fp)

osm_data = osm_data.to_crs(commune_gps.crs)


osm_data = gpd.sjoin(osm_data, commune_gps, how="inner", op="within")


# TODO Add region, departement, commune in dhis


# TODO if needed geocache DHIS


# Standardize output

renacom_keep = ['MILIEU', 'region', 'departement', 'commune', 'LOCALITE',
                'TYPELOCALITE', 'MASCULIN', 'FEMININ',
                'TOTAL', 'LONGITUDE', 'LATITUDE']
renacom_out = renacom[renacom_keep]
renacom_out.columns = ['milieu', 'region', 'departement', 'commune',
                       'locality', 'locality_type', 'hommes', 'femmes',
                       'population', 'longitude', 'latitude']
renacom_out['source'] = 'renacom'
renacom_out['locality_id'] = ['RENACOM'] + pd.Series(list(range(len(renacom_out)))).astype(str)

renaloc_keep = ['locality', 'population', 'hommes', 'femmes',
                'settlement_type', 'region', 'departement', 'commune',
                'longitude', 'latitude']
renaloc_out = renaloc[pd.isnull(renaloc.milieu)]
renaloc_out = renaloc_out[renaloc_keep]
renaloc_out.columns = ['locality', 'population', 'hommes', 'femmes',
                       'locality_type', 'region', 'departement', 'commune',
                       'longitude', 'latitude']
renaloc_out['source'] = 'renaloc'
renaloc_out['locality_id'] = ['RENALOC'] + pd.Series(list(range(len(renaloc_out)))).astype(str)

osm_keep = ['osm_id', 'fclass', 'population', 'name', 'geometry', 'GPS_NAME',
            'REGION']
osm_data['longitude'] = osm_data.geometry.x
osm_data['latitude'] = osm_data.geometry.y
osm_out = osm_data[osm_keep]
osm_out.columns = ['locality_id', 'locality_type', 'population', 'locality',
                   'geometry', 'commune', 'region']
osm_out['source'] = 'osm'

bureaux_out = bureaux[~(bureaux.region == 'diaspora')]
bureaux_out['source'] = 'bureaux'


data_out = renacom_out.append(renaloc_out).append(osm_out).append(bureaux_out)








data_out.to_csv("~/data/niger_election_data/processed/pooled_data.csv")
