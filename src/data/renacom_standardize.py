import pandas as pd

renaloc = pd.read_csv('../../data/processed/renaloc_geolocalized.csv' , encoding = "ISO-8859-1" )
renacom = pd.read_csv('../../data/external/2006 - RENACOM.csv' , encoding = 'ISO-8859-1')

renacom.REGION = renacom.REGION.str.strip().str.lower()
renacom.DEPARTEMENT = renacom.DEPARTEMENT.str.strip().str.lower()
renacom.COMMUNE = renacom.COMMUNE.str.strip().str.lower()

renaloc.region = renaloc.region.str.strip().str.lower()
renaloc.departement = renaloc.departement.str.strip().str.lower()
renaloc.commune = renaloc.commune.str.strip().str.lower()


## Change urban communes
renaloc['commune'] = renaloc['commune'].str.replace('1' , 'i').str.replace('2' , 'ii').str.replace('3' , 'iii').str.replace('4' , 'iv').str.replace('5' , 'v')
arrondissements = ['arrondissement i' , 'arrondissement ii' , 'arrondissement iii' , 'arrondissement iv' , 'arrondissement v']

renacom.loc[renacom['DEPARTEMENT'] == "niamey" , 'COMMUNE'] = renacom.loc[renacom['DEPARTEMENT'] == "niamey" , 'COMMUNE'].str.replace("niamey " , "arrondissement ")
renacom.loc[renacom['DEPARTEMENT'] == "mirriah" , 'COMMUNE'] = renacom.loc[renacom['DEPARTEMENT'] == "mirriah" , 'COMMUNE'].str.replace("zinder " , "arrondissement ")
renacom.loc[(renacom['DEPARTEMENT'] == 'mirriah') & (renacom['COMMUNE'].isin(arrondissements))  , 'DEPARTEMENT'] = 'zinder'
renacom.loc[renacom['DEPARTEMENT'] == "madarounfa" , 'COMMUNE'] = renacom.loc[renacom['DEPARTEMENT'] == "madarounfa" , 'COMMUNE'].str.replace("maradi " , "arrondissement ")
renacom.loc[(renacom['DEPARTEMENT'] == 'madarounfa') & (renacom['COMMUNE'].isin(arrondissements))  , 'DEPARTEMENT'] = 'maradi'
renacom.loc[renacom['DEPARTEMENT'] == "tahoua" , 'COMMUNE'] = renacom.loc[renacom['DEPARTEMENT'] == "tahoua" , 'COMMUNE'].str.replace("tahoua " , "arrondissement ")

