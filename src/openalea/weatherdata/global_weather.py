# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 14:29:15 2013

@author: lepse
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from math import exp

def parse(yr, doy, hr):
    """ Convert the 'An', 'Jour' and 'hhmm' variables of the meteo dataframe in a datetime object (%Y-%m-%d %H:%M:%S format)
    """
    an, jour, heure = [int(x) for x in [yr, doy, hr/100]]
    dt = datetime(an - 1, 12, 31)
    delta = timedelta(days=jour, hours=heure)
    return dt + delta

class Weather(object):
    """ Class compliying echap local_microclimate model protocol (meteo_reader).
        expected variables of the data_file are:
            - 'An'
            - 'Jour'
            - 'hhmm' : hour and minutes (universal time, UTC)
            - 'PAR' : Quantum PAR (ppfd) in micromol.m-2.sec-1
            - 'Pluie' : Precipitation (mm)
            - 'Tair' : Temperature of air (Celcius)
            - 'HR': Humidity of air (kPa)
            - 'Vent' : Wind speed (m.s-1)
    """
    def __init__(self, data_file='', sep = ';'):
        if data_file is '':
            self.data = None
        else:
            data = pd.read_csv(data_file, parse_dates={'datetime':['An','Jour','hhmm']},
                               date_parser=parse, sep=sep,
                               usecols=['An','Jour','hhmm','PAR','Tair','HR','Vent','Pluie'])

            data.index = data.datetime
            data = data.rename(columns={'PAR':'PPFD',
                                 'Tair':'temperature_air',
                                 'HR':'relative_humidity',
                                 'Vent':'wind_speed',
                                 'Pluie':'rain'})
            self.data = data

    def get_weather(self, timestep, t_deb):
        """ Read an hourly meteo file and return the global climate averaged and the global climate detail dataframe for an hour time step and the start date of each time step.

        :Parameters:
        ----------
        - `timestep` (int)
            The time step on which the averages are performed and for which the data frame is return
        - `t_deb` (datetime)
            The start date for reading the meteo file 

        :Returns:
        ---------
        - `mean_globalclimate` (dataframe)
            Mean variables of the global climate dataframe
        - `globalclimate` (dataframe)
            Pandas dataframe with hourly meteo for the time step from t_deb
        """    
        data = self.data

        globalclimate = data.truncate(before = t_deb, after = self.next_date((timestep - 1), t_deb))
        mean_globalclimate = globalclimate.mean()
        return mean_globalclimate, globalclimate
        
    
    def get_variable(self, what, time_sequence):
        """
        return values of what at date specified in time sequence
        """
        return self.data[what][time_sequence]

    
    def split_weather(self, time_step, t_deb, n_steps):
        
        """ return an generator iterating over sub-part of the meteo data, each corresponding to one time-step"""
        tstep = [t_deb + i * timedelta(hours=time_step) for i in range(n_steps)]
        return (self.data.truncate(before = t, after = self.next_date((time_step - 1), t)) for t in tstep)
    
    def str_to_datetime(self, t_deb):
        """ Convert a date in string format into a datetime object
        """
        format = "%Y-%m-%d %H:%M:%S"
        if isinstance(t_deb, str):
            t_deb = datetime.strptime(t_deb,format)
        return t_deb

    def add_global_radiation(self):
        """ Add the column 'global_radiation' to the data frame.
        """
        data = self.data
        global_radiation = self.PPFD_to_global(data['PPFD'])
        data = data.join(global_radiation)
        
    def add_vapor_pressure(self, globalclimate):
        """ Add the column 'global_radiation' to the data frame.
        """
        vapor_pressure = self.humidity_to_vapor_pressure(globalclimate['relative_humidity'], globalclimate['temperature_air'])
        globalclimate = globalclimate.join(vapor_pressure)
        mean_vapor_pressure = globalclimate['vapor_pressure'].mean()
        return mean_vapor_pressure, globalclimate

    # def fill_data_frame(self):
        # """ Add all possible variables.

        # For instance, call the method 'add_global_radiation'.
        # """
        # self.add_global_radiation()

    def next_date(self, timestep, t_deb):
        """ Return the new t_deb after the timestep 
        """
        return t_deb + timedelta(hours=timestep)

    def PPFD_to_global(self, PAR):
        """ Convert the PAR (ppfd in micromol.m-2.sec-1) in global radiation (J.m-2.s-1, ie W/m2)
        1 WattsPAR.m-2 = 4.6 ppfd, 1 Wglobal = 0.48 WattsPAR)
        """
        gr = (PAR * 1./4.6) / 0.48
        gr.name = 'global_radiation'
        gr.index = PAR.index
        return gr

    def Psat(self, T):
        """ Saturating water vapor pressure (kPa) at temperature T (Celcius) with Tetens formula
        """
        return 0.6108 * np.exp(17.27 * T / (237.3 + T))

    def humidity_to_vapor_pressure(self, humidity, Tair):
        """ Convert the relative humidity (%) in water vapor pressure (kPa)
        """
        vp = humidity / 100. * self.Psat(Tair)
        vp.name = 'vapor_pressure'
        vp.index = humidity.index
        return vp
                
#
# To do /add (pour ratp): 
# file meteo exemples
# add RdRs (ratio diffus /global)
# add NIR = RG - PAR
# add Ratmos = epsilon sigma Tair^4, epsilon = 0.7 clear sky, eps = 1 overcast sky
# add CO2
#
# peut etre aussi conversion hUTC -> time zone 'euroopean' 

##
# sinon faire des generateur pour tous les fichiers ratp
#
