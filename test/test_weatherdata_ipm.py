import pandas
import xarray

from weatherdata.ipm import WeatherDataHub, WeatherDataSource

wdh= WeatherDataHub()
list_resources = list(wdh.list_resources())

def keys_exists(dict_, keys, test = all):
    return test(key in dict_ for key in keys)

def test_list_ressource():
    rep= wdh.list_resources()
    assert type(rep) is dict, rep
    assert keys_exists(
            rep.keys(),
            ('Met Norway Locationforecast', 
            'FMI weather forecasts', 
            'Finnish Meteorological Institute measured data', 
            'Landbruksmeteorologisk tjeneste', 'MeteoBot API',
            'Fruitweb',
            'Metos')
        )

def test_get_ressource():

    for name in list_resources:
        rep=wdh.get_ressource(name=name)
        if isinstance(rep,WeatherDataSource):
            pass

def test_station_id():
    wds_station_ids={name:WeatherDataSource(name=name).station_ids() for name in list_resources}

    # Met Norway Locationforecast resource
    assert type(wds_station_ids['Met Norway Locationforecast']) is str
    assert wds_station_ids['Met Norway Locationforecast'] == 'no stations for this ressources'
    # FMI weather forecasts resource
    assert type(wds_station_ids['FMI weather forecasts']) is str
    assert wds_station_ids['FMI weather forecasts'] == 'no stations for this ressources'

    # Finnish Meteorological Institute measured data resource
    assert type(wds_station_ids['Finnish Meteorological Institute measured data']) is pandas.DataFrame
    assert wds_station_ids['Finnish Meteorological Institute measured data'].shape==(208,3)
    assert list(wds_station_ids['Finnish Meteorological Institute measured data'].columns)==['name', 'id', 'coordinates']
    # Landbruksmeteorologisk tjeneste resource
    assert type(wds_station_ids['Landbruksmeteorologisk tjeneste']) is pandas.DataFrame
    assert wds_station_ids['Landbruksmeteorologisk tjeneste'].shape==(92,3)
    assert list(wds_station_ids['Landbruksmeteorologisk tjeneste'].columns)==['name', 'id', 'coordinates']
    # MeteoBot API resource
    assert type(wds_station_ids['MeteoBot API']) is pandas.DataFrame
    assert wds_station_ids['MeteoBot API'].shape==(528,3)
    assert list(wds_station_ids['MeteoBot API'].columns)==['name', 'id', 'coordinates']
    # Fruitweb resource
    assert type(wds_station_ids['Fruitweb']) is str
    assert wds_station_ids['Fruitweb'] == 'no stations for this ressources'

    # Metos resource
    assert type(wds_station_ids['Metos']) is str
    assert wds_station_ids['Fruitweb'] == 'no stations for this ressources'

