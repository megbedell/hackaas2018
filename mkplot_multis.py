import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from tqdm import tqdm
import os
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from bokeh.plotting import *
from bokeh.models import OpenURL, Circle, HoverTool, PanTool, BoxZoomTool, ResetTool, SaveTool, TapTool, WheelZoomTool
#from bokeh.models import *

import pandas as pd

from PyAstronomy import pyasl

if not os.path.isfile('multiples.csv'):
    nexa = pyasl.NasaExoplanetArchive()

    name = nexa.data['pl_hostname'].astype(str)
    mass = nexa.data['pl_massj'].astype(float)
    rad = nexa.data['pl_radj'].astype(float)
    per = nexa.data['pl_orbper'].astype(float)
    teff = nexa.data['st_teff'].astype(float)
    letter = nexa.data['pl_letter'].astype(str)
    st_rad = nexa.data['st_rad'].astype(float)

    unq = np.unique(name, return_counts=True)[1] > 1
    mask = [n in np.unique(name)[unq] for n in name]

    params = [name[mask], mass[mask], rad[mask], per[mask], teff[mask], st_rad[mask], letter[mask]]
    param_names = ['Name', 'Mass', 'Radius', 'Period', 'StTeff', 'StRadius', 'Letter']


    df = pd.DataFrame()
    for param, param_name in zip(params, param_names):
        df[param_name] = param
    #Drop any NaN radius value planets
    df = df.dropna(axis=0, subset=['Radius','Period']).reset_index(drop=True)

    df['PeriodRatio'] = 0
    unique_names = df.Name.unique()
    for unq in tqdm(unique_names):
        pos = df.Name == unq
        df = df.set_value(pos, 'PeriodRatio', (df[pos].Period/np.nanmin(df[pos].Period)))

    df['StarInt'] = 0
    for idx, n in enumerate(tqdm(unique_names)):
        df = df.set_value(df.Name == n, 'StarInt', idx)



    df.to_csv('multiples.csv', index=False)

else:
    df = pd.read_csv('multiples.csv')
# start plotting in bokeh:

output_file("multis.html")

df = df.sort_values('StRadius')
unique_names = df.Name.unique()

df['StarInt'] = 0
for idx, n in enumerate(tqdm(unique_names)):
    df = df.set_value(df.Name == n, 'StarInt', idx)

source = ColumnDataSource(data=dict(
                            Name=df.Name,
                            StarInt=df.StarInt,
                            StTeff=df.StTeff,
                            StRadius=df.StRadius,
                            Radius=df.Radius*10,
                            Letter=df.Letter,
                            PeriodRatio=df.PeriodRatio,
                            Period=df.Period,
                            )
                          )

fig = figure(tools="pan,wheel_zoom,box_zoom,reset", x_range=[-0.5, 50.0], active_scroll="wheel_zoom")

pl_render = fig.circle('PeriodRatio','StarInt', source=source, size='Radius', name='planets', alpha=0.7)
hover = HoverTool(renderers=[pl_render],
tooltips=[
        ("system", "@Name @Letter"),
        ("period", "@Period{1.11} days")
        ]
    )

p = np.unique(df.Name, return_index=True)[1]
st_source = ColumnDataSource(data=dict(
                            Name=df.Name[p],
                            StarInt=df.StarInt[p],
                            StTeff=df.StTeff[p],
                            StRadius=df.StRadius[p]*10,
                            )
                          )
st_render = fig.circle(0,'StarInt', source=st_source, size='StRadius', name='planets', alpha=0.7, color='StTeff')

#fig.add_tools(hover)
show(fig)
