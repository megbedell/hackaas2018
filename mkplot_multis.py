import numpy as np
import matplotlib.pyplot as plt
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
