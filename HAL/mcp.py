import time
from IBMConnector import IBMConnector
from Dallas       import Dallas
from DHT          import DHT

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

    iotfClient       = IBMConnector(commandCallback)
    waterTemperature = Dallas()
    airInside        = DHT(23)
    airOutside       = DHT(24)

    while True:
        m = {}
        m['Watertemperature']   = waterTemperature.getWaterTemp()
        m['InsideHumidity']     = airInside.getHumidity()
        m['InsideTemperature']  = airInside.getTemperature()
        m['OutsideHumidity']    = airOutside.getHumidity()
        m['OutsideTemperature'] = airOutside.getTemperature()
        iotfClient.pushDataToIBM(m)
        time.sleep(1)
