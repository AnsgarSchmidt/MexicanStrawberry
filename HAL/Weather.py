import threading
import json
import time
import urllib2
class Weather(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.credentials        = json.load(open("config.txt"))['weatherinsights'][0]['credentials']
        self.credentials['url'] = 'https://twcservice.mybluemix.net/api/weather/v1/geocode/52.52/13.4049/observations.json?language=en-US&units=m'
        self.pressure           = 0
        self.pressure_trent     = 0
        self.rh                 = 0
        self.precip_hrly        = 0
        self.precip_total       = 0
        self.uv_index           = 0
        self.start()

    def updateWeather(self):
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.credentials['url'], self.credentials['username'], self.credentials['password'])
        handler      = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener       = urllib2.build_opener(handler)
        f            = opener.open(self.credentials['url'])
        j            = json.loads(f.read())
        #print json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))
        self.pressure       = j['observation']['pressure']
        self.pressure_trent = j['observation']['pressure_tend']
        self.rh             = j['observation']['rh']
        self.precip_hrly    = j['observation']['precip_hrly']
        self.precip_total   = j['observation']['precip_total']
        self.uv_index       = j['observation']['uv_index']

    def getPressure(self):
        return self.pressure

    def getPressureTrent(self):
        return self.pressure_trent

    def getHumidity(self):
        return self.rh

    def getPrecipHrly(self):
        return self.precip_hrly

    def getPrecipTotal(self):
        return self.precip_total

    def getUV(self):
        return self.uv_index

    def run(self):
        while True:
            self.updateWeather()
            time.sleep(60*15) # 15 min

if __name__ == '__main__':
    w = Weather()
    w.start()
    time.sleep(5)
    print w.getPressure()
    print w.getPressureTrent()
    print w.getHumidity()
    print w.getPrecipHrly()
    print w.getPrecipTotal()
    print w.getUV()
