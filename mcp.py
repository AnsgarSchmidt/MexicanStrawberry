import ibmiotf.application
import json
import time
import sys

config = json.load(open("HAL/config.txt"))['iotf-service'][0]['credentials']

options = {
    "org"         : config['org'],
    "id"          : config['iotCredentialsIdentifier'],
    "auth-method" : "Token",
    "auth-key"    : config['apiKey'],
    "auth-token"  : config['apiToken']
}

def myEventCallback(event):
  str = "%s event '%s' received from device [%s]: %s"
  #print(str % (event.format, event.event, event.device, json.dumps(event.data)))
  global measurement
  measurement = event.data['v']
  print "%02.1f - Hum:%d - Hatch:%d - OUT:%d - IN%d" % (measurement['InsideSensorHumidity'],measurement['Humidifier'],measurement['Hatch'],measurement['FanOUT'],measurement['FanIN'])

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

def doit(hatch, humidifier, infan, outfan, stime):

    setHatch(hatch)

    if humidifier:
        setHumidifier(stime)
    else:
        setHumidifier(0)

    if infan:
        setINFan(stime)
    else:
        setINFan(0)

    if outfan:
        setOUTFan(stime)
    else:
        setOUTFan(0)

    time.sleep(stime)
    print "COOLDOWN"
    setHatch(1)
    setHumidifier(0)
    setINFan(200)
    setOUTFan(200)
    time.sleep(200)
    print "NEXT"

client = ibmiotf.application.Client(options)
client.connect()
client.deviceEventCallback = myEventCallback
client.deviceStatusCallback = myStatusCallback
client.subscribeToDeviceStatus()
client.subscribeToDeviceEvents(deviceId="Plant1")

time.sleep(5)
picture()
setINFan(10000)
time.sleep(1)
setHumidifier(3)
time.sleep(1)
sys.exit(1)

outfan = False
hum = False
hatch = False

for i in range(5000):

    h = measurement['InsideSensorHumidity']

    if not outfan and h > desired + 5:
        outfan = True

    if outfan and h < desired - 1:
        outfan = False

    if hum and h > desired:
        hum = False

    if not hum and h < desired - 2:
        hum = True

    if not hatch and h > desired + 0:
        hatch = True

    if hatch and h < desired - 0:
        hatch = False

    if outfan:
        setOUTFan(1)

    if hum:
        setHumidifier(1)

    if hatch:
        setHatch(1)
    else:
        setHatch(0)

    time.sleep(1)