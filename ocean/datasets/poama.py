#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import json

from ocean import util, config
from ocean.datasets import Dataset
from ocean.plotter import COMMON_FILES, EXTRA_FILES

class POAMA(Dataset):

    __form_params__ = {
        'mode': str,
        'lat': float,
        'lon': float,
    }
    __form_params__.update(Dataset.__form_params__)

    __required_params__ = Dataset.__required_params__ + [
    ]

    __periods__ = [
        'seasonal',
    ]

    __variables__ = [
        'height',
        'ssta',
        'sst'
    ]

    __plots__ = [
        'map',
        'point'
    ]

    __subdirs__ = [
        'sla',
        'ssta'
    ]

    def __init__(self):
        self.plotter = self.PLOTTER()

    def process(self, params):
        response = {}

        dataset = params['dataset']
        varStr = params['variable']
        periodStr = params['period']
        regionStr = params['area']

        if params['plot'] == 'map':
            config = self.generateConfig(params)
            configStr = json.dumps(config) 

            params['forecast'] = config

            response['forecast'] = configStr 
            response['mapimg'] = self.getPlotFileName(varStr, 0, 'pac')[1] + COMMON_FILES['mapimg']
            response['scale'] = self.getPlotFileName(varStr, 0, 'pac')[1] + COMMON_FILES['scale']
            # response['img'] = self.getPlotFileName(varStr, 0, 'pac')[1] + COMMON_FILES['img']
            response['img'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['img']
            if varStr == 'ssta':
                response['map'] = 'anom'
            elif varStr == 'height':
                response['map'] = 'poamasla'
            elif varStr == 'sst':
                response['map'] = 'mean'
                response['contour'] = self.getPlotFileName(varStr, 0, 'pac')[1] + EXTRA_FILES['map'] + EXTRA_FILES['contour']
                response['normal'] = self.getPlotFileName(varStr, 0, 'pac')[1] + EXTRA_FILES['map'] + EXTRA_FILES['normal']

            if ('mode' in params) and (params['mode'] == 'preprocess'):
                response['preproc'] = 'inside'
                self.preprocess(varStr, regionStr, params)

        elif params['plot'] == 'point': #for point value extraction
            (lat, lon), value = self.plotter.extract(**params)
            response['value'] = float(value)
 
        return response

    def preprocess(self, varName, region, args):
        '''
            Allows the map images to be produced via the URL.
        '''
        pass

    def generateConfig(self, args):
        '''
            Generate the configuration file
        '''
        pass

 
    def getPlotFileName(self, varName, timeIndex, regionName):
        '''
            A helper method to put together the plot file name.
        '''
        pass 

    def plotSurfaceData(self, varName, timeIndex, regionName):
        '''
            Plot wind and wave forecasts dataset, including the following three variables:
            sig_wav_ht, together with the pk_wave_dir vector overlay;
            pk_wav_per, with pk_wav_dir vector overlay;
            and
            wnd_spd, with wnd_dir vector overlay.
        ''' 
        pass
