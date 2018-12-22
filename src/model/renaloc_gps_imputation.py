import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import AdaBoostRegressor


%matplotlib inline

# Load Data
data = pd.read_csv('~/data/niger_election_data/external/gps_validation_set.csv',
                   encoding="ISO-8859-1")


# Facility to compute distance
def haversine(gps1, gps2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1 = gps1[0]
    lat1 = gps1[1]
    lon2 = gps2[0]
    lat2 = gps2[1]
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


# For localities with multiple matches, only keep closest matches
def keep_min_distance(data):
    uni_data = data[data['dist_validation'] == min(data['dist_validation'])].iloc[0]
    del uni_data['ID']
    return uni_data


def keep_unique_loc(data):
    uni_data = data.iloc[0]
    return uni_data


def keep_non_rounded(data):
    long_multip = list(data.long.value_counts()[data.long.value_counts() == 1].index)
    lat_multip = list(data.lat.value_counts()[data.lat.value_counts() == 1].index)
    uni_data = data[(data.long.isin(long_multip)) & (data.lat.isin(lat_multip))]
    return uni_data


# Keep only unique IDs and only one facility by GPS + only in clean of validation with
def make_validation_set(data, error_guess, radius):
    uni_data = data.groupby('ID').apply(keep_min_distance)
    uni_data = uni_data.reset_index()
    uni_data = uni_data.groupby(['long', 'lat']).apply(keep_unique_loc)
    uni_data = keep_non_rounded(uni_data)
    dat_mod = uni_data[((uni_data.dist_validation < (error_guess + radius)) &
                        (uni_data.dist_validation > (error_guess - radius)))]
    return dat_mod


dat_mod = make_validation_set(data, 25, 5)
len(dat_mod)

dat_mod = dat_mod[['departement', 'lat', 'long', 'region', 'renaloc_latitude',
                   'renaloc_longitude']]


# Format validation set for scikit-learn use
def make_sckikit_set(dat_mod):
    y = []
    dic = []
    for i in range(len(dat_mod)):
        dic = dic + [{'latitude':dat_mod.renaloc_latitude.iloc[i] , 'longitude':dat_mod.renaloc_longitude.iloc[i] ,  'region':dat_mod.region.iloc[i] , 'departement':dat_mod.departement.iloc[i] }]
        y = y + [[dat_mod.lat.iloc[i] , dat_mod.long.iloc[i]]]

    vec = DictVectorizer()
    X = vec.fit_transform(dic).toarray()
    y = np.array(y)
    return (X , y)

X , y =  make_sckikit_set(dat_mod)

## Get Training and Testing sets
X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.33)


## Setting regressors

### Regression Tree
DTregressor = DecisionTreeRegressor(max_depth=8)
DTpredicted = DTregressor.fit(X_train , y_train).predict(X_test)

def complete_predicted(predicted_long , predicted_lat) :
    predicted = []
    for i in range(len(predicted_long)):
        predicted = predicted + [[predicted_long[i] , predicted_lat[i]]]
    predicted = np.asarray(predicted)
    return predicted

### Boosted Regression Tree
GBregressor = GradientBoostingRegressor(n_estimators=8, learning_rate=0.4,
  max_depth=100, random_state=0, loss='huber')
GBpredicted_long = GBregressor.fit(X_train, y_train[: ,0]).predict(X_test)
GBpredicted_lat = GBregressor.fit(X_train, y_train[: ,1]).predict(X_test)

GBpredicted = complete_predicted(GBpredicted_long , GBpredicted_lat)

### AdaBoost Regressor
ABregressor = AdaBoostRegressor(DecisionTreeRegressor(max_depth=500),
                          n_estimators=500)
ABpredict_long = ABregressor.fit(X_train , y_train[: ,0]).predict(X_test)
ABpredict_lat = ABregressor.fit(X_train , y_train[: ,1]).predict(X_test)

ABpredicted = complete_predicted(ABpredict_long , ABpredict_lat)

## Linear Regressor
from sklearn import linear_model

### Bayesian Ridge
BRpredict_long = linear_model.BayesianRidge().fit(X_train , y_train[: ,0]).predict (X_test)
BRpredict_lat = linear_model.BayesianRidge().fit(X_train , y_train[: ,1]).predict (X_test)

