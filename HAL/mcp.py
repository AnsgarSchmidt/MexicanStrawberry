import time
import datetime
from IBMConnector import IBMConnector
from Dallas       import Dallas
from DHT          import DHT
from SystemData   import SystemData
from Weather      import Weather
from CSVPersistor import CSVPersistor

def commandCallback(cmd):
        print("Command received: %s" % cmd.command)
        if cmd.command == "FanIN":
            if 'time' not in cmd.data:
                print("Error - FanIN is missing required information: 'time'")
            else:
                pass

        elif cmd.command == "FanOUT":
            if 'time' not in cmd.data:
                print("Error - FanOUT is missing required information: 'time'")
            else:
                pass

        elif cmd.command == "Humidifier":
            if 'time' not in cmd.data:
                print("Error - Humidifier is missing required information: 'time'")
            else:
                pass

        elif cmd.command == "Hatch":
            if 'value' not in cmd.data:
                print("Error - Hatch is missing required information: 'value'")
            else:
                if cmd.data['value'] >= 0 and cmd.data['value'] <= 1:
                    pass

        elif cmd.command == "Picture":
            pass

        else:
            print "Unknown command"
            print(cmd.command)

if __name__ == '__main__':
    print "MS HAL start"

    #Connectors
    iotfClient       = IBMConnector(commandCallback)
    time.sleep(1)
    csvPersistor     = CSVPersistor("Plant1")
    time.sleep(1)

    #Sensors
    waterTemperature = Dallas()
    time.sleep(1)
    airInside        = DHT(23)
    time.sleep(1)
    airOutside       = DHT(24)
    time.sleep(1)
    systemData       = SystemData()
    time.sleep(1)
    weather          = Weather()
    time.sleep(1)

    while True:
        now = datetime.datetime.now()
        m = {}
        m['Timestamp']               = "%d-%d-%d-%d-%d-%d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        m['Watertemperature']        = waterTemperature.getWaterTemp()
        m['InsideHumidity']          = airInside.getHumidity()
        m['InsideTemperature']       = airInside.getTemperature()
        m['OutsideHumidity']         = airOutside.getHumidity()
        m['OutsideTemperature']      = airOutside.getTemperature()
        m['CPUTemperature']          = systemData.getCPUTemp()
        m['GPUTemperature']          = systemData.getGPUTemp()
        m['CPUUsage']                = systemData.getCPUuse()
        m['Loadlevel']               = systemData.getLoadLevel()
        m['WeatherHumidity']         = weather.getHumidity()
        m['WeatherPressure']         = weather.getPressure()
        m['WeatherPressureTrent']    = weather.getPressureTrent()
        m['WeatherUV']               = weather.getUV()
        m['WeatherPreciptionTotal']  = weather.getPrecipTotal()
        m['WeatherPreciptionHourly'] = weather.getPrecipHrly()

        iotfClient.pushDataToIBM(m)
        csvPersistor.persist(m)
        time.sleep(1)
