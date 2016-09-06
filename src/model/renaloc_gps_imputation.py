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

## Adding variable looling
data['in_departement'] = data.departement.isin(data['osm_is_in'])

## match with renaloc
## ML for correction
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

uni_data = data.groupby('ID').apply(keep_min_distance)
uni_data = uni_data.reset_index()

print(len(uni_data))

uni_data = uni_data.groupby(['long','lat']).apply(keep_unique_loc)
print(len(uni_data))


dat_mod = uni_data[(uni_data.dist_validation < 40)]

y = []
dic = []
for i in range(len(dat_mod)) :
    dic = dic + [{'latitude':dat_mod.renaloc_latitude.iloc[i] , 'longitude':dat_mod.renaloc_longitude.iloc[i] ,  'region':dat_mod.region.iloc[i] }]
    y = y + [[dat_mod.lat.iloc[i] , dat_mod.long.iloc[i]]]

vec = DictVectorizer()
X = vec.fit_transform(dic).toarray()
y = np.array(y)

X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.33)

regr_1 = DecisionTreeRegressor(max_depth=(300))
regr_1.fit(X_train, y_train)

# Predict
y_1 = regr_1.predict(X_test)

out = []
comp = []
for u in range(len(y_1)) :
    out = out + [haversine(y_test[u] , y_1[u])]
    comp = comp + list(dat_mod.dist_validation[(dat_mod.long == y_test[u,1]) & (dat_mod.lat ==
    y_test[u,0])])

dat_mod.head()

len(comp)
len(out)

comp

out = pd.Series(out)
out = out[out < 41]

plt.hist(out , color = 'r' ,  bins=41)

plt.hist(comp , alpha = 0.5 , bins =41 , color = 'g')
plt.show()

def prop_exact(dat , dist):
    return sum(pd.Series(dat) < dist) / len(dat)

prop_exact(out , 25)
prop_exact(comp , 25)

np.median(comp)
np.median(out)
