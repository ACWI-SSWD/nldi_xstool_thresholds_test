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


# Function to plot gage cross-section and threshold values
def plot_gage_xs(index, gage_path, gage_thresholds, cross_sections, gage_datum, dem_res):
    colors=['r', 'g', 'b']
    fig, ax = plt.subplots()
    for ind, (k, v) in enumerate(gage_path.items()):
        if ind == index:
            print('Available DEM Resolution')
            for dk, dv in dem_res[index].items():
                if dv == True:
                    print(f'{dk}:{dv}')
            name=v['name']
            plt.title(f'USGS Gage {k}:{name}')
            cross_sections[index].plot.line(x='distance', y='elevation', ax=ax)

    for ind, (k, v) in enumerate(gage_thresholds.items()):
        if ind == index:
            for ind2, (thresh_k, thresh_v) in enumerate(v['Thresholds'].items()):

                ax.axhline(y=(thresh_v['Value']*.3048)+gage_datum[index], 
                           color=colors[ind2], 
                           linestyle='-', 
                           label=thresh_v['Name'])
                ax.legend(bbox_to_anchor=(0.6, -0.15))
                ax.set_ylabel('Elevation (m)')
                ax.set_xlabel('Distance from left bank (m)')

def plot_gage_location(index, gage_location, gage_path, gage_thresholds, cross_sections):
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