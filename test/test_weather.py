# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 14:57:47 2013

@author: lepse
"""

from alinea.weather.global_weather import *
from datetime import datetime


def test_get_meteo():
    weather = Weather()
    timestep = 2
    t_deb = datetime(2000,10,1, 1,00,00)
    mean_globalclimate, globalclimate = weather.get_weather(timestep, t_deb)
    print mean_globalclimate, globalclimate
    mean_global_radiation, globalclimate = weather.add_global_radiation(globalclimate)
    print mean_global_radiation, globalclimate
    newt_deb = weather.next_date(timestep, t_deb)
    print newt_deb
    gr = weather.convert_par(globalclimate['PPFD'])
    print gr






