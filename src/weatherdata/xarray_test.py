import numpy as np
import xarray as xr
import pandas as pd
from metpy.units import units
import matplotlib.pyplot as plt

from agroservices import IPM 

ipm = IPM()

def data(
    parameters=[1002,3002], 
    station_id=101104, 
    interval=3600,
    timeStart='2020-06-12',
    timeEnd='2020-07-03',
    timezone="UTC",
    altitude=70,
    longitude=14.3711,
    latitude=67.2828,
    ViewDataFrame=True):

    response=ipm.get_weatheradapter(
        endpoint='/weatheradapter/fmi/',
        credentials=None,
        weatherStationId=station_id, 
        timeStart=timeStart, 
        timeEnd=timeEnd, 
        interval=interval, 
        parameters=parameters
        )
            
    times = pd.date_range(
        start=response['timeStart'].split('T')[0], 
        end=response['timeEnd'].split('T')[0], 
        freq="H",
        name="time")

    parameter = response['weatherParameters']

    d_array = xr.DataArray(
        data=response['locationWeatherData'][0]['data'],
        coords={'time':times,
                'parameter':parameter,
                'latitude':response['locationWeatherData'][0]['latitude'],
                'longitude':response['locationWeatherData'][0]['longitude'],
                'altitude':response['locationWeatherData'][0]['altitude']},
        dims=['time','parameter']
        )

    ds=d_array.to_dataset("parameter")

    # add attribute
    ## coordinate attribute

    ds.coords['latitude'].attrs['name']='latitude'
    ds.coords['latitude'].attrs['unit']='degrees_north'

    ds.coords['longitude'].attrs['name']='longitude'
    ds.coords['longitude'].attrs['unit']='degrees_east'

    ds.coords['altitude'].attrs['name']='altitude'
    ds.coords['altitude'].attrs['unit']='meters'



    ## variable attribute
    param = ipm.get_parameter()
    p={str(item['id']): item for item in param if item['id'] in response['weatherParameters']}

    for el in list(ds.data_vars):
        ds.data_vars[el].attrs=p[str(el)]


    df = ds.to_dataframe()

    if (ViewDataFrame==True):
        return df
    else:
        return ds
