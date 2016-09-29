import pandas as pd

### Math libraries
import numpy as np
from math import radians, cos, sin, asin, sqrt

### Plotting libraries
import matplotlib.pyplot as plt

### Machine Learning libraries
from sklearn.tree import DecisionTreeRegressor
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import AdaBoostRegressor

### Load Data
data = pd.read_csv('../../data/external/gps_validation_set.csv' , encoding = "ISO-8859-1")

## Facility to compute distance
def haversine(gps1,gps2):
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

## For localities with multiple matches, only keep closest matches
def keep_min_distance(data) :
    uni_data = data[data['dist_validation'] == min(data['dist_validation'])].iloc[0]
    del uni_data['ID']
    return uni_data

def keep_unique_loc(data):
    uni_data = data.iloc[0]
    return uni_data

## Keep only unique IDs and only one facility by GPS + only in clean of validation with
def make_validation_set(data , radius):
    uni_data = data.groupby('ID').apply(keep_min_distance)
    uni_data = uni_data.reset_index()
    uni_data = uni_data.groupby(['long','lat']).apply(keep_unique_loc)
    dat_mod = uni_data[(uni_data.dist_validation < radius)]
    return dat_mod

dat_mod = make_validation_set(data , 30)
dat_mod = dat_mod[['departement' , 'lat' , 'long' , 'region' , 'renaloc_latitude' , 'renaloc_longitude']]

## Format validation set for scikit-learn use
def make_sckikit_set(dat_mod):
    y = []
    dic = []
    for i in range(len(dat_mod)) :
        dic = dic + [{'latitude':dat_mod.renaloc_latitude.iloc[i] , 'longitude':dat_mod.renaloc_longitude.iloc[i] ,  'region':dat_mod.region.iloc[i] }]
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

def regressor_distance_median(i):
    print(i)
    ABreg = get_regressor_distance(AdaBoostRegressor(DecisionTreeRegressor(max_depth=200),
                              n_estimators=500 , learning_rate= i/1000) , X_train , y_train , X_test , y_test ,
                              multi_y = False )
    GBreg = get_regressor_distance(GradientBoostingRegressor(n_estimators=i, learning_rate=i/1000,
                            max_depth=500 , random_state=0, loss='huber'),
                            X_train , y_train , X_test , y_test ,
                            multi_y = False )
    DTreg = get_regressor_distance(DecisionTreeRegressor(max_depth=i),
                        X_train , y_train , X_test , y_test ,
                        multi_y = True )
    BRreg = get_regressor_distance(linear_model.BayesianRidge(),
                        X_train , y_train , X_test , y_test ,
                        multi_y = False )
    LAreg = get_regressor_distance(linear_model.Lasso(alpha=i/1000),
                        X_train , y_train , X_test , y_test ,
                        multi_y = False )
    Rreg = get_regressor_distance(linear_model.Ridge (alpha = i/1000),
                        X_train , y_train , X_test , y_test ,
                        multi_y = False )
    med_out = [i , np.median(ABreg.dist_post) , np.median(GBreg.dist_post) , np.median(DTreg.dist_post) ,
                        np.median(BRreg.dist_post) , np.median(LAreg.dist_post) , np.median(Rreg.dist_post)]
    return med_out

n_processes = os.cpu_count()
threadPool = ThreadPool(n_processes)
extracted_validation = threadPool.map(regressor_distance_median , list(range(10, 1000 , 50)))

out = pd.DataFrame(extracted_validation)
out.columns = list(['depth' , 'AdaBoosted' , 'GradientBoosted' , 'Regression_Tree' , 'BayesRidge', 'Lasso' ,
                    'Ridge_regression'])

plt.scatter(out.depth , out.AdaBoosted , c = 'b' )
plt.scatter(out.depth , out.GradientBoosted , c = 'r' )
plt.scatter(out.depth , out.Regression_Tree , c = 'g' )
plt.scatter(out.depth , out.BayesRidge , c = 'y' )
plt.scatter(out.depth , out.Lasso , c = 'grey' )
plt.scatter(out.depth , out.Ridge_regression , c = 'black' )
plt.xlabel('Depth of tree')
plt.ylabel('Distance to actual')
plt.show()

plt.scatter(dist_post_tree , dist_from_renaloc)
plt.xlabel('Distance to actual - post regression')
plt.ylabel('Distance moved by regression')
plt.show()

plt.scatter(dist_post_tree , dist_from_renaloc)
plt.xlabel('Distance to actual - post regression')
plt.ylabel('Distance moved by regression')
plt.show()

plt.hist(dist_post_tree , color = 'r' ,  bins=41)
plt.hist(dist_pre_tree , alpha = 0.5 , bins =41 , color = 'g')
plt.hist(dist_from_renaloc , alpha = 0.5 , bins =41 , color = 'b')
plt.show()
