import pandas as pd
import warnings
warnings.filterwarnings('ignore')

data = pd.read_csv('../../data/external/gps_validation_set.csv' , encoding = "ISO-8859-1")
del data['Unnamed: 0']


## Looking at distribution of things
def n_units(data):
    return data['ID'].nunique()

data.groupby('region').apply(n_units)
n_units(data)

## Get distance between original and validation sets

for i in range(len(data)):
    dist_i = haversine(data.long.iloc[i] , data.lat.iloc[i] , data.renaloc_longitude.iloc[i] , data.renaloc_latitude.iloc[i])
    data.loc[i , 'dist_validation'] = dist_i

    data.loc[i ,  'in_departement'] = data.loc[i , 'departement'] in data.loc[i , 'osm_is_in']

def N_dept(data):
    return data.in_departement.value_counts()

data.groupby('region').apply(N_dept)




### For now I'll take data that is less than 40 km from its original
### Idea : experiment with area to improve exclusion rule

## match with renaloc
## ML for correction

import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor

from sklearn.cross_validation import train_test_split

from sklearn import preprocessing
enc = preprocessing.OneHotEncoder()




def keep_min_distance(data) :
    return data[data['dist_validation'] == min(data['dist_validation'])]

uni_data = data.groupby('ID').apply(keep_min_distance)
del uni_data['ID']
uni_data = uni_data.reset_index()

from ggplot import *
ggplot(aes(x = 'dist_validation' , fill = 'in_departement') , data = uni_data[uni_data.dist_validation < 40]) + \
    geom_histogram(binwidth=5) +\
    scale_color_brewer(type='qual')+ \
    facet_wrap('region' , scales = "free_y")

dat_mod = uni_data[(uni_data.in_departement == True) & (uni_data.dist_validation < 40)]

y = []
dic = []
for i in range(len(dat_mod)) :
    print(i)
    dic = dic + [{'latitude':dat_mod.renaloc_latitude.iloc[i] , 'longitude':dat_mod.renaloc_longitude.iloc[i] ,  'region':dat_mod.region.iloc[i]}]
    y = y + [[dat_mod.lat.iloc[i] , dat_mod.long.iloc[i]]]

from sklearn.feature_extraction import DictVectorizer
vec = DictVectorizer()
X = vec.fit_transform(dic).toarray()
y = np.array(y)

len(y)

X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.33)

regr_1 = DecisionTreeRegressor(max_depth=(500))
regr_1.fit(X_train, y_train)

# Predict
y_1 = regr_1.predict(X_test)

out = []
comp = []

for u in range(len(y_1)) :
    print(u)
    out = out + [haversine(y_test[u] , y_1[u])]
    comp = comp + list(dat_mod.dist_validation[(dat_mod.renaloc_latitude == X_test[u,0]) & (dat_mod.renaloc_longitude ==
    X_test[u,1])])
    print(len(comp))

dat_mod.head()


len(comp)
len(out)

plt.hist(out , color = 'r' , normed=True , bins=20)
plt.hist(comp , alpha = 0.5 , normed=True , bins =20 , color = 'g')
plt.show()

np.median(comp)
np.median(out)


dat_mod.head()