## Typos change
renacom.loc[renacom['DEPARTEMENT'] == 'maine soroa' ,  'DEPARTEMENT'] = 'maine-soroa'
renacom.loc[(renacom['DEPARTEMENT'] == 'maine-soroa') & (renacom['COMMUNE'] == 'foulateri') ,  'COMMUNE'] = 'foulatari'
renacom.loc[(renacom['DEPARTEMENT'] == 'maine-soroa') & (renacom['COMMUNE'] == "n'guelbeyli") ,  'COMMUNE'] = "n'guelbely"
renacom.loc[(renacom['DEPARTEMENT'] == "n'guigmi") & (renacom['COMMUNE'] == "kabelewa") ,  'COMMUNE'] = "kablewa"
renacom.loc[(renacom['DEPARTEMENT'] == "n'guigmi") & (renacom['COMMUNE'] == "kabelewa") ,  'COMMUNE'] = "kablewa"
renacom.loc[(renacom['DEPARTEMENT'] == "dosso") & (renacom['COMMUNE'] == "farrey") ,  'COMMUNE'] = "farey"
renacom.loc[(renacom['DEPARTEMENT'] == "dosso") & (renacom['COMMUNE'] == "garankedeye") ,  'COMMUNE'] = "garankedey"
renacom.loc[(renacom['DEPARTEMENT'] == "dosso") & (renacom['COMMUNE'] == "gorouban kassam") ,  'COMMUNE'] = "goroubankassam"
renacom.loc[(renacom['DEPARTEMENT'] == "dosso") & (renacom['COMMUNE'] == "kargui bangou") ,  'COMMUNE'] = "karguibangou"
renacom.loc[renacom['DEPARTEMENT'] == "dosso" , 'COMMUNE'] = renacom.loc[renacom['DEPARTEMENT'] == "dosso" , 'COMMUNE'].str.replace("tombo koarey " , "tombokoirey ")
renacom.loc[(renacom['DEPARTEMENT'] == "boboye") & (renacom['COMMUNE'] == "fabirdji") ,  'COMMUNE'] = "fabidji"
renacom.loc[(renacom['DEPARTEMENT'] == "boboye") & (renacom['COMMUNE'] == "falmey") ,  'COMMUNE'] = "falmey/falmey haoussa"
renacom.loc[(renacom['DEPARTEMENT'] == "boboye") & (renacom['COMMUNE'] == "harika-nassou") ,  'COMMUNE'] = "harikanassou"
renacom.loc[(renacom['DEPARTEMENT'] == "dogondoutchi") & (renacom['COMMUNE'] == "dan kassari") ,  'COMMUNE'] = "dan-kassari"
renacom.loc[(renacom['DEPARTEMENT'] == "dogondoutchi") & (renacom['COMMUNE'] == "dogon kiria") ,  'COMMUNE'] = "dogonkiria"
renacom.loc[(renacom['DEPARTEMENT'] == "dogondoutchi") & (renacom['COMMUNE'] == "tibiri (doutchi)") ,  'COMMUNE'] = "tibiri"
renacom.loc[(renacom['DEPARTEMENT'] == "gaya") & (renacom['COMMUNE'] == "dioudou") ,  'COMMUNE'] = "dioundiou"
renacom.loc[(renacom['DEPARTEMENT'] == "gaya") & (renacom['COMMUNE'] == "kara kara") ,  'COMMUNE'] = "karakara"
renacom.loc[(renacom['DEPARTEMENT'] == "madarounfa") & (renacom['COMMUNE'] == "dan issa") ,  'COMMUNE'] = "dan-issa"
renacom.loc[(renacom['DEPARTEMENT'] == "madarounfa") & (renacom['COMMUNE'] == "djirataoua") ,  'COMMUNE'] = "djiratawa"
renacom.loc[(renacom['DEPARTEMENT'] == "madarounfa") & (renacom['COMMUNE'] == "serki yama") ,  'COMMUNE'] = "sarkin yamma"
renacom.loc[(renacom['DEPARTEMENT'] == "dakoro") & (renacom['COMMUNE'] == "adjiekoria") ,  'COMMUNE'] = "adjekoria"
renacom.loc[(renacom['DEPARTEMENT'] == "dakoro") & (renacom['COMMUNE'] == "dan goulbi") ,  'COMMUNE'] = "dan-goulbi"
renacom.loc[(renacom['DEPARTEMENT'] == "dakoro") & (renacom['COMMUNE'] == "sabonmachi") ,  'COMMUNE'] = "sabon machi"
renacom.loc[(renacom['DEPARTEMENT'] == "guidan-roumdji") & (renacom['COMMUNE'] == "tibiri (maradi)") ,  'COMMUNE'] = "tibiri"
renacom.loc[(renacom['DEPARTEMENT'] == "mayahi") & (renacom['COMMUNE'] == "alhassane maireyrey") ,  'COMMUNE'] = "el allassane maireyrey"
renacom.loc[(renacom['DEPARTEMENT'] == "mayahi") & (renacom['COMMUNE'] == "kanambakache") ,  'COMMUNE'] = "kanan-bakache"
renacom.loc[(renacom['DEPARTEMENT'] == "mayahi") & (renacom['COMMUNE'] == "sarki haoussa") ,  'COMMUNE'] = "sarkin haoussa"
renacom.loc[(renacom['DEPARTEMENT'] == "tessaoua") & (renacom['COMMUNE'] == "baoudeta") ,  'COMMUNE'] = "baoudetta"
renacom.loc[(renacom['DEPARTEMENT'] == "tahoua") & (renacom['COMMUNE'] == "afala") ,  'COMMUNE'] = "affala"
renacom.loc[(renacom['DEPARTEMENT'] == "tahoua") & (renacom['COMMUNE'] == "takanamatt") ,  'COMMUNE'] = "takanamat"
renacom.loc[(renacom['DEPARTEMENT'] == "birni n'konni") & (renacom['COMMUNE'] == "dogueraoua") ,  'COMMUNE'] = "doguerawa"
renacom.loc[(renacom['DEPARTEMENT'] == "bouza") & (renacom['COMMUNE'] == "allakeye") ,  'COMMUNE'] = "allakaye"
renacom.loc[(renacom['DEPARTEMENT'] == "bouza") & (renacom['COMMUNE'] == "baban katami") ,  'COMMUNE'] = "babankatami"
renacom.loc[(renacom['DEPARTEMENT'] == "bouza") & (renacom['COMMUNE'] == "korafane") ,  'COMMUNE'] = "karofane"
renacom.loc[(renacom['DEPARTEMENT'] == "kollo") & (renacom['COMMUNE'] == "dantchandou") ,  'COMMUNE'] = "diantchandou"
renacom.loc[(renacom['DEPARTEMENT'] == "say") & (renacom['COMMUNE'] == "ouro gueledjo") ,  'COMMUNE'] = "ouro gueladjo"
renacom.loc[(renacom['DEPARTEMENT'] == "tera") & (renacom['COMMUNE'] == "goroual") ,  'COMMUNE'] = "gorouol"
renacom.loc[(renacom['DEPARTEMENT'] == "mirriah") & (renacom['COMMUNE'] == "gafati") ,  'COMMUNE'] = "gaffati"
renacom.loc[(renacom['DEPARTEMENT'] == "mirriah") & (renacom['COMMUNE'] == "koleram") ,  'COMMUNE'] = "kolleram"
renacom.loc[(renacom['DEPARTEMENT'] == "magaria") & (renacom['COMMUNE'] == "dantchio") ,  'COMMUNE'] = "dantchiao"
renacom.loc[(renacom['DEPARTEMENT'] == "magaria") & (renacom['COMMUNE'] == "dogo dogo") ,  'COMMUNE'] = "dogo-dogo"
renacom.loc[(renacom['DEPARTEMENT'] == "magaria") & (renacom['COMMUNE'] == "mallaoua") ,  'COMMUNE'] = "malawa"
renacom.loc[(renacom['DEPARTEMENT'] == "matamaye") & (renacom['COMMUNE'] == "matamaye") ,  'COMMUNE'] = "matamey"
renacom.loc[(renacom['DEPARTEMENT'] == "tanout") & (renacom['COMMUNE'] == "falanko") ,  'COMMUNE'] = "falenko"
renacom.loc[(renacom['DEPARTEMENT'] == "tanout") & (renacom['COMMUNE'] == "ganganra") ,  'COMMUNE'] = "gangara"
renacom.loc[(renacom['DEPARTEMENT'] == "tanout") & (renacom['COMMUNE'] == "tenhia") ,  'COMMUNE'] = "tenhya"

