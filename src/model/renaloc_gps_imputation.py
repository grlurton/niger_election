import pandas as pd

### Warnings management
import warnings
warnings.filterwarnings('ignore')

### Math libraries
import numpy as np
from math import radians, cos, sin, asin, sqrt

### Plotting libraries
import matplotlib.pyplot as plt

### Machine Learning libraries
from sklearn.tree import DecisionTreeRegressor
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction import DictVectorizer


### Load Data
data = pd.read_csv('../../data/external/gps_validation_set.csv' , encoding = "ISO-8859-1")

## Looking at distribution of things
def n_units(data):
    return data['ID'].nunique()

n_units(data)
data.groupby('region').apply(n_units)

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

dat_mod = make_validation_set(data , 40)

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

## Setting regressor
regressor = DecisionTreeRegressor(max_depth=500)
regressor.fit(X_train, y_train)

# Predict
predicted = regressor.predict(X_test)

def get_distances(y_test , X_test , predicted):
    dist_post_tree = []
    dist_pre_tree = []
    dist_from_renaloc = []

    for u in range(len(y_1)) :
        dist_post_tree = dist_post_tree + [haversine(y_test[u] , predicted[u])]
        dist_pre_tree = dist_pre_tree + [haversine(X_test[u] , y_test[u])]
        dist_from_renaloc = dist_from_renaloc + [haversine(X_test[u] , predicted[u])]

    dist_post_tree = pd.Series(dist_post_tree)
    dist_from_renaloc = pd.Series(dist_from_renaloc)
    dist_pre_tree = pd.Series(dist_pre_tree)

    return (dist_post_tree , dist_pre_tree , dist_from_renaloc)

dist_post_tree , dist_pre_tree , dist_from_renaloc = get_distances(y_test , X_test , predicted)

plt.scatter(dist_post_tree , dist_from_renaloc)
plt.xlabel('Distance to actual - post regression')
plt.ylabel('Distance moved by regression')
plt.show()

dist_post_tree = dist_post_tree[dist_from_renaloc < 40] ## Censurer les localities qui sont bougées de plus de 40 km
dist_pre_tree = dist_pre_tree[dist_from_renaloc < 40]
dist_from_renaloc = dist_from_renaloc[dist_from_renaloc < 40]

plt.scatter(dist_post_tree , dist_from_renaloc)
plt.xlabel('Distance to actual - post regression')
plt.ylabel('Distance moved by regression')
plt.show()


len(dist_post_tree)
len(dist_pre_tree)
len(dist_from_renaloc)

plt.hist(dist_post_tree , color = 'r' ,  bins=41)
plt.hist(dist_pre_tree , alpha = 0.5 , bins =41 , color = 'g')
plt.hist(dist_from_renaloc , alpha = 0.5 , bins =41 , color = 'b')
plt.show()

def prop_exact(dat , dist):
    return sum(pd.Series(dat) < dist) / len(dat)

prop_exact(dist_pre_tree , 10)
prop_exact(dist_post_tree , 10)

np.median(dist_pre_tree)
np.median(dist_post_tree)
