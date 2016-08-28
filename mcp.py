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
  print "%02.1f - Hum:%d - Hatch:%d - OUT:%d - IN%d" % (measurement['test1'],measurement['test2'],measurement['test2'],measurement['test4'],measurement['test5'])

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

client = ibmiotf.application.Client(options)
client.connect()
client.deviceEventCallback  = myEventCallback
client.deviceStatusCallback = myStatusCallback
client.subscribeToDeviceStatus()
client.subscribeToDeviceEvents(deviceId="dummyposter")

time.sleep(5)
