from nldi_xstool.XSGen import XSGen
from nldi_xstool.ancillary import queryDEMsShape, getGageDatum
from nldi_xstool.nldi_xstool import getXSAtPoint, getXSAtEndPts
from shapely.geometry import LineString, Point
import py3dep
from pynhd import NLDI, NHDPlusHR, WaterData
import xarray as xr
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import dataretrieval.nwis as nwis
import requests
# import plotly.express as px
import folium
from folium import plugins
from cycler import cycler
from itertools import cycle

# Function to plot gage cross-section, measured cross-section, and threshold values
def plotGageXS_meas(index, gage_path, gage_thresholds, cross_sections, meas_xs, gage_datum, dem, dem_res, tindex):
    col_cycler = cycler(c=['r', 'g'])
    lw_cycler = cycler(lw=[1, 3])
    ls_cycler = cycler(ls=['-','-.'])
    
    style_cycler = col_cycler*lw_cycler*ls_cycler
    
    fig, ax = plt.subplots(1,2, figsize=(10,5))
    for ind, (k, v) in enumerate(gage_path.items()):
        if ind == index:
            res_list = []
            for dk, dv in dem_res[index].items():
                if dv == True:
                    res_list.append(f'{dk}:{dv}')
            print(f"Available Resolution: {', '.join(res_list)}")
            name=v['name']
            
            cross_sections[index].plot.line(x='distance', y='elevation', ax=ax[0])
            
            
            dem[index].plot(ax=ax[1])
            cross_sections[index].plot(ax=ax[1], c='r')
            
    for ind, (k, v) in enumerate(gage_thresholds.items()):
        if ind == index:
            num_t = len(v['Thresholds'])
#             print(num_t)
            colors = plt.cm.YlOrRd(np.linspace(0,1,num_t))
            for ind2, ((thresh_k, thresh_v), style) in enumerate(zip(v['Thresholds'].items(), cycle(style_cycler))):
#                 print(ind2)
                if ind2 in tindex:
                    ax[0].axhline(y=(thresh_v['Value']*.3048)+gage_datum[index], 
                               label=thresh_v['Name'], 
                               **style)
    meas_xs.plot.line(x='station', y='measured_elevation_m', ax=ax[0], c='black')            
    ax[0].legend(bbox_to_anchor=(0.6, -0.15))
    ax[0].set_ylabel('Elevation (m)')
    ax[0].set_xlabel('Distance from left bank (m)')                
#     ax[1].set_aspect('image')
#     ax[0].set_aspect('image')
    plt.title(f'USGS Gage {k}:{name}', y= 1.1)
#     plt.tight_layout()


# Function to plot gage cross-section and threshold values
def plotGageXS(index, gage_path, gage_thresholds, cross_sections, gage_datum, dem, dem_res):
    colors=['r', 'g', 'b', 'm', 'y', 'c']
    fig, ax = plt.subplots(1,2, figsize=(10,5))
    for ind, (k, v) in enumerate(gage_path.items()):
        if ind == index:
            res_list = []
            for dk, dv in dem_res[index].items():
                if dv == True:
                    res_list.append(f'{dk}:{dv}')
            print(f"Available Resolution: {', '.join(res_list)}")
            name=v['name']
            
            cross_sections[index].plot.line(x='distance', y='elevation', ax=ax[0])
            
            dem[index].plot(ax=ax[1])
            
            
    for ind, (k, v) in enumerate(gage_thresholds.items()):
        if ind == index:
            num_t = len(v['Thresholds'])
            print(num_t)
            colors = plt.cm.YlOrRd(np.linspace(0,1,num_t))
            for ind2, (thresh_k, thresh_v) in enumerate(v['Thresholds'].items()):
                print(ind2)
                ax[0].axhline(y=(thresh_v['Value']*.3048)+gage_datum[index], 
                           color=colors[ind2], 
                           linestyle='-', 
                           label=thresh_v['Name'])
                
    ax[0].legend(bbox_to_anchor=(0.6, -0.15))
    ax[0].set_ylabel('Elevation (m)')
    ax[0].set_xlabel('Distance from left bank (m)')                
#     ax[1].set_aspect('image')
#     ax[0].set_aspect('image')
    plt.title(f'USGS Gage {k}:{name}', y= 1.1)
#     plt.tight_layout()

def plotGageLocation(index, gage_location, gage_path, gage_thresholds, cross_sections):
    gage_loc = [gage_location[index].geometry.y[0], gage_location[index].geometry.x[0]]
#     print(gage_loc)
#     xs_geojson = cross_sections[index].to_json()
#     xs_gj = folium.GeoJson(xs_geojson, name='cross-section')
    linestr = []
    for tind, row in cross_sections[index].iterrows():
        x = row.geometry.x
        y = row.geometry.y
        linestr.append([y,x])


    m = folium.Map(location=gage_loc, zoom_start=100)
    folium.Marker(location=gage_loc, 
                  name=f'USGS gage-{tuple(gage_path.keys())[0]}', 
                  popup=f'USGS gage-{tuple(gage_path.keys())[0]}',
                  tooltip=f'USGS gage-{tuple(gage_path.keys())[0]}'
                 ).add_to(m)
    
    for ind, (k,v) in enumerate(gage_thresholds.items()):
#         print(ind)
        if ind == index:
            for ind2, (thresh_k, thresh_v) in enumerate(v['Thresholds'].items()):
                m_loc = [thresh_v['lat'], thresh_v['lon']]
#                 print(m_loc)
                folium.Marker(location=m_loc, 
                              name=thresh_v['Name'], 
                              popup=thresh_v['Name'],
                              tooltip=thresh_v['Name']).add_to(m)
        
    # With some work the cross-section plot above could be put into a popup
    # see: https://python-visualization.github.io/folium/quickstart.html#Vincent/Vega-and-Altair/VegaLite-Markers
    # see: https://altair-viz.github.io/
    # see: https://github.com/wrobstory/vincent
    
    folium.vector_layers.PolyLine(linestr, popup='Gage Cross-section',
                                  tooltip='Gage Cross-section',
                                  color='blue',
                                  weight=10).add_to(m)

    folium.LayerControl().add_to(m)
    plugins.MousePosition().add_to(m)
    return m

def interpTValues(gage_path, gage_thresholds, gage_datum_m, dem):
    interp_v = []
    absTValue = []
    headers = ['Gage', 'Gage Name', 'Threshold Name', 'Threshold Value', 'DEM Interpolated Value', 'Difference']
    for index, (k,v) in enumerate(gage_thresholds.items()):
        for ind2, (thresh_k, thresh_v) in enumerate(v['Thresholds'].items()):
            absTValue = gage_datum_m[index] + thresh_v['Value']*.3048
            intv = dem[index].interp(x= thresh_v['lon'], y=thresh_v['lat'])
            if index == 0 and ind2 == 0:
                print(', '.join(headers))
            gage_name = list(gage_path.values())[index]['name'].replace(',', ' ')
            t_name = thresh_v['Name']
            print(f'{k}, ', \
                  f'{gage_name}, ', \
                  f'{t_name}, ', \
                  f'{absTValue}, ', \
                  f'{intv.values}, ', \
                  f'{absTValue-intv.values}')
            