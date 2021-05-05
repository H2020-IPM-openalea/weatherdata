# -*- python -*-
# -*- coding:utf-8 -*-
#
#       Copyright 2020 INRAE-CIRAD
#       Distributed under the Cecill-C License.
#       See https://cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import pandas
import datetime
import xarray as xr
import numpy as np

from agroservices import IPM

class WeatherDataSource(object):
    ''' 
    Allows to query weather data resource for a given date range and return
    meteorological data in the form of a Python data structure that keeps tracks
    of location and units.

    ..doctest::
        >>> ws = WeatherDataSource(name='Finnish Meteorological Institute measured data')
        >>> ws.station_ids()
        >>> ws.parameters()
        >>> ws.endpoint()
        >>> ws.check_forecast_endpoint()
        >>> ws.data(parameters=[1002,3002], station_id=101104, timeStart='2020-06-12',timeEnd='2020-07-03',timezone="UTC", altitude=70,longitude=14.3711,latitude=67.2828, ViewDataFrame=True)
    '''
    def __init__(self, name):
        '''
        WeatherDataSource parameters to access at one weather data source of IPM 
        '''
        self.ipm = IPM()
        self.name = name
        

    def station_ids(self):
        ''' 
        Get a dataframe with station id and coordinate

        Parameters:
        -----------

        Returns:
        --------
            a dataframe containing name, id and coordinate of station available for weather resource'''

        rep = self.ipm.get_weatherdatasource()  

        values = {item['name']:item['spatial']['geoJSON']for item in rep}

        station_ids = dict()
        coord = dict()

        for names in values:
            if 'features' in values[names]:
                station_ids[names]=[values[names]['features'][item]['properties'] for item in range(len(values[names]['features']))]
                coord[names]=[values[names]['features'][item]['geometry'] for item in range(len(values[names]['features']))]
            else:
                station_ids[names]= 'no stations for this ressources'
                coord[names]= 'no stations for this ressources'

        df_station_ids = pandas.DataFrame(station_ids[self.name])
        df_coord = pandas.DataFrame(coord[self.name])
        df = [df_station_ids,df_coord]
        data = pandas.concat(df,axis=1)
        data = data[["name","id","coordinates"]]
        return data

    def parameters(self):
        """
        Get list of available parameters for ressource

        Parameters:
        -----------

        Returns:
        --------
            a dictionnary containing common and optional parameters
        """
        rep = self.ipm.get_weatherdatasource()

        values = {item['name']:item['parameters']for item in rep}
         
        if self.name in values:
           parameters = values[self.name]

        return parameters

    def endpoint(self):
        """
        Get endpoint associate at the name parameter of WeatherDataSource

        Parameters:
        -----------

        Returns:
        --------
            a endpoint (str) used in get_data function
        """
        endpoints = self.ipm.weatheradapter_service()

        if self.name in endpoints:
            endpoint = endpoints[self.name]
        
        return endpoint    

    def check_forecast_endpoint(self):
        """
        Check if endpoint is a forecast or not
        
        Parameters:
        -----------

        Returns:
        --------
            Boolean value True if endpoint is a forecast endpoint either False
        """
        forcast_endpoints=self.ipm.weatheradapter_service(forecast=True).values()
        
        forcast=None
        
        if self.endpoint() in forcast_endpoints:
            forcast=True
        else:
            forcast=False

        return forcast 

    def data(
        self,
        parameters=[1002,3002], 
        station_id=[101104], 
        timeStart='2020-06-12',
        timeEnd='2020-07-03',
        timezone="UTC",
        altitude=[70],
        longitude=[14.3711],
        latitude=[67.2828],
        format='ds'):
        """
        Get weather data from weatherdataressource

        Parameters:
        -----------
            parameters: list of parameters of weatherdata 
            station_id: (int) station id of weather station 
            daterange:  a pandas.date_range(start date, end date, freq='H', timezone(tz))
                        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.date_range.html
            
            Only for forcast:
            ----------------
            altitude: (list) only for Met Norway Locationforecast WGS84 Decimal degrees
            latitude: (list) WGS84 Decimal degrees
            longitude: (list) WGS84 Decimal degrees
        
        Returns:
        --------
            return a dataset (format='ds') or json format (format='json') 
        """
        forcast=self.check_forecast_endpoint()

        if forcast==False:
            
            times= pandas.date_range(timeStart,timeEnd,freq='H',tz=timezone)

            timeStart = times[0].strftime('%Y-%m-%dT%H:%M:%S')
            timeEnd = times[-1].strftime('%Y-%m-%dT%H:%M:%S')
            if times.tz._tzname == 'UTC':
                timeStart +='Z'
                timeEnd += 'Z'
            else:
                decstr = times[0].strftime('%z')
                decstr = decstr[:-2] + ':' + decstr[-2:]
                timeStart += decstr
                timeEnd += decstr
            
            interval = pandas.Timedelta(times.freq).seconds
            
            responses= [self.ipm.get_weatheradapter(
                                endpoint=self.endpoint(),
                                weatherStationId=station_id[el],
                                timeStart=timeStart,
                                timeEnd=timeEnd,
                                interval=interval,
                                parameters=parameters) for el in range(len(station_id))]
        else:
            station_id=None
            if len(latitude)==len(longitude):
                responses = [self.ipm.get_weatheradapter_forecast(
                    endpoint=self.endpoint(), 
                    altitude= altitude[el],
                    latitude=latitude[el],
                    longitude=longitude[el]) for el in range(len(latitude))]
            else:
                raise ValueError("list of latitude and longitude must be have the same lenght")
            
            #time variable
            times = pandas.date_range(
                start=responses[0]['timeStart'], 
                end=responses[0]['timeEnd'], 
                freq="H",
                name="time")


        if format == 'ds':
            #data conversion in numpy array
            data= [np.array(responses[el]['locationWeatherData'][0]['data']) for el in range(len(responses))]
            dat=[[data[el][:,i].reshape(data[el].shape[0],1) for i in range(data[el].shape[1])] for el in range(len(data))]

            # construction of dict for dataset variable
            data_vars=[{str(responses[el]['weatherParameters'][i]):(['time','location'],dat[el][i]) for i in range(len(responses[el]['weatherParameters']))} for el in range(len(data))]
            
            # construction dictionnaire coordonnée
            if station_id is not None:
                coords=[{'time':times.values,
                'location':([station_id[el]]),
                'lat':[responses[el]['locationWeatherData'][0]['latitude']],
                'lon':[responses[el]['locationWeatherData'][0]['longitude']],
                'alt':[responses[el]['locationWeatherData'][0]['altitude']]} 
                for el in range(len(responses))]
                
            else:
                coords=[{'time':times.values,
                'location':([str([latitude[el],longitude[el]])]),
                'lat':[responses[el]['locationWeatherData'][0]['latitude']],
                'lon':[responses[el]['locationWeatherData'][0]['longitude']],
                'alt':[responses[el]['locationWeatherData'][0]['altitude']]} 
                for el in range(len(responses))]
               
                
            # list de dss
            list_ds=[xr.Dataset(data_vars[el], coords=coords[el]) for el in range(len(responses))]
            #merge ds
            ds=xr.combine_by_coords(list_ds)
            
            #coordinates attributes
            ds.coords['location'].attrs['name']= 'WeatherStationId'
            ds.coords['lat'].attrs['name']='latitude'
            ds.coords['lat'].attrs['unit']='degrees_north'
            ds.coords['lon'].attrs['name']='longitude'
            ds.coords['lon'].attrs['unit']='degrees_east'
            ds.coords['alt'].attrs['name']='altitude'
            ds.coords['alt'].attrs['unit']='meters'

            #variable attribute
            param = self.ipm.get_parameter()
            p={str(item['id']): item for item in param if item['id'] in responses[0]['weatherParameters']}
            
            for el in list(ds.data_vars):
                ds.data_vars[el].attrs=p[str(el)]
            
            if station_id is not None:
                ds.attrs['weatherRessource']=self.name
                ds.attrs['weatherStationId']=station_id
                ds.attrs['longitude']=list(ds.coords['lon'].values)
                ds.attrs['latitude']=list(ds.coords['lat'].values)
                ds.attrs['timeStart']=ds.coords['time'].values[0]
                ds.attrs['timeEnd']=ds.coords['time'].values[-1]
                ds.attrs['parameters']=list(ds.data_vars)
            else:
                ds.attrs['weatherRessource']=self.name
                ds.attrs['longitude']=list(ds.coords['lon'].values)
                ds.attrs['latitude']=list(ds.coords['lat'].values)
                ds.attrs['timeStart']=ds.coords['time'].values[0]
                ds.attrs['timeEnd']=ds.coords['time'].values[-1]
                ds.attrs['parameters']=list(ds.data_vars)
            
            return ds
        else:
            return responses
                        
       
# TODO : this class should inheritate from a more generic Wheather DataHub
class WeatherDataHub(object):
    """
        Allows to access at IPM weather resources 
        give the list of weather adapter (resources) available on IPM and allows access to weather data source
        
        ..doctest::
        >>> wsh = WeatherDataHub()
        >>> wsh.list_resources()
        >>> wsh.get_resource(name = 'Finnish Meteorological Institute measured data')

    """

    def __init__(self):
        """
            Give an access to IPM interface from agroservice
        """
        self.ipm = IPM()

    def list_resources(self):
        """
        get list of ressource available in IPM services

        Parameters:
        -----------

        Returns:
        ---------
            dictionnary with name and description of available weatherdatasource on IPM service
        """
        rep = self.ipm.get_weatherdatasource()
        return {item['name']:item['description'] for item in rep}
        
    def get_ressource(self, name):
        """
        Parameters:
        -----------
            name: name of weatherdatasource (available in list ressource)
            
        Returns:
        --------
            run weatherdatasource with the name of resource
        """
        rep = self.ipm.get_weatherdatasource()
        keys = [item['name'] for item in rep]
        if name in keys:
            return WeatherDataSource(name)
        else:
            raise NotImplementedError()
