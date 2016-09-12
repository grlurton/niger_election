# coding: utf-8

## Loading Relevant libraries
import pandas as pd
import os as os
import json


## Adding Unique IDs
data = pd.read_csv("../../data/processed/voters_list.csv" , encoding = "ISO-8859-1")

def correct_profession(key):
    print(key)
    data.loc[data.corrected_profession.isin(correction_dictionnary[key]) , "corrected_profession"] = key
    return data

len(data)

data = data[data.region != "DIASPORA"]

len(data)

data["corrected_profession"] = list(data["profession"])

print(data.corrected_profession.nunique())
data.corrected_profession = data.corrected_profession.str.replace("à|â" , "a").str.replace("É|é|è|a\x89|a\x88","e").str.replace("\(|\)","").str.replace("  "," ").str.replace("a\x87|\Ç","c").str.replace("\xa0|Â£|Âµ|Â²|\?|²|\µ","")


with open("../../data/dictionnaries/professions_recode.json") as json_data:
    correction_dictionnary = json.load(json_data)
    json_data.close()

for key in list(correction_dictionnary.keys()):
    data = correct_profession(key)

print(data.corrected_profession.nunique())

print(data.corrected_profession.value_counts()[40:80])

print(data.corrected_profession.value_counts()[200:265])

print(data.corrected_profession[~(data.corrected_profession.isin(list(correction_dictionnary.keys())))].unique()[0:100])

data[data.profession == 'AGENT AIRTEL']

##### ON A DES IDs DE VOTERS DUPLIQUES A TAHOUA
sum(data.unique_ID.value_counts() == 2)
