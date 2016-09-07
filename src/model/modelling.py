# coding: utf-8

import pandas as pd
import numpy as np
import pickle
import os

from scipy.interpolate import UnivariateSpline

## Additional analytic tools
import statsmodels.formula.api as smf

from multiprocessing.pool import ThreadPool


import warnings
warnings.filterwarnings('ignore')

## Setting working directory

## SETTING PARAMETERS
age_adulte = 19

## Voters data
voters_data = pd.read_csv('../../data/processed/voters_list.csv' , encoding = "ISO-8859-1")
voters_data = voters_data[(voters_data.age >= age_adulte) & (voters_data.region != 'DIASPORA')]

## Model data
model_data = pd.read_csv('../../data/processed/commune_collapsed_matched.csv' , encoding = "ISO-8859-1")

def get_bootstrap_sample(voters_data):
    bootstrap_sample = voters_data.sample(n = len(voters_data) , replace = True)
    return bootstrap_sample

def age_distrib(data) :
    """
    Function to get the distribution of voters by age in a dataset. Age is censored at 100.
    """
    data.age[data.age > 100] = 100
    out =  np.round(data.age).value_counts() / len(data)
    out = out.reset_index()


    out.columns = ['age' , 'percentage']
    return out

def get_full_model_data(bootstrap_sample , model_data , levels):
    """
    Getting the model data
    """
    N_Voters = bootstrap_sample.groupby(levels).apply(len).reset_index()
    full_data = pd.merge(N_Voters , model_data , on = levels , how = 'inner')
    return full_data

def get_variables_def(results) :
    """
    Function that goes through a statsmodel summary and returns list of variables and values to include in prediction
    """
    variables = list(results.params.keys())
    variable_list = {}
    for var in variables :
        value = ''
        out = {'variable':var}
        var_split = var.split('[')
        if len(var_split) > 1 :
            value = var_split[1].replace(']' , '').replace('T.' , '')
            out = {'variable':var_split[0] , 'value':value , 'parametre':var}
        variable_list[var] = out
    return variable_list

def pred_random_effect(re_model , test_data , random_effect):
    """
    Function that returns the response of a statsmodel random effect linear model
    """
    test_data['Intercept'] = test_data['Intercept RE'] = 1
    params = re_model.params
    variables = get_variables_def(re_model)
    out = 0
    for var in list(variables.keys()) :
        v = variables[var]
        if len(v) > 1 :
            out = out + params[v['parametre']]*(str(test_data[v['variable']]) == v['value'])
        if len(v) == 1 :
            out = out + params[v['variable']]*test_data[v['variable']]

    if len(test_data[random_effect].unique()) > len(re_model.random_effects.Intercept) :
        missing = test_data.loc[(test_data[random_effect].isin(list(re_model.random_effects.Intercept.index)) == False) , random_effect].unique()
        for reg in missing :
            print(missing + ' is missing')
            re_model.random_effects.Intercept[reg] = 0

    random_effects = list(re_model.random_effects.Intercept[test_data.loc[: , random_effect]])
    out =  out + random_effects

    return out

def k_fold_validation(n_folds , data , model , random_effect):
    """
    Function that performs k_fold validation computations for random effect
    """
    samp = np.random.choice(len(data), len(data) , replace = False)
    test_out = ''
    for i in range(n_folds):
        f = np.round(((i)*(len(data)/n_folds))).astype(int)
        l = np.round(((i + 1)*(len(data)/n_folds))).astype(int)
        out = samp[f:l]
        train_dat = data[~data.index.isin(out)]
        test_dat = data[data.index.isin(out)]
        result = smf.mixedlm(model , data = train_dat , groups = train_dat[random_effect]).fit()
        test_dat['prediction'] = pred_random_effect(result , test_dat , random_effect)
        if len(test_out) > 0 :
            test_out = test_out.append(test_dat)
        elif len(test_out) == 0 :
            test_out = test_dat
    return test_out

n_folds = 7
model = "population_census ~ population_voting_list + mean_age + urbain + prop_women + laouan_magagi_prop + jean_philipe_padonou_prop + abdou_labo_prop + kassoum_moctar_prop + adal_rhoubeid_prop + mahamane_ousmane_prop + seyni_omar_prop + tahirou_guimba_prop + hama_amadou_prop + ibrahim_yacouba_prop + mahamadou_issoufou_prop + abdoulaye_amadou_traore_prop + cheffou_amadou_prop + boubacar_cisse_prop + registered_voting_prop + additional_list_prop + invalid_votes_prop + valid_votes_prop"

def model_predict_bootstrap(i):
    """
    Wrapper to get the bootstrapped predictions for a model
    """
    print(i)
    sample = get_bootstrap_sample(model_data)
    sample = sample.reset_index()
    del sample['index']
    out = k_fold_validation(n_folds , sample , model , 'region')
    return out


## Getting bootstrapped splines
n_processes = os.cpu_count()
n_replications = 250

threadPool = ThreadPool(n_processes)
bootstrapped_models = threadPool.map(model_predict_bootstrap , list(range(n_replications)))

model_total = pd.concat(bootstrapped_models, axis=0)

model_total.to_csv('../../data/processed/model_data.csv')
