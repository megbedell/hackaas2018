import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from tqdm import tqdm
import os
import astropy.units as u
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from bokeh.plotting import *
from bokeh.models import OpenURL, Circle, HoverTool, PanTool, BoxZoomTool, ResetTool, SaveTool, TapTool, WheelZoomTool, ColorBar
from bokeh.models import ColorMapper
#from bokeh.models import *

import pandas as pd

from PyAstronomy import pyasl

if not os.path.isfile('multiples.csv'):
    nexa = pyasl.NasaExoplanetArchive()

    name = nexa.data['pl_hostname'].astype(str)
    mass = nexa.data['pl_massj'].astype(float)
    rad = nexa.data['pl_radj'].astype(float)
    per = nexa.data['pl_orbper'].astype(float)
    smax = nexa.data['pl_orbsmax'].astype(float)
    teff = nexa.data['st_teff'].astype(float)
    letter = nexa.data['pl_letter'].astype(str)
    st_rad = nexa.data['st_rad'].astype(float)
    st_mass = nexa.data['st_mass'].astype(float)

    unq = np.unique(name, return_counts=True)[1] > 1
    mask = [n in np.unique(name)[unq] for n in name]

    params = [name[mask], mass[mask], rad[mask], per[mask], smax[mask], teff[mask], st_rad[mask], st_mass[mask], letter[mask]]
    param_names = ['Name', 'Mass', 'Radius', 'Period', 'Sep', 'StTeff', 'StRadius', 'StMass', 'Letter']

    df = pd.DataFrame()
    for param, param_name in zip(params, param_names):
        df[param_name] = param
    #Drop any NaN radius value planets
    df = df.dropna(axis=0, how='any', subset=['Radius','Period','StRadius','StTeff']).reset_index(drop=True)

    df['PeriodRatio'] = 0
    unique_names = df.Name.unique()
    for unq in tqdm(unique_names):
        pos = df.Name == unq
        df = df.set_value(pos, 'PeriodRatio', (df[pos].Period/np.nanmin(df[pos].Period)))

    df['StarInt'] = 0
    for idx, n in enumerate(tqdm(unique_names)):
        df = df.set_value(df.Name == n, 'StarInt', idx)

    sep = np.asarray(df.Sep)*u.AU
    rstar = (np.asarray(df.StRadius)*u.solRad).to(u.AU)
    temp = np.asarray(df.StTeff)*u.K
    df['Teq'] = (temp*np.sqrt(rstar/(2*sep)))

    m = (np.asarray(df.Mass)*u.jupiterMass).to(u.g)
    v = (4./3)*np.pi*((np.asarray(df.Radius)*u.jupiterRad).to(u.cm))**3
    df['Rho'] = (m/v).value

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
df = df.reset_index(drop=True)
opacity=df.Rho * 0.1 + 0.5
opacity[np.isnan(df.Rho)]=0.5

cmap = mpl.cm.get_cmap(name='RdBu_r')
norm = mpl.colors.Normalize(vmin=173,vmax=373)
colors = norm(df.Teq)
colors = np.asarray([mpl.colors.rgb2hex(cmap(c)) for c in colors])
colors[np.isnan(df.Teq)] = '#000000'

source = ColumnDataSource(data=dict(
                            Name=df.Name,
                            StarInt=df.StarInt,
                            StTeff=df.StTeff,
                            StRadius=df.StRadius,
                            Radius=df.Radius,
                            Letter=df.Letter,
                            PeriodRatio=df.PeriodRatio,
                            Period=df.Period,
                            Density=df.Rho,
                            Mass=df.Mass,
                            Teq=df.Teq,
                            opacity=opacity,
                            size=df.Radius*0.5,
                            color=colors
                            )
                          )
fig = figure(tools="pan,wheel_zoom,box_zoom,reset", x_range=[-0.5, 50.0], active_scroll="wheel_zoom", title='Multiplanet Systems')
fig.yaxis.visible = False
fig.xaxis.axis_label = "Period [days]"


pl_render = fig.circle('Period','StarInt', source=source, radius='size', name='planets', alpha='opacity', color='color', line_color='black')
hover = HoverTool(renderers=[pl_render],
tooltips=[
        ("System", "@Name @Letter"),
        ("Period", "@Period{1.11} days"),
        ("Mass", "@Mass{1.11} MJup"),
        ("Radius", "@Radius{1.11} RJup"),
        ("Temperature", "@Teq{1.0} K"),
        ("Density", "@Density{1.0} g/cm^3")
        ]
    )
fig.add_tools(hover)

p = np.unique(df.StarInt, return_index=True)[1]
cmap = mpl.cm.get_cmap(name='RdYlBu')
norm = mpl.colors.Normalize(vmin=3000,vmax=10000)
colors = norm(df.StTeff)
colors = np.asarray([mpl.colors.rgb2hex(cmap(c)) for c in colors])
st_source = ColumnDataSource(data=dict(
                            Name=df.Name[p],
                            StarInt=df.StarInt[p],
                            StTeff=df.StTeff[p],
                            size=df.StRadius[p]*0.05,
                            StRadius=df.StRadius[p],
                            StMass=df.StMass[p],
                            color=colors[p]
                            )
                          )
st_render = fig.circle(0,'StarInt', source=st_source, radius='size', name='stars', alpha=0.7, color='color')
st_hover = HoverTool(renderers=[st_render],
tooltips=[
        ("Star", "@Name"),
        ("Temp", "@StTeff{1.0} K"),
        ("Mass", "@StMass{1.0} SolarMasses"),
        ("Radius", "@StRadius{1.0} SolarRadii"),
            ]
    )
fig.add_tools(st_hover)

show(fig)
