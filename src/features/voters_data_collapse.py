# coding: utf-8

import pandas as pd
import json
import warnings
import os as os
import numpy as np
import pickle


from scipy.interpolate import UnivariateSpline

## For parralell computing
from joblib import Parallel, delayed

warnings.filterwarnings('ignore')

## Setting working directory
os.chdir('c://users/grlurton/documents/niger_election_data')

## Voters data
voters_data = pd.read_csv('data/processed/voters_list.csv' , encoding = "ISO-8859-1")
voters_data = voters_data[(voters_data.age >= 18) & (voters_data.NOM_REGION != 'DIASPORA')]


def age_distrib(data) :
    """
    Function to get the distribution of voters by age in a dataset. Age is censored at 100.
    """
    data.age[data.age > 100] = 100
    out =  np.round(data.age).value_counts() / len(data)
    out = out.reset_index()
    out.columns = ['age' , 'percentage']
    return out

def get_age_distribution(data , level):
    """
    Function to get age distribution in data stratified by different levels
    """
    out = data.groupby(level).apply(age_distrib).reset_index()
    sort_order = level + ['age']
    out = out.sort(sort_order, ascending=[1]*len(sort_order))
    i = len(level)
    lev_to_drop = 'level_' + str(i)
    del out[lev_to_drop]
    return out

def spl_age(data):
    """
    Function to get spline of age from a distribution estimated with get_age_distribution
    """
    out = UnivariateSpline(data['age'] , data['percentage'])
    return out

def impute_non_adulte(splines , age_adulte = 18):
    """
    Imputing non adulte distributions in population smoothed from a spline
    """
    age_extrap = range(0,age_adulte)
    age_range = range(age_adulte,101)
    out = {'splined':list(splines(age_range)) ,
        'extrapol':list(splines(age_extrap))}
    return out

def get_spline_from_sample(voters_data , level):
    """
    Wrapper function to get age distribution, spline it and impute non adults from a given sample
    """
    age_dist = get_age_distribution(voters_data , level)
    extrapolated_data = {}
    splines = age_dist.groupby(level).apply(spl_age)
    for region in list(splines.index.levels[0]) :
        sp_reg = splines[region]
        for departement in list(sp_reg.index.levels[0]) :
            sp_reg_d = sp_reg[departement]
            for commune in list(sp_reg_d.index) :
                splinned = impute_non_adulte(splines[region][departement][commune])
                extrapolated_data[region + '_' + commune] = {'commune' : commune ,
                                                         'departement' : departement ,
                                                         'region' : region ,
                                                         'splinned': splinned['splined'] ,
                                                         'extrapolated' : splinned['extrapol']}
    return extrapolated_data

def sample_spline(voters_data , level):
    """
    Wrapper function to draw sample and return splines smoothed curve and extrapolation
    """
    sample = np.random.choice(len(voters_data), len(voters_data) , replace = True)
    sample = voters_data.iloc[sample]
    u = get_spline_from_sample(sample , level)
    return u

level = ['NOM_REGION' , 'NOM_DEPART' , 'NOM_COMMUNE']

def bootstrap_spline(voters_data = voters_data, level = level , n_rep = 1000):
    out = Parallel(n_jobs=4, verbose=10 , backend = 'threading')(delayed(sample_spline)(voters_data , level) for i in range(n_rep))
    return out

boot_splines = voters_data.groupby(level).apply(bootstrap_spline)

pickle.dump(boot_splines , open("data/processed/bootstraped_splines.p" , "wb"))
