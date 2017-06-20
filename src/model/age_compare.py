import pandas as pd
import numpy as np

age_dist_census = pd.read_csv(
    '../../data/external/tabula-ETAT_STRUCTURE_POPULATION.csv')
age_dist_census = age_dist_census[~(age_dist_census.AGE == 'Total')]
age_dist_census = age_dist_census[~(age_dist_census.Region == 'Niger')]

age_dist_census_adults = age_dist_census[age_dist_census.AGE.astype(int) > 17]


voters_data = pd.read_csv(
    '../../data/processed/voters_list.csv', encoding="ISO-8859-1")
voters_data.region = voters_data.region.str.title()

voters_data.age = np.round(voters_data.age)
print(len(voters_data))
voters_data = voters_data[(voters_data.age < 99) & (voters_data.age > 17)]
voters_data = voters_data[~(voters_data.region == 'Diaspora')]
print(len(voters_data))

voters_data.region[voters_data.region == 'Tillaberi'] = 'Tillabery'


def census_sum_total(data_census):
    region = data_census.Region.unique()[0]
    n_total = sum(data_census.Total)
    out = data_census['Total'] / n_total
    age_str = data_census['AGE'].astype(str) + ' Ans'
    return pd.DataFrame({'region': region, 'percentage': out.tolist(), 'Age': age_str})

by_region_census_total = age_dist_census_adults.groupby(
    ['Region']).apply(census_sum_total)


def voters_age_distrib(data):
    """
    Function to get the distribution of voters by age in a dataset. Age is censored at 100.
    """
    data.age_str = data.age.astype(int).astype(str) + ' Ans'
    out = data.age_str.value_counts() / len(data)
    out = out.reset_index()
    out.columns = ['age', 'percentage']
    return out

by_region_voters_total = voters_data.groupby(
    'region').apply(voters_age_distrib).reset_index()
by_region_voters_total['source'] = 'Voters'
by_region_census_total['source'] = 'Census'

by_region_voters_total = by_region_voters_total.drop('level_1', 1)

by_region_voters_total.columns = ['region', 'age', 'percentage', 'source']
by_region_census_total.columns = ['age', 'percentage', 'region', 'source']

data = by_region_voters_total.append(by_region_census_total)

data = data.reset_index()

data['age_num'] = 0
for i in range(len(data)):
    data.loc[i, 'age_num'] = data.iloc[i]['age'][0:2]

data['age_num'] = data['age_num'].astype(int)

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid" , font_scale = 1.8)
%matplotlib inline

kws = dict(s=50, linewidth=.5, edgecolor="w")
g = sns.FacetGrid(data, col="region", col_wrap=3, size=5, aspect=.8, hue="source", palette="Set1", ylim=(-0.001, 0.08)
                  ).map(plt.scatter,  'age_num',  'percentage', **kws).set(xlabel='Age', ylabel='Age Distribution').add_legend()



g.savefig('../../reports/figures/age_structure_comparison.pdf', dpi=1200)
