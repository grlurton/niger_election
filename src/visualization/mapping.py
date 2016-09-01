import numpy as np
from collections import OrderedDict
from bokeh.plotting import figure, show, output_notebook, ColumnDataSource, gridplot , output_file
from bokeh.models import HoverTool
from bokeh.io import vform
from bokeh.palettes import *

def make_map_data(carto_data , data , variable , palette) :
    n_colors = len(palette)
    regions_names = regions_ID = xs = ys  = values = cols = []
    for id in carto_data.keys() :
        regions_ID = regions_ID  + [id]
        regions_names = regions_names + [carto_data[id]['name']]
        xs = xs + [carto_data[id]['coordinates']['x']]
        ys = ys + [carto_data[id]['coordinates']['y']]
        if id in list(data.gps_ID) :
            values = values + [list(data.loc[data.gps_ID == id , variable])[0]]
        else :
            values = values + [ float('nan')]

    bins = np.linspace(min(values), max(values), n_colors)
    bine = np.digitize(values, bins) - 1
    for i in range(len(bine)) :
        cols = cols + [palette[bine[i]]]

    map_source = ColumnDataSource(
    data = dict(
        x=xs,
        y=ys,
        ID=regions_ID,
        name=regions_names ,
        values = values ,
        color = cols))

    return map_source


def univar_map(carto_data , data , variable , palette):
    map_source =  make_map_data(carto_data , data , variable , palette)
    p = figure(plot_width=700, plot_height=700,
           title="Registered voters by Commune" , title_text_font_size='12pt' ,
           tools='wheel_zoom,hover')
    p.patches('x', 'y',
          fill_color = "color" ,
          line_color="grey", line_width=0.5,
          source=map_source , legend = 'tool')
    hover = p.select(dict(type=HoverTool))
    hover.point_policy = "follow_mouse"
    hover.tooltips = OrderedDict([
        ("Nom", "@name") ,
        ("% Population registered" , "@values")])
    return p
