# -*- coding: utf-8 -*-

import pandas as pd
from shapely.geometry import Point, shape

from flask import Flask
from flask import render_template
import json


data_path = './input/'

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index2.html")

@app.route("/data")
def get_data():
    df = pd.read_csv(data_path  + 'data_for_viz.csv', encoding = "ISO-8859-1")
    col_names = ['n_population_2012','latitude','longitude','locality','n_population_2001','loc_type']
    new_df = df[col_names]
    new_df.loc[pd.isna(new_df['n_population_2012']),'n_population_2012'] = 0
#    df_clean = new_df.dropna()
    #df_clean = df_clean[0:1000]

    return new_df.to_json(orient='records')


if __name__ == "__main__":
    app.run(host='127.0.0.1',port=8000,debug=True, ssl_context='adhoc')
