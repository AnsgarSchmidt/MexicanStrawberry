import ibmiotf.device
import time
import json

PIN_DALLAS         =  4
PIN_LED_1          =  7
PIN_LED_2          =  8
PIN_BUTTON_SILENCE = 12

def connectToIBM():
    client = ibmiotf.device.Client(json.load(open("clientconfig.txt")))
    client.connect()
    return client

def pushDataToIBM(client, measurements):
    measurements['test1'] = 42
    measurements['test2'] = 23
    measurements['test3'] = 234
    measurements['test4'] = 424
    measurements['test5'] = 23356
    data = {}
    data['d'] = measurements
    client.publishEvent("Plant1", "json", data)
    print "Data send:" + str(data)

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

    client = connectToIBM()
    client.commandCallback = commandCallback
    time.sleep(1)

    while True:
        m = {}
        pushDataToIBM(client, m)
        time.sleep(1)