def test_parameters():
    wds_parameters={name:WeatherDataSource(name=name).parameters() for name in list_resources}

    # Met Norway Locationforecast resource
    assert type(wds_parameters['Met Norway Locationforecast']) is dict
    assert type(wds_parameters['Met Norway Locationforecast']['common']) is list
    assert wds_parameters['Met Norway Locationforecast']['common'] == [1001, 3001, 2001, 4002]
    assert wds_parameters['Met Norway Locationforecast']['optional'] is None
    # FMI weather forecasts resource
    assert type(wds_parameters['FMI weather forecasts']) is dict
    assert type(wds_parameters['FMI weather forecasts']['common']) is list
    assert wds_parameters['FMI weather forecasts']['common'] == [1001, 1901, 2001, 3001, 4002, 5001]
    assert wds_parameters['FMI weather forecasts']['optional'] is None

    # Finnish Meteorological Institute measured data resource
    assert type(wds_parameters['Finnish Meteorological Institute measured data']) is dict
    assert type(wds_parameters['Finnish Meteorological Institute measured data']['common']) is list
    assert wds_parameters['Finnish Meteorological Institute measured data']['common'] == [1002, 3002, 2001, 4003]
    assert wds_parameters['Finnish Meteorological Institute measured data']['optional'] is None
    # Landbruksmeteorologisk tjeneste resource
    assert type(wds_parameters['Landbruksmeteorologisk tjeneste']) is dict
    assert type(wds_parameters['Landbruksmeteorologisk tjeneste']['common']) is list
    assert wds_parameters['Landbruksmeteorologisk tjeneste']['common'] == [1002, 1003, 1004, 3002, 2001, 4003]
    assert wds_parameters['Landbruksmeteorologisk tjeneste']['optional'] == [3101, 5001]

    # MeteoBot API resource
    assert type(wds_parameters['MeteoBot API']) is dict
    assert type(wds_parameters['MeteoBot API']['common']) is list
    assert wds_parameters['MeteoBot API']['common'] == [1001, 3001, 2001, 4002]
    assert wds_parameters['MeteoBot API']['optional'] is None
    
    # Fruitweb resource
    assert type(wds_parameters['Fruitweb']) is dict
    assert type(wds_parameters['Fruitweb']['common']) is list
    assert wds_parameters['Fruitweb']['common'] == [1001, 3001, 2001, 4002] 
    assert wds_parameters['Fruitweb']['optional'] is None

    # Metos resource
    assert type(wds_parameters['Metos']) is dict
    assert type(wds_parameters['Metos']['common']) is list
    assert wds_parameters['Metos']['common'] == [1001, 3001, 2001, 4002] 
    assert wds_parameters['Metos']['optional'] is None

def test_endpoint():
    wds_endpoints={name:WeatherDataSource(name=name).endpoint() for name in list_resources}

    # Met Norway Locationforecast resource
    assert type(wds_endpoints['Met Norway Locationforecast']) is str
    assert wds_endpoints['Met Norway Locationforecast']== '/weatheradapter/yr/'

    # FMI weather forecasts resource
    assert type(wds_endpoints['FMI weather forecasts']) is str
    assert wds_endpoints['FMI weather forecasts']== '/weatheradapter/fmi/forecasts'

    # Finnish Meteorological Institute measured data resource
    assert type(wds_endpoints['Finnish Meteorological Institute measured data']) is str
    assert wds_endpoints['Finnish Meteorological Institute measured data']== '/weatheradapter/fmi/'

    # Landbruksmeteorologisk tjeneste resource
    assert type(wds_endpoints['Landbruksmeteorologisk tjeneste']) is str
    assert wds_endpoints['Landbruksmeteorologisk tjeneste']== '/ipmdecisions/getdata/'

    # MeteoBot API resource
    assert type(wds_endpoints['MeteoBot API']) is str
    assert wds_endpoints['MeteoBot API']== '/weatheradapter/meteobot/'

    # Fruitweb resource
    assert type(wds_endpoints['Fruitweb']) is str
    assert wds_endpoints['Fruitweb']== '/weatheradapter/davisfruitweb/'

    # Metos resource
    assert type(wds_endpoints['Metos']) is str
    assert wds_endpoints['Metos']== '/weatheradapter/metos/'

def test_check_forcast():
    wds_check_forcast={name:WeatherDataSource(name=name).check_forecast_endpoint() for name in list_resources}

    # Met Norway Locationforecast resource
    assert type(wds_check_forcast['Met Norway Locationforecast']) is bool
    assert wds_check_forcast['Met Norway Locationforecast'] is True

    # FMI weather forecasts resource
    assert type(wds_check_forcast['FMI weather forecasts']) is bool
    assert wds_check_forcast['FMI weather forecasts'] is True

    # Finnish Meteorological Institute measured data resource
    assert type(wds_check_forcast['Finnish Meteorological Institute measured data']) is bool
    assert wds_check_forcast['Finnish Meteorological Institute measured data'] is False

    # Landbruksmeteorologisk tjeneste resource
    assert type(wds_check_forcast['Landbruksmeteorologisk tjeneste']) is bool
    assert wds_check_forcast['Landbruksmeteorologisk tjeneste'] is False

    # MeteoBot API resource
    assert type(wds_check_forcast['MeteoBot API']) is bool
    assert wds_check_forcast['MeteoBot API'] is False

    # Fruitweb resource
    assert type(wds_check_forcast['Fruitweb']) is bool
    assert wds_check_forcast['Fruitweb'] is False

    # Metos resource
    assert type(wds_check_forcast['Metos']) is bool
    assert wds_check_forcast['Metos'] is False

