
# This file has been generated at Fri May 31 10:05:45 2013

from openalea.core import *


__name__ = 'weather'

__editable__ = True
__description__ = ''
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = []
__version__ = '0.8.0'
__authors__ = ''
__institutes__ = None
__icon__ = ''


__all__ = ['global_weather_Weather']



global_weather_Weather = Factory(name='Weather',
                authors=' (wralea authors)',
                description='',
                category='Unclassified',
                nodemodule='alinea.weather.global_weather',
                nodeclass='Weather',
                inputs=[{'interface': IFileStr, 'name': 'data_file', 'value': None, 'desc': 'Path for read the meteo data file csv'}],
                outputs=[{'interface': None, 'name': 'mean_globalclimate, globalclimate, t_deb', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




