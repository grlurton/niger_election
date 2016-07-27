from sklearn import datasets
from sklearn.cross_validation import cross_val_predict
from sklearn import linear_model
from sklearn import preprocessing
from sklearn.feature_extraction import DictVectorizer

import matplotlib.pyplot as plt
import pandas as pd
import os as os
import numpy as np

from IPython.display import Markdown , Latex

os.chdir('c://users/grlurton/documents/niger_election_data')

data = pd.read_csv('data/processed/commune_collapsed_matched.csv')

regs = pd.get_dummies(data.region)

le = preprocessing.LabelEncoder()
le.fit(data.region)

lr = linear_model.LinearRegression()
y = np.asarray(data.population_census)

x_cat = data[['region']].T.to_dict().values()
v = DictVectorizer(sparse=False)
x_cat = v.fit_transform(x_cat)

x_train = np.hstack((data[['population_voting_list' , 'mean_age']] , x_cat ))


predicted = cross_val_predict(lr, x_train  , y, cv=100)

fig, ax = plt.subplots()
ax.scatter(y, predicted)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
ax.set_xlabel('Measured')
ax.set_ylabel('Predicted')
plt.show()
