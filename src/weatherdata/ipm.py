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
        station_id=101104, 
        timeStart='2020-06-12',
        timeEnd='2020-07-03',
        timezone="UTC",
        altitude=70,
        longitude=14.3711,
        latitude=67.2828,
        ViewDataFrame=True):
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
            altitude: (double) only for Met Norway Locationforecast WGS84 Decimal degrees
            latitude: (double) WGS84 Decimal degrees
            longitude: (double) WGS84 Decimal degrees
        
        Returns:
        --------
            return a dataframe (ViewDataFrame=True) or json format (ViewDataFrame=False) 
        """
        forcast=self.check_forecast_endpoint()

        if forcast==False:
            
            daterange= pandas.date_range(timeStart,timeEnd,freq='H',tz=timezone)

            timeStart = daterange[0].strftime('%Y-%m-%dT%H:%M:%S')
            timeEnd = daterange[-1].strftime('%Y-%m-%dT%H:%M:%S')
            if daterange.tz._tzname == 'UTC':
                timeStart +='Z'
                timeEnd += 'Z'
            else:
                decstr = daterange[0].strftime('%z')
                decstr = decstr[:-2] + ':' + decstr[-2:]
                timeStart += decstr
                timeEnd += decstr
        
            interval = pandas.Timedelta(daterange.freq).seconds

            response=self.ipm.get_weatheradapter(
                endpoint=self.endpoint(),
                credentials=None,
                weatherStationId=station_id, 
                timeStart=timeStart, 
                timeEnd=timeEnd, 
                interval=interval, 
                parameters=parameters
                )
            
            if ViewDataFrame ==True:
                data = {str(var): vals for var, vals in zip(response['weatherParameters'], zip(*response['locationWeatherData'][0]['data']))}
                df = pandas.DataFrame(data)
                df.index = daterange
                # TODO : get all what is needed for intantiating a WeatherData object (meta, units, ...) and retrun it
                return df
            else:
                return response

        if forcast==True:
            response = self.ipm.get_weatheradapter_forecast(
                endpoint=self.endpoint(), 
                altitude= altitude,
                latitude=latitude,
                longitude=longitude
                )

            daterange= pandas.date_range(
                response['timeStart'],
                response['timeEnd'],
                freq='H',tz='UTC')
            
            timeStart = daterange[0].strftime('%Y-%m-%dT%H:%M:%S')
            timeEnd = daterange[-1].strftime('%Y-%m-%dT%H:%M:%S')
            if daterange.tz._tzname == 'UTC':
                timeStart +='Z'
                timeEnd += 'Z'
            else:
                decstr = daterange[0].strftime('%z')
                decstr = decstr[:-2] + ':' + decstr[-2:]
                timeStart += decstr
                timeEnd += decstr
        
            interval = pandas.Timedelta(daterange.freq).seconds

            if ViewDataFrame ==True:
                data = {str(var): vals for var, vals in zip(response['weatherParameters'], zip(*response['locationWeatherData'][0]['data']))}
                df = pandas.DataFrame(data)
                df.index = daterange
                # TODO : get all what is needed for intantiating a WeatherData object (meta, units, ...) and retrun it
                return df
            else:
                return response

    
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