def test_data():
    
    # Met Norway Locationforecast resource
    norway=WeatherDataSource(name='Met Norway Locationforecast')
    rep1_ds=norway.data(latitude=[67.2828],longitude=[14.3711],altitude=[70],format="ds")
    assert type(rep1_ds) is xarray.Dataset
    assert keys_exists(dict(rep1_ds.dims),('alt','lat','location','lon','time'))
    
    ## test coords
    assert list(rep1_ds.coords)==['time', 'location', 'lat', 'lon', 'alt']
    assert rep1_ds.coords['time'].dtype=='<M8[ns]'
    assert rep1_ds.coords['time'].attrs=={}
    assert rep1_ds.coords['location'].dtype=='<U18'
    assert rep1_ds.coords['location'].values=='[67.2828, 14.3711]'
    #assert rep1_ds.coords['location'].attrs=={'name': '[latitude,longitude]'}
    assert rep1_ds.coords['lat'].dtype=='float64'
    assert rep1_ds.coords['lat'].attrs=={'name': 'latitude', 'unit': 'degrees_north'}
    assert rep1_ds.coords['lat'].values==[67.2828]
    assert rep1_ds.coords['lon'].dtype=='float64'
    assert rep1_ds.coords['lon'].attrs=={'name': 'longitude', 'unit': 'degrees_east'}
    assert rep1_ds.coords['lon'].values==[14.3711]
    assert rep1_ds.coords['alt'].dtype=='float64'
    assert rep1_ds.coords['alt'].attrs=={'name': 'altitude', 'unit': 'meters'}
    assert rep1_ds.coords['alt'].values==[70]
    
    ## test data variable
    assert list(rep1_ds.data_vars) == ['1001', '3001', '2001', '4002']
    assert rep1_ds.data_vars['1001'].dtype == 'float64'
    assert rep1_ds.data_vars['1001'].attrs == {'id': 1001, 'name': 'Instantaneous temperature at 2m', 'description': None, 'unit': 'Celcius'}    
    assert rep1_ds.data_vars['3001'].dtype == 'float64'
    assert rep1_ds.data_vars['3001'].attrs == {'id': 3001, 'name': 'Instantaneous RH at 2m (%)', 'description': None, 'unit': '%'}    
    assert rep1_ds.data_vars['2001'].dtype == 'float64'
    assert rep1_ds.data_vars['2001'].attrs == {'id': 2001, 'name': 'Precipitation', 'description': None, 'unit': 'mm'}
    assert rep1_ds.data_vars['4002'].dtype == 'float64'
    assert rep1_ds.data_vars['4002'].attrs == {'id': 4002, 'name': 'Instantaneous wind speed at 2m', 'description': None, 'unit': 'm/s'}

    ## test ds attribute
    assert type(rep1_ds.attrs) is dict
    assert keys_exists(rep1_ds.attrs,('weatherRessource','longitude','latitude','timeStart','timeEnd','parameters'))
    assert rep1_ds.attrs['weatherRessource']=='Met Norway Locationforecast'
    assert rep1_ds.attrs['longitude']==[14.3711]
    assert rep1_ds.attrs['latitude']==[67.2828]
    assert rep1_ds.attrs['parameters']==['1001', '3001', '2001', '4002']

    #test conversion dataframe
    assert rep1_ds.to_dataframe().shape[1]==4
    assert rep1_ds.to_dataframe().index.names==['alt', 'lat', 'location', 'lon', 'time']