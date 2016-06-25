import ibmiotf.device
import time
import json
#import RPi.GPIO as GPIO
#import Adafruit_DHT

class mcp():

    def __init__(self):
        self.measurements = {}
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(12, GPIO.OUT)
        #GPIO.output(12, False)
        #sensor = Adafruit_DHT.DHT22

    def connectToIBMForPush(self):
        try:
            self.client = ibmiotf.device.Client(json.load(open("config.txt")))
            self.client.connect()
            print "Connected to IBM for pushing"
        except e:
            print "Error connecting IBM:%s" % str(e)

    def pushData(self):
        self.measurements['test'] = 89
        self.client.publishEvent("Plant1", "json", self.measurements)
        print "Data send:" + str(self.measurements)

    def getCPUTemp(self):
        self.measurements['CPU-Temp'] = 22.4

    def getGPUTemp(self):
        self.measurements['GPU-Temp'] = 33.4

    def getLoadLevel(self):
        self.measurements['LoadLevel'] = 2.23

    def getTempAndHumidity(self):
        humidity, temperature = Adafruit_DHT.read_retry(22, 4)
        self.measurements['ENV-Temp'] = temperature
        self.measurements['ENV-Humidity'] = humidity

    def gatherDate(self):
        self.getCPUTemp()
        self.getGPUTemp()
        self.getLoadLevel()

    def setFan(self, value):
        GPIO.output(12, value)

if __name__ == '__main__':
    print "Running"
    m = mcp()
    m.connectToIBMForPush()
    m.gatherDate()
    for i in range(2):
        m.pushData()
        time.sleep(1)