#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os
import os.path
import sys

from ocean import util, config
from ocean.plotter import COMMON_FILES
from ocean.config import productName, tidalGaugeConfig
from ocean.datasets import Dataset, MissingParameter, ValidationError

from sealevelPlotter import *

#Maybe move these into configuration later
seaGraph = '%s_%s_%s_%s'
seaChart = '%s_%s_%s'

#get the server dependant path configurations
serverCfg = config.get_server_config()

#get dataset dependant production information
seaLevelProduct = productName.products['sealevel']

class sealevel(Dataset):

    __form_params__ = {
        'tidalGaugeId': str,
        'lat': float,
        'lon': float,
    }
    __form_params__.update(Dataset.__form_params__)

    __periods__ = [
        'monthly',
    ]

    __variables__ = [
        'alt',
        'rec',
        'gauge',
    ]

    __plots__ = [
        'map',
        'ts',
        'point'
    ]

    __subdirs__ = [
        'grids',
        'gauges-new',
    ]

    @classmethod
    def validate_tidalGaugeId(self, p):
        assert p in tidalGaugeConfig.tidalGauge

    def plot_surface(self, params):
        response = {}

        if 'date' not in params:
            raise MissingParameter("Missing parameter 'date'")
        elif 'area' not in params:
            raise MissingParameter("Missing parameter 'area'")

        variableStr = params['variable']
        dateStr = params['date'].strftime('%Y%m%d')
        areaStr = params['area']
        periodStr = params['period']

        plotter = SeaLevelSurfacePlotter(variableStr)
 
        if params['plot'] == 'map':
            if periodStr == 'monthly':
                fileName = seaGraph % (seaLevelProduct['monthly'],
                                       variableStr, areaStr,
                                       dateStr[:6])
            else:
                assert 0, "Should not be reached"

            outputFileName = serverCfg['outputDir'] + fileName

            if not util.check_files_exist(outputFileName, COMMON_FILES.values()):
                plotter.plot(fileName, **params)

            if not util.check_files_exist(outputFileName, COMMON_FILES.values()):
                responseObj['error'] = \
                    "Requested image is not available at this time."
            else:
                response.update(util.build_response_object(
                        COMMON_FILES.keys(),
                        os.path.join(serverCfg['baseURL'],
                                     serverCfg['rasterURL'],
                                     fileName),
                        COMMON_FILES.values()))
                response['map'] = 'poamasla'
                util.touch_files(os.path.join(serverCfg['outputDir'],
                                              fileName),
                                 COMMON_FILES.values())
        elif params['plot'] == 'point': #for point value extraction
            (lat, lon), value = plotter.extract(**params)
            response['value'] = float(value)
        return response

    def plot_alt(self, params):
        response = {}

        if params['plot'] == 'ts':
            if 'lon' not in params or 'lat' not in params:
                raise MissingParameter(
                    "'lat' or 'lon' not present in parameters")

            # FIXME: snap to grid location
            loc = '%i_%i' % (params['lat'] * 1000, params['lon'] * 1000)
            params['tidalGaugeName'] = '%g%s %g%s' % (
                abs(params['lat']), 'N' if params['lat'] >= 0 else 'S',
                abs(params['lon']), 'E' if params['lon'] >= 0 else 'W')

            fileName = seaChart % (seaLevelProduct['monthly'],
                                   loc, 'alt')
            outputFileName = os.path.join(serverCfg['outputDir'], fileName)

            if not os.path.exists(outputFileName + '.png'):
                plotTimeseries(outputFileName, **params)

            if not os.path.exists(outputFileName + '.png'):
                response['error'] = \
                    "Requested image is not available at this time."
            else:
                response.update(util.build_response_object(
                    [ 'altimg', 'alttxt' ],
                    os.path.join(serverCfg['baseURL'],
                                 serverCfg['rasterURL'],
                                 fileName),
                    [ '.png', '.txt' ]))
                util.touch_files(os.path.join(serverCfg['outputDir'],
                                              fileName),
                                 [ '.png', '.txt' ])
        else: # map
            response.update(self.plot_surface(params))

        return response

    def plot_rec(self, params):
        response = {}

        if params['plot'] == 'ts':
            if 'lon' not in params or 'lat' not in params:
                raise MissingParameter(
                    "'lat' or 'lon' not present in parameters")

            # FIXME: snap to grid location
            loc = '%i_%i' % (params['lat'] * 1000, params['lon'] * 1000)
            params['tidalGaugeName'] = '%g%s %g%s' % (
                abs(params['lat']), 'N' if params['lat'] >= 0 else 'S',
                abs(params['lon']), 'E' if params['lon'] >= 0 else 'W')

            fileName = seaChart % (seaLevelProduct['monthly'],
                                   loc, 'rec')
            outputFileName = os.path.join(serverCfg['outputDir'], fileName)

            if not os.path.exists(outputFileName + '.png'):
                plotTimeseries(outputFileName, **params)

            if not os.path.exists(outputFileName + '.png'):
                responseObj['error'] = \
                    "Requested image is not available at this time."
            else:
                response.update(util.build_response_object(
                    [ 'recimg', 'rectxt' ],
                    os.path.join(serverCfg['baseURL'],
                                 serverCfg['rasterURL'],
                                 fileName),
                    [ '.png', '.txt' ]))
                util.touch_files(os.path.join(serverCfg['outputDir'],
                                              fileName),
                                 [ '.png', '.txt' ])
        else: # map
            response.update(self.plot_surface(params))

        return response

    def plot_gauge(self, params):
        response = {}

        if 'tidalGaugeId' not in params:
            raise ValidationError("Variable 'gauge' requires a 'tidalGaugeId'")
        elif params['plot'] != 'ts':
            raise ValidationError("Plot must be 'ts'")

        tid = params['tidalGaugeId']

        params['tidalGaugeName'] = tidalGaugeConfig.tidalGauge[tid]['name']
        params['lat'] = tidalGaugeConfig.tidalGauge[tid]['lat']
        params['lon'] = tidalGaugeConfig.tidalGauge[tid]['lon']

        fileName = seaChart % (seaLevelProduct['monthly'], tid, 'tid')
        outputFileName = os.path.join(serverCfg['outputDir'], fileName)

        FILES = ['.png', '.csv']

        plotTidalGauge(outputFileName, **params)

        if not util.check_files_exist(outputFileName, FILES):
            responseObj['error'] = \
                "Requested image is not available at this time."
        else:
            response.update(util.build_response_object(
                [ 'tidimg', 'tidtxt' ],
                os.path.join(serverCfg['baseURL'],
                             serverCfg['rasterURL'],
                             fileName),
                FILES))
            util.touch_files(os.path.join(serverCfg['outputDir'],
                                          fileName),
                             FILES)

        return response

    def process(self, params):
        response = {}

        response.update(getattr(self, 'plot_%s' % params['variable'])(params))

        return response
