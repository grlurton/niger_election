# coding: utf-8

## Loading Relevant libraries
import pandas as pd
import os as os
import json


## Adding Unique IDs
store_electeurs = pd.HDFStore('../../data/raw/full_data.h5')
data = store_electeurs['complete_data']
store_electeurs.close()

def correct_profession(key):
    print(key)
    data.loc[data.corrected_profession.isin(correction_dictionnary[key]) , 'corrected_profession'] = key
    return data
len(data)
data = data[data.NOM_REGION != 'DIASPORA']

data['corrected_profession'] = list(data['profession'])

print(data.corrected_profession.nunique())
data.corrected_profession = data.corrected_profession.str.replace('à|â' , 'a').str.replace('é|è|a\x89','e').str.replace("\(|\)","").str.replace("  "," ").str.replace("a\x87|\Ç","c").str.replace("\xa0|Â£|Âµ|Â²","")


with open('../../data/dictionnaries/professions_recode.json') as json_data:
    correction_dictionnary = json.load(json_data)
    json_data.close()

for key in list(correction_dictionnary.keys()):
    data = correct_profession(key)

print(data.corrected_profession.nunique())


print(data.corrected_profession.value_counts()[0:60])

print(data.corrected_profession.unique()[1500:1589])

data[data.corrected_profession == '3RAMATOU']

def ff(data):
    return data.corrected_profession.value_counts()

len(data)
u = data.groupby('NOM_REGION').apply(ff)

len(u['NIAMEY'])


u['NIAMEY']
data.head()
