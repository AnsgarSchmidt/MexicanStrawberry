import ibmiotf.application
import json
import time

config = json.load(open("HAL/config.txt"))['iotf-service'][0]['credentials']

options = {
    "org"         : config['org'],
    "id"          : config['iotCredentialsIdentifier'],
    "auth-method" : "Token",
    "auth-key"    : config['apiKey'],
    "auth-token"  : config['apiToken']
}

global hum
hum = 0

def myEventCallback(event):
    str = "%s event '%s' received from device [%s]: %s"
    #print(str % (event.format, event.event, event.device, json.dumps(event.data)))
    measurement = event.data['d']
    global hum
    hum = measurement['InsideHumidity']
    print "%02.1f - Hum:%d - Hatch:%1.1f - OUT:%d - IN%d" % (measurement['InsideHumidity'],measurement['Humidifier'],measurement['Hatch'],measurement['OutsideFan'],measurement['InsideFan'])

def myStatusCallback(status):
    if status.action == "Disconnect":
        str = "%s - device %s - %s (%s)"
        print(str % (status.time.isoformat(), status.device, status.action, status.reason))
    else:
        print("%s - %s - %s" % (status.time.isoformat(), status.device, status.action))

def picture():
    commandData = {'value': 7}
    client.publishCommand("RPi", "Plant1", "Picture", "json", commandData)
    time.sleep(1)

def setHatch(value):
    commandData = {'value': value}
    client.publishCommand("RPi", "Plant1", "Hatch", "json", commandData)
    time.sleep(1)

def setHumidifier(value):
    commandData = {'time': value}
    client.publishCommand("RPi", "Plant1", "Humidifier", "json", commandData)
    time.sleep(1)

def setINFan(value):
    commandData = {'time': value}
    client.publishCommand("RPi", "Plant1", "FanIN", "json", commandData)
    time.sleep(1)

def setOUTFan(value):
    commandData = {'time': value}
    client.publishCommand("RPi", "Plant1", "FanOUT", "json", commandData)
    time.sleep(1)

def setLightMovement(value):
    commandData = {'time': value}
    client.publishCommand("RPi", "Plant1", "Stepper", "json", commandData)
    time.sleep(1)

client = ibmiotf.application.Client(options)
client.connect()
client.deviceEventCallback  = myEventCallback
client.deviceStatusCallback = myStatusCallback
client.subscribeToDeviceStatus()
client.subscribeToDeviceEvents(deviceId="Plant1")

setLightMovement(1000)

sethum = 60.0

time.sleep(5)

while True:

    setLightMovement(100)

    if hum < sethum:
        setINFan(5)
        setHumidifier(10)
        time.sleep(20)

    if hum < (sethum+1):
        setHatch(0)

    if hum > (sethum+2):
        setHatch(1)

    if hum > (sethum + 5):
        setOUTFan(5)
        setINFan(6)
        time.sleep(10)

    time.sleep(1)