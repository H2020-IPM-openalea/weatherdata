from openalea.weatherdata.weather_data import WeatherData
import pandas

def test_intantiate():
    wd = WeatherData('ipm_decision')
    daterange = pandas.date_range('2020-03-06T10:00:00', '2020-03-15T06:00:00', freq='H', tz='UTC')
    wd.get_data('station', daterange, 'name')
    wd.data
    wd.meta
    wd.meta_vars