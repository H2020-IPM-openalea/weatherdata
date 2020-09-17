import os
import json

datadir = os.path.join(os.path.dirname(__file__), 'data')


def ipm_weather_data_standard():
    """A path to a file containing the result of getdata webservice"""
    return os.path.join(datadir, 'weather_data_standard_example.json')
    
def ipm_getdata_request(weatherStationid=None, time_start=None, time_end=None, parameters=None, interval=None, ignoreError=None)
    """simulate a webservice query returning data"""
    path = ipm_weather_data_standard()
    with open(path) as f:
        data = json.load(f)
    return data
