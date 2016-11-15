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
    df = pd.read_csv(data_path  + 'data_for_viz.csv')
    col_names = ['population','latitude','longitude','locality']
    new_df = df[col_names]
    df_clean = new_df.dropna()
    df_clean = df_clean[0:1000]

    return df_clean.to_json(orient='records')


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8889,debug=True)