## Departement Change
renacom.loc[(renacom['DEPARTEMENT'] == 'tchirozerine') & (renacom['COMMUNE'] == 'aderbissinat')  , 'DEPARTEMENT'] = 'aderbissinat'
renacom.loc[(renacom['DEPARTEMENT'] == 'tchirozerine') & (renacom['COMMUNE'] == 'ingall')  , 'DEPARTEMENT'] = 'ingall'
renacom.loc[(renacom['DEPARTEMENT'] == 'arlit') & (renacom['COMMUNE'].isin(['iferouane' , 'timia']))  , 'DEPARTEMENT'] = 'iferouane'
renacom.loc[(renacom['DEPARTEMENT'] == 'diffa') & (renacom['COMMUNE'].isin(['bosso' , 'toumour']))  , 'DEPARTEMENT'] = 'bosso'
renacom.loc[(renacom['DEPARTEMENT'] == 'maine-soroa') & (renacom['COMMUNE'].isin(['goudoumaria']))  , 'DEPARTEMENT'] = 'goudoumaria'
renacom.loc[(renacom['DEPARTEMENT'] == "n'guigmi") & (renacom['COMMUNE'].isin(["n'gourti"]))  , 'DEPARTEMENT'] = "n'gourti"
renacom.loc[(renacom['DEPARTEMENT'] == "boboye") & (renacom['COMMUNE'].isin(["falmey/falmey haoussa" , "guilladje"])) ,  'DEPARTEMENT'] = "falmey"
renacom.loc[(renacom['DEPARTEMENT'] == "dogondoutchi") & (renacom['COMMUNE'].isin(["doumega" , "guecheme" , "kore mairoua" , "tibiri"])) ,  'DEPARTEMENT'] = "tibiri"
renacom.loc[(renacom['DEPARTEMENT'] == "gaya") & (renacom['COMMUNE'].isin(["dioundiou" , "karakara" , "zabori"])) ,  'DEPARTEMENT'] = "dioundiou"
renacom.loc[(renacom['DEPARTEMENT'] == "aguie") & (renacom['COMMUNE'].isin(["gangara" , "gazaoua"])) ,  'DEPARTEMENT'] = "gazaoua"
renacom.loc[(renacom['DEPARTEMENT'] == "dakoro") & (renacom['COMMUNE'].isin(["bermo" , "gadabedji"])) ,  'DEPARTEMENT'] = "bermo"
renacom.loc[(renacom["DEPARTEMENT"] == "birni n'konni") & (renacom['COMMUNE'].isin(["doguerawa" , "malbaza"])) ,  'DEPARTEMENT'] = "malbaza"
renacom.loc[(renacom["DEPARTEMENT"] == "illela") & (renacom['COMMUNE'].isin(["bagaroua"])) ,  'DEPARTEMENT'] = "bagaroua"
renacom.loc[(renacom["DEPARTEMENT"] == "tchintabaraden") & (renacom['COMMUNE'].isin(["tassara"])) ,  'DEPARTEMENT'] = "tassara"
renacom.loc[(renacom["DEPARTEMENT"] == "tchintabaraden") & (renacom['COMMUNE'].isin(["tillia"])) ,  'DEPARTEMENT'] = "tillia"
renacom.loc[(renacom["DEPARTEMENT"] == "tillaberi") & (renacom['COMMUNE'].isin(["ayerou" , "inates"])) ,  'DEPARTEMENT'] = "ayerou"
renacom.loc[(renacom["DEPARTEMENT"] == "filingue") & (renacom['COMMUNE'].isin(["abala" , "sanam"])) ,  'DEPARTEMENT'] = "abala"
renacom.loc[(renacom["DEPARTEMENT"] == "filingue") & (renacom['COMMUNE'].isin(["tagazar"])) ,  'DEPARTEMENT'] = "balleyara"
renacom.loc[(renacom["DEPARTEMENT"] == "ouallam") & (renacom['COMMUNE'].isin(["banibangou"])) ,  'DEPARTEMENT'] = "banibangou"
renacom.loc[(renacom["DEPARTEMENT"] == "tera") & (renacom['COMMUNE'].isin(["bankilare"])) ,  'DEPARTEMENT'] = "bankilare"
renacom.loc[(renacom["DEPARTEMENT"] == "tera") & (renacom['COMMUNE'].isin(["dargol" , "gotheye"])) ,  'DEPARTEMENT'] = "gotheye"
renacom.loc[(renacom["DEPARTEMENT"] == "say") & (renacom['COMMUNE'].isin(["torodi"])) ,  'DEPARTEMENT'] = "torodi"
renacom.loc[(renacom["DEPARTEMENT"] == "mirriah") & (renacom['COMMUNE'].isin(["albarkaram" , "damagaram takaya" , "guidimouni" , "mazamni" , "moa" , "wame"])) ,  'DEPARTEMENT'] = "damagaram takaya"
renacom.loc[(renacom["DEPARTEMENT"] == "mirriah") & (renacom['COMMUNE'].isin(["dakoussa" , "garagoumsa" , 'tirmini'])) ,  'DEPARTEMENT'] = "takeita"
renacom.loc[(renacom["DEPARTEMENT"] == "goure") & (renacom['COMMUNE'].isin(["tesker"])) ,  'DEPARTEMENT'] = "tesker"
renacom.loc[(renacom["DEPARTEMENT"] == "magaria") & (renacom['COMMUNE'].isin(["dogo-dogo" , "dungass" , "gouchi" , "malawa"])) ,  'DEPARTEMENT'] = "dungass"
renacom.loc[(renacom["DEPARTEMENT"] == "matamaye") & (renacom['COMMUNE'].isin(["dan barto" , "daouche" , "doungou" , "ichirnawa" , "kantche" , "kourni" , "tsaouni" , "yaouri" , "matamey"])) ,  'DEPARTEMENT'] = "kantche"
renacom.loc[(renacom["DEPARTEMENT"] == "tanout") & (renacom['COMMUNE'].isin(["tarka"])) ,  'DEPARTEMENT'] = "belbedji"


renacom_com = renacom[['CodeCommune' , 'REGION' , 'DEPARTEMENT' , 'COMMUNE']].drop_duplicates()
renaloc_com = renaloc[[ 'commune_ID' , 'region' , 'departement' , 'commune']].drop_duplicates()

dico_commune = pd.merge(renaloc_com , renacom_com ,
                        left_on = ['region' , 'departement' , 'commune'] ,
                        right_on = ['REGION' , 'DEPARTEMENT' , 'COMMUNE'])

dico_to_merge = dico_commune[['CodeCommune' , 'region' , 'departement' , 'commune' , 'commune_ID']]

out = pd.merge(renacom , dico_to_merge , on = ['CodeCommune'])


out.to_csv('../../data/processed/renacom_full.csv' , index = False)
