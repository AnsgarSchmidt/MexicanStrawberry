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

def myEventCallback(event):
  str = "%s event '%s' received from device [%s]: %s"
  #print(str % (event.format, event.event, event.device, json.dumps(event.data)))
  measurement = event.data['d']
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

def setHatch(value):
    commandData = {'value': value}
    client.publishCommand("RPi", "Plant1", "Hatch", "json", commandData)

def setHumidifier(value):
    commandData = {'time': value}
    client.publishCommand("RPi", "Plant1", "Humidifier", "json", commandData)

def setINFan(value):
    commandData = {'time': value}
    client.publishCommand("RPi", "Plant1", "FanIN", "json", commandData)

def setOUTFan(value):
    commandData = {'time': value}
    client.publishCommand("RPi", "Plant1", "FanOUT", "json", commandData)

client = ibmiotf.application.Client(options)
client.connect()
client.deviceEventCallback  = myEventCallback
client.deviceStatusCallback = myStatusCallback
client.subscribeToDeviceStatus()
client.subscribeToDeviceEvents(deviceId="Plant1")

time.sleep(1)

for i in range(10):
    setHatch(0.1 * i)
    time.sleep(1)

setOUTFan(5)
time.sleep(2)
setINFan(6)
time.sleep(2)
setHumidifier(2)

time.sleep(10)
