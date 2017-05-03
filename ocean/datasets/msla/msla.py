#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac 
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import os
import os.path
import sys

from ocean import util, config, logger
from ocean.config import productName
from ocean.datasets import Dataset, MissingParameter, ValidationError
from ocean.plotter import COMMON_FILES
from mslaPlotter import *

#Maybe move these into configuration later
seaGraph = '%s_%s_%s_%s'

#get the server dependant path configurations
serverCfg = config.get_server_config()

#get dataset dependant production information
seaLevelProduct = productName.products['sealevel']

class msla(Dataset):
    
    __form_params__ = {
        'lat': float,
        'lon': float,
    }
    __form_params__.update(Dataset.__form_params__)

    __required_params__ = Dataset.__required_params__ + [
        'date',
        'area',
    ]
    
    __periods__ = [
        'daily',
        'monthly'
    ]

    __variables__ = [        
        'sla',
    ]

    __plots__ = [
        'map',
        'point'
    ]

    __subdirs__ = [
        'grids',
    ]
    
    def process(self, params):
        response = {}
        
        if 'date' not in params:
            raise MissingParameter("Missing parameter 'date'")
        elif 'area' not in params:
            raise MissingParameter("Missing parameter 'area'")

        variableStr = params['variable']
        areaStr = params['area']
        periodStr = params['period']

        plotter = MslaPlotter(variableStr)

        if params['plot'] == 'map':
            if periodStr == 'daily':
                dateStr = params['date'].strftime('%Y%m%d')
                fileName = seaGraph % (seaLevelProduct['daily'],
                                       variableStr, areaStr,
                                       dateStr)                                   
            elif periodStr == 'monthly':
                dateStr = params['date'].strftime('%Y%m')
                fileName = seaGraph % (seaLevelProduct['monthly'],
                                       variableStr, areaStr,
                                       dateStr)
            else:
                assert 0, "Should not be reached"

            outputFileName = serverCfg['outputDir'] + fileName
    
            if not util.check_files_exist(outputFileName, COMMON_FILES.values()):
                plotter.plot(fileName, **params)

            if not util.check_files_exist(outputFileName, COMMON_FILES.values()):
                response['error'] = \
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
