from agroservices import IPM

ipm = IPM()
ressource_ids = {'Finnish Meteorological Institute measured data': 'fmi'}
weather_adapter = {'fmi': ipm.get_weatheradapter_fmi}



import pandas



class WheatherDataSource(object):

    def __init__(self, name, station_ids):
        self.id = ressource_ids[name]
        self.ws = weather_adapter[name]
        self.station_ids = station_ids

    def get_station_ids(self):
        return self.station_ids


    def get_data(self,parameters, station_id, daterange):
        timeStart = daterange[0].strftime('%Y-%m-%dT%H:%M:%S%z')
        timeEnd = daterange[-1].strftime('%Y-%m-%dT%H:%M:%S%z')
        interval = pandas.Timedelta(daterange.freq).seconds
        if daterange.tz._tzname == 'UTC':
            timeStart += 'Z'
            timeEnd += 'Z'
        response=self.ws(weatherStationid=station_id, timeStart=timeStart, timeEnd=timeEnd, interval=interval, parameters=parameters)
        data = {str(var): vals for var, vals in
                zip(response['weatherParameters'], zip(*response['locationWeatherData'][0]['data']))}
        df = pandas.DataFrame(data)
        df.index = daterange
        # TODO : get all what is needed forintantiating a WeatherData object (meta, units, ...) and retrun it
        return df


# TODO : this class should inheritate from a more generic Wheather DataHub
class WeatherDataHub(object):

    def __init__(self):
        self.ws = IPM()

    def list_ressources(self):
        rep = self.ws.get_weatherdatasource()
        return {it['name']:it['desc'] for it in rep}

    def get_ressource(self, name):
        rep = self.ws.get_weatherdatasource()
        keys = [it['name'] for it in rep]
        staion_ids=['101104']
        if name in keys:
            return WheatherDataSource(name, station_ids)
        else:
            raise NotImplementedError()