### LASSO
LApredict_long = linear_model.Lasso(alpha=.1).fit(X_train , y_train[: ,0]).predict (X_test)
LApredict_lat = linear_model.Lasso(alpha=.1).fit(X_train , y_train[: ,1]).predict (X_test)

## SVM
from sklearn import svm




### Models evaluation
def get_distances(y_test , X_test , predicted):
    dist_post_tree = []
    dist_pre_tree = []
    dist_from_renaloc = []

    for u in range(len(y_test)) :
        dist_post_tree = dist_post_tree + [haversine(y_test[u] , predicted[u])]
        dist_pre_tree = dist_pre_tree + [haversine(X_test[u] , y_test[u])]
        dist_from_renaloc = dist_from_renaloc + [haversine(X_test[u] , predicted[u])]

    dist_post_tree = pd.Series(dist_post_tree)
    dist_from_renaloc = pd.Series(dist_from_renaloc)
    dist_pre_tree = pd.Series(dist_pre_tree)

    return (dist_post_tree , dist_pre_tree , dist_from_renaloc)

def get_regressor_distance(regressor , X_train , y_train , X_test , y_test , multi_y):
    if multi_y == True :
        predicted = regressor.fit(X_train , y_train).predict(X_test)
    if multi_y == False :
        predicted_long = regressor.fit(X_train , y_train[: ,0]).predict(X_test)
        predicted_lat = regressor.fit(X_train , y_train[: ,1]).predict(X_test)
        predicted = complete_predicted(predicted_long , predicted_lat)
    dist_post_tree , dist_pre_tree , dist_from_renaloc = get_distances(y_test , X_test , predicted)
    ## Censurer les localities qui sont bougées de plus de 40 km
    dist_post_tree = dist_post_tree[dist_from_renaloc < 40]
    dist_pre_tree = dist_pre_tree[dist_from_renaloc < 40]
    dist_from_renaloc = dist_from_renaloc[dist_from_renaloc < 40]
    out = {"dist_pre":dist_pre_tree , "dist_post":dist_post_tree ,
            "moved_distance":dist_from_renaloc}
    return pd.DataFrame(out)



import os
from multiprocessing.pool import ThreadPool
from sklearn.kernel_ridge import KernelRidge
from sklearn.neural_network import MLPRegressor

def regressor_distance_median(i):
    print(i)
    ABreg = get_regressor_distance(AdaBoostRegressor(DecisionTreeRegressor(max_depth=200),
                              n_estimators=500 , learning_rate= i/1000) , X_train , y_train , X_test , y_test ,
                              multi_y = False )
    GBreg = get_regressor_distance(GradientBoostingRegressor(n_estimators=i, learning_rate=0.2,
                            max_depth=500 , random_state=0, loss='huber'),
                            X_train , y_train , X_test , y_test ,
                            multi_y = False )
    DTreg = get_regressor_distance(DecisionTreeRegressor(max_depth=i),
                        X_train , y_train , X_test , y_test ,
                        multi_y = True )
    BRreg = get_regressor_distance(linear_model.BayesianRidge(),
                        X_train , y_train , X_test , y_test ,
                        multi_y = False )
    LAreg = get_regressor_distance(linear_model.Lasso(alpha=0.05),
                        X_train , y_train , X_test , y_test ,
                        multi_y = False )
    Rreg = get_regressor_distance(linear_model.Ridge (alpha = i/1000),
                        X_train , y_train , X_test , y_test ,
                        multi_y = False )
    SVMreg = get_regressor_distance(svm.SVR(),
                        X_train , y_train , X_test , y_test ,
                        multi_y = False )
    ENreg = get_regressor_distance(linear_model.ElasticNet(alpha = 0.05),
                        X_train , y_train , X_test , y_test ,
                        multi_y = False )
    KRreg = get_regressor_distance(KernelRidge(kernel='rbf', gamma=i/1000),
                        X_train , y_train , X_test , y_test ,
                        multi_y = False )
    OLSreg = get_regressor_distance(linear_model.LinearRegression(),
                        X_train , y_train , X_test , y_test ,
                        multi_y = False )
    MLPreg = get_regressor_distance(MLPRegressor(alpha=i / 10000),
                        X_train , y_train , X_test , y_test ,
                        multi_y = False )

    dat_out = {'ABreg':ABreg , 'GBreg':GBreg , 'DTreg':DTreg , 'BRreg':BRreg , 'LAreg':LAreg , 'Rreg':Rreg ,
                'SVMreg':SVMreg , 'ENreg':ENreg , 'KRreg':KRreg , 'OLSreg':OLSreg , 'MLPreg':MLPreg}

    med_out = [i , np.median(ABreg.dist_post) , np.median(GBreg.dist_post) , np.median(DTreg.dist_post) ,
                        np.median(BRreg.dist_post) , np.median(LAreg.dist_post) , np.median(Rreg.dist_post) , np.median(SVMreg.dist_post) , np.median(ENreg.dist_post) , np.median(KRreg.dist_post) , np.median(OLSreg.dist_post) , np.median(MLPreg.dist_post)]
    return (med_out , dat_out)

