import pandas

from weatherdata.ipm import WeatherDataHub, WeatherDataSource

wdh= WeatherDataHub()

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
    list_resources = list(wdh.list_resources())
    
    for name in list_resources:
        rep=wdh.get_ressource(name=name)
        if isinstance(rep,WeatherDataSource):
            pass

def test_station_id():
    list_resources = list(wdh.list_resources())
    wds_station_ids={name:WeatherDataSource(name=name).station_ids() for name in list_resources}
    # Met Norway Locationforecast resource
    assert type(wds_station_ids['Met Norway Locationforecast']) is str
    # FMI weather forecasts resource
    assert type(wds_station_ids['FMI weather forecasts']) is str
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
    # Metos resource
    assert type(wds_station_ids['Metos']) is str