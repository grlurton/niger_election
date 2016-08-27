# coding: utf-8

import pandas as pd
import os as os
import numpy as np
import pickle

from scipy.interpolate import UnivariateSpline

from multiprocessing import Pool
from multiprocessing.pool import ThreadPool


#warnings.filterwarnings('ignore')

## Setting working directory
os.chdir('h://niger_election_data')

## Voters data
voters_data = pd.read_csv('data/processed/voters_list.csv' , encoding = "ISO-8859-1")

age_adulte = 18
voters_data = voters_data[(voters_data.age >= age_adulte) & (voters_data.region != 'DIASPORA')]

def age_distrib(data) :
    """
    Function to get the distribution of voters by age in a dataset. Age is censored at 100.
    """
    data.age[data.age > 100] = 100
    out =  np.round(data.age).value_counts() / len(data)
    out = out.reset_index()
    out.columns = ['age' , 'percentage']
    return out

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

def get_spline_from_sample(voters_data):
    """
    Wrapper function to get age distribution, spline it and impute non adults from a given sample
    """
    sample = voters_data.sample(n = len(voters_data) , replace = True)
    age_dist = age_distrib(sample)
    splines = spl_age(age_dist)
    extrapolated_data = impute_non_adulte(splines)
    return extrapolated_data

def spline_on_level(i):
    """
    Wrapper to get the bootstrapped splines
    """
    print(i)
    out = voters_data.groupby(levels).apply(get_spline_from_sample)
    return out


## Getting bootstrapped splines

n_processes = 4
n_replications = 4
levels= ['region' , 'departement' ,  'commune']

#pool = Pool(n_processes)
threadPool = ThreadPool(n_processes)
boot_splines = threadPool.map(spline_on_level , list(range(n_replications)))

def boot_splines_to_dataframe(boot_splines , levels):
    """
    Taking bootstraped splines and making them into dataframe
    """
    out = pd.DataFrame(boot_splines[0].reset_index())
    for i in range(1, len(boot_splines)):
        out = out.append(pd.DataFrame(boot_splines[i].reset_index()))
    out.columns = levels + ['data']
    out = out.reset_index()
    out['splined'] = out['extrapolated'] = 'uu'
    for j in range(len(out)) :
        out.set_value(j, 'splined', out.loc[j , 'data']['splined'])
        out.set_value(j, 'extrapolated', out.loc[j , 'data']['extrapol'])
    return out

bootstrapedsplined = boot_splines_to_dataframe(boot_splines , levels)

def get_spline_95IC(out_spline):
    """
    Function to get the 95 Confidence interval from splined age structure
    """
    ext5 = pd.DataFrame(list(out_spline['extrapolated'])).quantile(q=0.025, axis=0, numeric_only=True)
    ext95 = pd.DataFrame(list(out_spline['extrapolated'])).quantile(q=0.975, axis=0, numeric_only=True)
    spl5 = pd.DataFrame(list(out_spline['splined'])).quantile(q=0.025, axis=0, numeric_only=True)
    spl95 = pd.DataFrame(list(out_spline['splined'])).quantile(q=0.975, axis=0, numeric_only=True)
    return ([ext5 , ext95] , [spl5 , spl95])

#ICSplined = bootstraped_splines.groupby(levels).apply(get_spline_95IC)

####################
### Running all this

#age_structure = get_age_distribution(voters_data , level)
#boot_splines = voters_data.groupby(levels).apply(bootstrapedsplined)
#data_bootstrapped = boot_splines_to_dataframe(test)

### Computing IC95 for splined age structures
ICSplined = bootstrapedsplined.groupby(levels).apply(get_spline_95IC)
ICSplined = ICSplined.reset_index()
ICSplined.columns = levels + ['IC95']

out = {#'data_bootstrapped':data_bootstrapped ,
'confidence_intervals':ICSplined}# , 'age_structure':age_structure}

pickle.dump(out , open("data/processed/bootstraped_splines.p" , "wb"))
