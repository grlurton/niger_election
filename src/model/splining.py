age_adulte = 19

age_adulte = 22

def spl_age(data):
    """
    Function to get spline of age from a distribution estimated with get_age_distribution
    """
    out = UnivariateSpline(data['age'] , data['percentage'] , k= 3)
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

def get_spline_from_sample(data):
    """
    Wrapper function to get age distribution, spline it and impute non adults from a given sample
    """
    sample = data.sample(frac = 1 , replace = True)
    age_dist = age_distrib(sample)
    splines = spl_age(age_dist)
    extrapolated_data = impute_non_adulte(splines)
    return extrapolated_data

<<<<<<< HEAD



=======
>>>>>>> cf0c17c8e6c292592f92bf653736da9af5440ae6
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

def age_distrib(data) :
    """
    Function to get the distribution of voters by age in a dataset. Age is censored at 100.
    """
    data.age[data.age > 100] = 100
    out =  np.round(data.age).value_counts() / len(data)
    out = out.reset_index()
    out.columns = ['age' , 'percentage']
    return out

import pandas as pd
import numpy as np
from scipy.interpolate import UnivariateSpline
import os
import pickle


from multiprocessing.pool import ThreadPool

voters_data = pd.read_csv('../../data/processed/voters_list.csv'  , encoding = "ISO-8859-1")
voters_data = voters_data[(voters_data.region != 'DIASPORA' ) & (voters_data.age >= age_adulte)]

####################
### Getting structure for complete data

levels= ['region' , 'departement' ,  'commune']
#levels = ['region' , 'departement']

age_structure = voters_data.groupby(levels).apply(age_distrib)
age_structure = age_structure.reset_index()
del age_structure['level_' + str(len(levels))]
age_structure.columns = levels + ['age' , 'percentage']

splined_data = boot_splines_to_dataframe(voters_data.groupby(levels).apply(get_spline_from_sample) , levels)


## Getting bootstrapped splines

n_processes = 2
n_replications = 50

threadPool = ThreadPool(n_processes)
boot_splines = threadPool.map(spline_on_level , list(range(n_replications)))

bootstrapedsplined = boot_splines_to_dataframe(boot_splines , levels)

def get_spline_95IC(out_spline):
    """
    Function to get the 95 Confidence interval from splined age structure
    """
    ext5 = pd.DataFrame(list(out_spline['extrapolated'])).quantile(q=0.025, axis=0, numeric_only=True)
    print(ext5)
    ext95 = pd.DataFrame(list(out_spline['extrapolated'])).quantile(q=0.975, axis=0, numeric_only=True)
    print(ext95)
    spl5 = pd.DataFrame(list(out_spline['splined'])).quantile(q=0.025, axis=0, numeric_only=True)
    spl95 = pd.DataFrame(list(out_spline['splined'])).quantile(q=0.975, axis=0, numeric_only=True)
    return {'extrapolation_5':ext5 , 'extrapolation_95':ext95 ,
            'splining_5':spl5 , 'splining_95':spl95}


### Computing IC95 for splined age structures
ICSplined = bootstrapedsplined.groupby(levels).apply(get_spline_95IC)
ICSplined = ICSplined.reset_index()
ICSplined.columns = levels + ['IC95']

out = {'splined_data':splined_data , 'confidence_intervals':ICSplined , 'age_structure':age_structure}

pickle.dump(out , open("../../data/processed/bootstraped_splines.p" , "wb"))
