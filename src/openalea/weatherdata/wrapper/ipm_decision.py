from openalea.weatherdata.data import  ipm_getdata_request, ipm_get_weatherparameter
import pandas


#TODO : should this be part of weather ? (ie weather is for a datasource with several station
def get_station_list():
    pass


def get_data(station_id, daterange=pandas.date_range('2020-03-06T10:00:00', '2020-03-15T06:00:00', freq='H', tz='UTC'), label='id'):

    #TODO build resquest for querying data source (datestart....)
    timeStart = daterange[0]
    timeEnd = daterange[-1]
    interval = pandas.Timedelta(daterange.freq).seconds
    response = ipm_getdata_request(weatherStationid=station_id, timeStart=timeStart, timeEnd=timeEnd, interval=interval)
    data = {str(var):vals for var, vals in zip(response['weatherParameters'], zip(*response['locationWeatherData'][0]['data']))}
    df = pandas.DataFrame(data)
    df.index = daterange
    # get associated meta
    parameters = ipm_get_weatherparameter()
    meta_vars = {str(item['id']) : item for item in parameters if str(item['id']) in df.columns}
    if label is not 'id':
        df.rename({k:v[label] for k,v in meta_vars.items()}, axis='columns', inplace=True)
    return df, meta_vars, {k: response['locationWeatherData'][0][k] for k in ('latitude', 'longitude', 'altitude')}


