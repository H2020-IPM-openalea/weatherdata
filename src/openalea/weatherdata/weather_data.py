"""WeatherData class for handling weatherdata"""


wrappers = {'ipm_decision': 'openalea.weatherdata.wrapper.ipm_decision',
            'echap': 'openalea.weatherdata.wrapper.echap'}

# for wrapper in wrappers:
#     try:
#         eval('import ' + wrappers[wrapper] + ' as ' + wrapper)
#     except ImportError:
#         print('wrapper not found' + wrapper)
#         continue

import openalea.weatherdata.wrapper.ipm_decision as ipm_decision


class WeatherData(object):

    def __init__(self, name):
        if name not in wrappers:
            raise ValueError('unknown source: ' + name)
        self.name=name
        self.get_data = eval(name + '.get_data')
        self.get_meta = eval(name + '.get_meta')

