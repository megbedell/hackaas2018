import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib 
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from bokeh.plotting import *
from bokeh.models import OpenURL, Circle, HoverTool, PanTool, BoxZoomTool, ResetTool, SaveTool, TapTool, WheelZoomTool
#from bokeh.models import *

import xml.etree.ElementTree as ET, urllib, gzip, io
url = "https://github.com/OpenExoplanetCatalogue/oec_gzip/raw/master/systems.xml.gz"
oec = ET.parse(gzip.GzipFile(fileobj=io.BytesIO(urllib.urlopen(url).read())))

# Output mass and radius of all planets 
mass = []
radius = []
name = []
mass_errm = []
mass_errp = []
radius_errm = []
radius_errp = []
for planet in oec.findall(".//planet[mass]"):
    try: # check that all error bars exist
        mem = planet.find("mass").attrib['errorminus']
        mep = planet.find("mass").attrib['errorplus']
        rem = planet.find("radius").attrib['errorminus']
        rep = planet.find("radius").attrib['errorplus']
    except: # if not, skip this planet
        continue
    if (planet.findtext("name") == 'Kepler-11 c'):
        # manually adjust mass errors
        mem = 2.9/317.83
        mep = 1.6/317.83
    # if yes, save its relevant stats
    mass =  np.append(mass, float(planet.findtext("mass")))
    radius = np.append(radius, float(planet.findtext("radius")))
    name = np.append(name, planet.findtext("name"))
    mass_errm = np.append(mass_errm, float(mem))
    mass_errp = np.append(mass_errp, float(mep))
    radius_errm = np.append(radius_errm, float(rem))
    radius_errp = np.append(radius_errp, float(rep))
    
np.savetxt('oec_mr.csv',np.transpose([name,mass,mass_errp,mass_errm,radius,radius_errp,radius_errm]), 
        header='Name, Mass (Jup), Mass error+, Mass error-, Radius (Jup), Radius err+, Radius err-',
        delimiter=',',fmt='%s')