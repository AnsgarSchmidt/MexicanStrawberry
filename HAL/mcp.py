import threading
import time
import json
import datetime
import ibmiotf.device
import RPi.GPIO as GPIO
import Adafruit_DHT
import glob
import sys
import os
import wiringpi
import picamera
import json
import time
import swiftclient
import datetime

class Picture(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.camera = picamera.PiCamera()
        self.makepic = False

    def makePicture(self):
        self.makepic = True

    def run(self):
        while True:
            if self.makepic:
                camera.capture('image.jpg')
                self.makepic = False

class WaterTemp(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        self.temp_c = 0

    def read_temp_raw(self):
        f = open('/sys/bus/w1/devices/28-001454a22eff/w1_slave', 'r')
        lines = f.readlines()
        f.close()

    def aquireWaterTemp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            self.temp_c = float(temp_string) / 1000.0

    def getWaterTemp(self):
        return self.temp_c

    def run(self):
        while True:
            self.aquireWaterTemp()
            time.sleep(0.25)

class SystemData(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.cpu_temp   = 0
        self.gpu_temp   = 0
        self.cpu_use    = 0
        self.load_level = 0

    def getCPUTemp(self):
        return self.cpu_temp

    def getGPUTemp(self):
        return self.gpu_temp

    def getCPUuse(self):
        return self.cpu_use

    def getLoadLevel(self):
        return self.load_level

    def aquireData(self):
        # CPU Temp
        tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
        cpu_temp = tempFile.read()
        tempFile.close()
        self.cpu_temp = float(cpu_temp)/1000
        #GPU Temp
        res = os.popen('vcgencmd measure_temp').readline()
        self.gpu_temp = float(res.replace("temp=","").replace("'C\n",""))
        #CPU use
        use = os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
            )
        self.cpu_use = float(use)
        #LoadLevel
        ll = os.popen("uptime | cut -d \":\"  -f 4 | cut -d \",\" -f 1").readline().strip()
        self.load_level = float(ll)
        time.sleep(0.25)

    def run(self):
        while True:
            self.aquireData()
            time.sleep(0.25)

class OutsideSensor(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.temperature = 0
        self.humidity    = 0

    def getTemperature(self):
        return self.temperature

    def getHumidity(self):
        return self.humidity

    def run(self):
        while True:
            self.humidity, self.temperature = Adafruit_DHT.read_retry(22, 23)
            time.sleep(0.25)

class InsideSensor(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def getTemperature(self):
        return self.humidity

    def getHumidity(self):
        return self.temperature

    def run(self):
        while True:
            self.humidity, self.temperature = Adafruit_DHT.read_retry(22, 24)
            time.sleep(0.25)

def connectToIBM():
    client = ibmiotf.device.Client(json.load(open("clientconfig.txt")))
    client.connect()
    return client

def pushDataToIBM(data):
    pass

def persistData(data):
    pass

if __name__ == '__main__':
    print "MS HAL"

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(14, GPIO.OUT)  # LED1
    GPIO.setup(15, GPIO.OUT)  # LED2
    # GPIO.setup(18, GPIO.OUT) # SERVO
    # GPIO.setup(23, GPIO.OUT) # DHT OUT
    # GPIO.setup(24, GPIO.OUT) # DHT IN
    GPIO.setup(25, GPIO.OUT)  # HUMIDITY
    GPIO.setup(8, GPIO.OUT)  # FAN1
    GPIO.setup(7, GPIO.OUT)  # FAN2

    GPIO.output(14, False)
    GPIO.output(15, False)
    # GPIO.output(18, False)
    # GPIO.output(23, False)
    # GPIO.output(24, False)
    GPIO.output(25, False)
    GPIO.output(8, False)
    GPIO.output(7, False)

    os.popen("gpio mode 1 pwm")
    os.popen("gpio pwm-ms")
    os.popen("gpio pwmc 1920")
    os.popen("gpio pwmr 200")

    client = connectToIBM()
    # client.commandCallback = self.myCommandCallback

    waterTemp = WaterTemp()
    waterTemp.setDaemon(True)
    waterTemp.start()

    systemData = SystemData()
    systemData.setDaemon(True)
    systemData.start()

    outsideSensor = OutsideSensor()
    outsideSensor.setDaemon(True)
    outsideSensor.start()

    insideSensor = InsideSensor()
    insideSensor.setDaemon(True)
    insideSensor.start()

    picture = Picture()
    picture.setDaemon(True)
    picture.start()

    measurements = {}

    for i in range(10):
        print "Tick"

        measurements['Timestamp']                = time.time()
        measurements['WaterTemp']                = waterTemp.getWaterTemp()
        measurements['SystemCPUTemp']            = systemData.getCPUTemp()
        measurements['SystemGPUTemp']            = systemData.getGPUTemp()
        measurements['SystemLoadLevel']          = systemData.getLoadLevel()
        measurements['SystemCPUUse']             = systemData.getCPUuse()
        measurements['OutsideSensorTemperature'] = outsideSensor.getTemperature()
        measurements['OutsideSensorHumidity']    = outsideSensor.getHumidity()
        measurements['InsideSensorTemperature']  = insideSensor.getTemperature()
        measurements['InsideSensorHumidity']     = insideSensor.getHumidity()

        pushDataToIBM(measurements)
        persistData(measurements)
        time.sleep(1)