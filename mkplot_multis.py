import numpy as np
import matplotlib.pyplot as plt
import matplotlib
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

unq = np.unique(name, return_counts=True)[1] > 1
mask = [n in np.unique(name)[unq] for n in name]

params = [name[mask], mass[mask], rad[mask], per[mask], teff[mask], letter[mask]]
param_names = ['Name', 'Mass', 'Radius', 'Period', 'Teff', 'Letter']
df = pd.DataFrame(np.asarray(params).T, columns=param_names)
