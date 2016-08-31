# coding: utf-8

import pandas as pd
import os as os
import numpy as np
import pickle

from scipy.interpolate import UnivariateSpline

## Additional analytic tools
import statsmodels.formula.api as smf

from multiprocessing.pool import ThreadPool


import warnings
warnings.filterwarnings('ignore')

## Setting working directory

if os.name == 'nt':
    os.chdir('h://niger_election_data')

if os.name == 'posix':
    os.chdir('niger_election_data')


## SETTING PARAMETERS
age_adulte = 19

## Voters data
voters_data = pd.read_csv('data/processed/voters_list.csv' , encoding = "ISO-8859-1")
voters_data = voters_data[(voters_data.age >= age_adulte) & (voters_data.region != 'DIASPORA')]

## Model data
model_data = pd.read_csv('data/processed/commune_collapsed_matched.csv' , encoding = "ISO-8859-1")

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


## Dans ce script on s'arrete a la prediction, et on output le full dataset avec les predictions. On fera les rmse et autres visualisations dans le notebook

model_data.columns = list(model_data.columns.str.replace(' ' , '_'))

model = "population_census ~ population_voting_list + mean_age + voting + urbain + prop_women"
n_folds = 7

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

model_total.to_csv('data/processed/model_data.csv')

#######################
### Splining functions
#######################

def spl_age(data):
    """
    Function to get spline of age from a distribution estimated with get_age_distribution
    """
    out = UnivariateSpline(data['age'] , data['percentage'])
    return out

def impute_non_adulte(splines , age_adulte = age_adulte):
    """
    Imputing non adulte distributions in population smoothed from a spline
    """
    age_extrap = range(0,age_adulte)
    age_range = range(age_adulte,101)
    out = {'splined':list(splines(age_range)) ,
        'extrapol':list(splines(age_extrap))}
    return out

def get_spline_from_sample(sample):
    """
    Wrapper function to get age distribution, spline it and impute non adults from a given sample
    """
    age_dist = age_distrib(sample)
    splines = spl_age(age_dist)
    extrapolated_data = impute_non_adulte(splines)
    return extrapolated_data









### Running the models

def spline_on_level(i):
    """
    Wrapper to get the bootstrapped splines
    """
    print(i)
    out = voters_data.groupby(levels).apply(get_spline_from_sample)
    return out

def boot_splines_to_dataframe(boot_splines , levels):
    """
    Taking bootstraped splines and making them into dataframe
    """
    if type(boot_splines) is list :
        out = pd.DataFrame(boot_splines[0].reset_index())
        for i in range(1, len(boot_splines)):
            out = out.append(pd.DataFrame(boot_splines[i].reset_index()))
    else :
        out = boot_splines.reset_index()
    out.columns = levels + ['data']
    out = out.reset_index()
    out['splined'] = out['extrapolated'] = 'uu'
    for j in range(len(out)) :
        out.set_value(j, 'splined', out.loc[j , 'data']['splined'])
        out.set_value(j, 'extrapolated', out.loc[j , 'data']['extrapol'])
    return out










####################
### Getting structure for complete data

levels= ['region' , 'departement' ,  'commune']
levels = ['region' , 'departement']

age_structure = voters_data.groupby(levels).apply(age_distrib)
age_structure = age_structure.reset_index()
del age_structure['level_' + str(len(levels))]
age_structure.columns = levels + ['age' , 'percentage']

splined_data = boot_splines_to_dataframe(voters_data.groupby(levels).apply(get_spline_from_sample) , levels)

## Getting bootstrapped splines

n_processes = os.cpu_count() - 5
n_replications = 50

threadPool = ThreadPool(n_processes)
boot_splines = threadPool.map(spline_on_level , list(range(n_replications)))

bootstrapedsplined = boot_splines_to_dataframe(boot_splines , levels)

def get_spline_95IC(out_spline):
    """
    Function to get the 95 Confidence interval from splined age structure
    """
    ext5 = pd.DataFrame(list(out_spline['extrapolated'])).quantile(q=0.025, axis=0, numeric_only=True)
    ext95 = pd.DataFrame(list(out_spline['extrapolated'])).quantile(q=0.975, axis=0, numeric_only=True)
    spl5 = pd.DataFrame(list(out_spline['splined'])).quantile(q=0.025, axis=0, numeric_only=True)
    spl95 = pd.DataFrame(list(out_spline['splined'])).quantile(q=0.975, axis=0, numeric_only=True)
    return {'extrapolation_5':ext5 , 'extrapolation_95':ext95 ,
            'splining_5':spl5 , 'splining_95':spl95}


### Computing IC95 for splined age structures
ICSplined = bootstrapedsplined.groupby(levels).apply(get_spline_95IC)
ICSplined = ICSplined.reset_index()
ICSplined.columns = levels + ['IC95']

out = {'splined_data':splined_data , 'confidence_intervals':ICSplined , 'age_structure':age_structure}

pickle.dump(out , open("data/processed/bootstraped_splines.p" , "wb"))
