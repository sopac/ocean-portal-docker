from ocean.datasets import Dataset
import tide_stations as stations
import urllib
import urllib2
import json

class tideforecast(Dataset):
    PRODUCT_NAME = "Tide Forecast"
    BASE_URL = "http://www.bom.gov.au/australia/tides/scripts/getNextTides.php"
    
    __form_params__ = {
        'mode': str
    }
    
    __form_params__.update(Dataset.__form_params__)

    __required_params__ = Dataset.__required_params__ + [
    ]
    
    __periods__ = [
        'daily'
    ]
    
    __variables__ = [
        'tide'
    ]

    __plots__ = [
        'map'
    ]

    __subdirs__ = [
    ]
    
    def process(self, params):
        response = {}
        
        varStr = params['variable']
        periodStr = params['period']
        regionStr = params['area']
        
        station_list = stations.tide_stations
        
        for key, value in station_list.iteritems():
            values = {
                  "aac": value["station_number"],
                  "offset": "false",
                  "tz": value["timezone"]
                   }
            
            data = urllib.urlencode(values)
            full_url = self.BASE_URL + '?' + data
            
            try:
                response = urllib2.urlopen(full_url)
                content = response.read()
                d = json.loads(content)
                if d:
                    value["current_time"] =d["results"]["current_time"]
                    value["high_tide_height"] = d["results"]["next_high"]["height"]
                    value["low_tide_height"] = d["results"]["next_low"]["height"]
                    value["high_tide_time"] = d["results"]["next_high"]["time"]
                    value["low_tide_time"] = d["results"]["next_low"]["time"]
            except:
                response = station_list
                        
        response = station_list
        return response    
        