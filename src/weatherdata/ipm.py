from agroservices import IPM
import pandas
import datetime

ipm = IPM()
ressource_ids = {'Met Norway Locationforecast': 'yr',
                 'Finnish Meteorological Institute measured data': 'fmi',
                 'FMI weather forecasts': 'fmi_forecasts',
                 'Landbruksmeteorologisk tjeneste': 'lmt',
                 'MeteoBot API': 'metobot',
                 'Fruitweb': 'fw',
                 'Metos':'metos'}

weather_adapter = {'fmi': ipm.get_weatheradapter_fmi,
                   'yr': ipm.get_weatheradapter_yr,
                   'lmt':'',
                   'meteobot':'',
                   'fw':'',
                   'metos':''
                    }

class WeatherDataSource(object):

    def __init__(self, name, station_ids):
        self.ipm = IPM()
        self.id = ressource_ids[name]
        self.ws = weather_adapter[ressource_ids.get(name)]
        self.station_ids = station_ids

    def get_station_ids(self):
        return self.station_ids
    
    def get_parameters(self):
        return self.ipm.get_parameter()


    def get_data(self,parameters, station_id, daterange):
        timeStart = daterange[0].strftime('%Y-%m-%dT%H:%M:%S+%H:%M')
        timeEnd = daterange[-1].strftime('%Y-%m-%dT%H:%M:%S+%H:%M')
        interval = pandas.Timedelta(daterange.freq).seconds
        response=self.ws(weatherStationId=station_id, timeStart=timeStart, timeEnd=timeEnd, interval=interval, parameters=parameters)
        data = {str(var): vals for var, vals in zip(response['weatherParameters'], zip(*response['locationWeatherData'][0]['data']))}
        df = pandas.DataFrame(data)
        if daterange.tz._tzname =='UTC':
            df.index = daterange.strftime('%Y-%m-%dT%H:%M:%S')+"Z"
        else:
             df.index = daterange
        # TODO : get all what is needed for intantiating a WeatherData object (meta, units, ...) and retrun it
        return df
    
# TODO : this class should inheritate from a more generic Wheather DataHub
class WeatherDataHub(object):
    """
    """

    def __init__(self):
        self.ws = IPM()

    def list_ressources(self):
        """
        get list of ressource available in IPM services

        Parameters:
        -----------

        Returns:
        ---------
            dictionnary with name and description of available weatherdatasource on IPM service
        """
        rep = self.ws.get_weatherdatasource()
        return {it['name']:it['description'] for it in rep}

    def get_ressource(self, name):
        rep = self.ws.get_weatherdatasource()
        keys = [it['name'] for it in rep]
        station_ids=['101104']
        if name in keys:
            return WeatherDataSource(name, station_ids)
        else:
            raise NotImplementedError()