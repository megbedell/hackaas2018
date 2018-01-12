import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from tqdm import tqdm
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from bokeh.plotting import *
from bokeh.models import OpenURL, Circle, HoverTool, PanTool, BoxZoomTool, ResetTool, SaveTool, TapTool, WheelZoomTool
#from bokeh.models import *

import pandas as pd

from PyAstronomy import pyasl
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
df.dropna(axis=0, subset=['Radius']).reset_index(drop=True)

df['PeriodRatio'] = 0
unique_names = df.Name.unique()
for unq in tqdm(unique_names):
    pos = df.Name == unq
    df.loc[pos].PeriodRatio = (df[pos].Period/df[pos].Period.min())

df['StarInt'] = 0
for idx, n in enumerate(tqdm(unique_names)):
    df.StarInt[df.Name == n] = idx

df.to_csv('multiples.csv', index=False)

# start plotting in bokeh:

#output_file("multis.html")

source = ColumnDataSource(
data=dict(
        Name=df.Name,
        StarInt=df.StarInt,
        StTeff=df.StTeff,
        StRadius=df.StRadius,
        Radius=df.Radius,
        Letter=df.Letter,
        PeriodRatio=df.PeriodRatio,
        Period=df.Period
        )
    )
    
fig = figure(tools="pan,wheel_zoom,box_zoom,reset", x_range=[-0.5, 50.0], \
        y_range=[0.0,500.0], active_scroll="wheel_zoom") 
        
pl_render = fig.circle('PeriodRatio','StarInt', source=source, size=10, name='planets')
hover = HoverTool(renderers=[pl_render],
tooltips=[
        ("system", "@Name"),
        ("id", "@Letter"),
        ("period", "@Period{1.11} days")
        ]
    )
fig.add_tools(hover)

fig.show()