n_processes = os.cpu_count()
threadPool = ThreadPool(n_processes)
extracted_validation = threadPool.map(regressor_distance_median , list(range(10, 1000 , 50)))

meds = [extr[0] for extr in extracted_validation]
out = pd.DataFrame(meds)
out.columns = list(['depth' , 'AdaBoosted' , 'GradientBoosted' , 'Regression_Tree' , 'BayesRidge', 'Lasso' ,
                    'Ridge_regression' , 'SVM' , 'ElasticNet' , 'KernelRidge' , 'OLS' , 'MLP'])
out.head()


plt.figure(figsize=(20,10))
#plt.scatter(out.depth , out.AdaBoosted , c = 'b' , s= 50 )
#plt.scatter(out.depth , out.GradientBoosted , c = 'r' , s= 50 )

#plt.scatter(out.depth , out.BayesRidge , c = 'y' , s= 50 )
#plt.scatter(out.depth , out.Lasso , c = 'k' , s= 50 )
plt.scatter(out.depth , out.Ridge_regression , c = 'c' , s= 50 )
plt.scatter(out.depth , out.MLP , c = 'm', s= 50 )
plt.scatter(out.depth , out.OLS , c = 'g' , s= 50 )
#plt.xlabel('Depth of tree')
#plt.ylabel('Distance to actual')
plt.show()

for_hist = extracted_validation[1][1]
nrows = 4
ncols = 3
fig, axarr = plt.subplots(nrows=nrows,ncols=ncols,figsize=(20,10))
col = row = 0
for dat in for_hist :
    to_plot = for_hist[dat]
    perc_under_5 = np.round(sum(to_plot.dist_post < 5) / len(to_plot) , decimals = 3)
    axarr[row , col].hist(to_plot.dist_post , color = 'b' ,  bins=30)
    axarr[row , col].hist(to_plot.dist_pre , color = 'r' ,  bins=30 , alpha = 0.5)
    axarr[row , col].text(25, 20, perc_under_5 , fontsize=15)
    axarr[row , col].set_xlim([0,30])
    axarr[row , col].set_ylim([0,30])
    axarr[row , col].set_title(dat)
    col = col + 1
    if col > (ncols - 1) :
        col = 0
        row = row + 1



for_hist = extracted_validation[1][1]
nrows = 4
ncols = 3
fig, axarr = plt.subplots(nrows=nrows,ncols=ncols,figsize=(20,10))
col = row = 0
for dat in for_hist :
    to_plot = for_hist[dat]
    axarr[row , col].scatter(to_plot.dist_pre , to_plot.dist_post , color = 'b')
    axarr[row , col].set_xlim([25,30])
    axarr[row , col].set_ylim([0,50])
    axarr[row , col].set_title(dat)
    col = col + 1
    if col > (ncols - 1) :
        col = 0
        row = row + 1

fig, axarr = plt.subplots(nrows=nrows,ncols=ncols,figsize=(20,10))
col = row = 0
for dat in for_hist :
    to_plot = for_hist[dat]
    dists = range(0,30)
    dist_perc = []
    for km in range(0,30):
        dist_perc.append(sum(to_plot.dist_post < km) / len(to_plot))
    axarr[row , col].plot(dists , dist_perc)
    axarr[row , col].set_title(dat)
    col = col + 1
    if col > (ncols - 1) :
        col = 0
        row = row + 1
