import os 
import ibmiotf.device
import time
import json
import RPi.GPIO as GPIO
import Adafruit_DHT
import glob
import sys
import wiringpi

class mcp():

    def __init__(self):
        self.measurements = {}
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(14, GPIO.OUT) # LED1 
        GPIO.setup(15, GPIO.OUT) # LED2
        #GPIO.setup(18, GPIO.OUT) # SERVO
        #GPIO.setup(23, GPIO.OUT) # DHT OUT
        #GPIO.setup(24, GPIO.OUT) # DHT IN
        GPIO.setup(25, GPIO.OUT) # HUMIDITY
        GPIO.setup( 8, GPIO.OUT) # FAN1
        GPIO.setup( 7, GPIO.OUT) # FAN2

        GPIO.output(14, False)
        GPIO.output(15, False)
        #GPIO.output(18, False)
        #GPIO.output(23, False)
        #GPIO.output(24, False)
        GPIO.output(25, False)
        GPIO.output( 8, False)
        GPIO.output( 7, False)

        os.popen("gpio mode 1 pwm")	    
        os.popen("gpio pwm-ms")
        os.popen("gpio pwmc 1920")
        os.popen("gpio pwmr 200")

        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        # hard pwm controll
        # $ gpio mode 1 pwm
        # $ gpio pwm-ms
        # $ gpio pwmc 1920
        # $ gpio pwmr 200     # 0.1 ms per unit
        # $ gpio pwm 1 15     # 1.5 ms (0)
        # $ gpio pwm 1 20     # 2.0 ms (+90)
        # $ gpio pwm 1 10     # 1.0 ms (-90)
  
    def setHatch(self, value):
        value += 10
        os.popen("gpio pwm 1 %s"% value)	

    def connectToIBMForPush(self):
        self.client = ibmiotf.device.Client(json.load(open("config.txt")))
        self.client.connect()
        print "Connected to IBM for pushing"
        self.client.commandCallback = self.myCommandCallback

    def myCommandCallback(self, cmd):
        print("Command received: %s" % cmd.data)
        if cmd.command == "Fan":
            if 'speed' not in cmd.data:
                print("Error - command is missing required information: 'interval'")
            else:
                if cmd.data['speed'] > 0:
            self.setFan(True)
                else:
                    self.setFan(False)
        elif cmd.command == "Hum":
            if 'intense' not in cmd.data:
                print("Error - command is missing required information: 'message'")
            else:
                if cmd.data['intense'] > 0:
                    self.setHumidifier(True)                
                else:
                    self.setHumidifier(False)
        elif cmd.command == "Hatch":
            if 'value' not in cmd.data:
                print("Error - command is missing required information: 'message'")
            else:
                if cmd.data['value'] >= 0 and cmd.data['value'] <11:
                    self.setHatch(cmd.data['value'])
        else:
            print(cmd.command)

    def pushData(self):
        self.measurements['test'] = 42
        data = {}
        data['v'] = self.measurements
        self.client.publishEvent("Plant1", "json", data)
        print "Data send:" + str(data)

    def read_temp_raw(self):
        f = open('/sys/bus/w1/devices/28-001454a22eff/w1_slave', 'r')
        lines = f.readlines()
        f.close()
        return lines
 
    def getWaterTemp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            self.measurements['WATER-Temp'] = temp_c

    def getGPUTemp(self):
        res = os.popen('vcgencmd measure_temp').readline()
        self.measurements['GPU-Temp'] = float(res.replace("temp=","").replace("'C\n",""))

    def getCPUuse(self):
        use = os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
)
    self.measurements['CPUuse'] = float(use)

    def getCPUTemp(self):
        tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )  
        cpu_temp = tempFile.read()  
        tempFile.close()  
        self.measurements['CPU-Temp'] = float(cpu_temp)/1000 

    def setLedIN(self, value):
        GPIO.output(14, value)

    def setLedOUT(self, value):
        GPIO.output(15, value)

    def getLoadLevel(self):
        ll = os.popen("uptime | cut -d \":\"  -f 4 | cut -d \",\" -f 1").readline().strip()
        self.measurements['LoadLevel'] = float(ll) 

    def getTempAndHumidityOUT(self):
        humidity, temperature = Adafruit_DHT.read_retry(22, 23)
        self.measurements['ENV-Temp'] = temperature
        self.measurements['ENV-Humidity'] = humidity

    def getTempAndHumidityIN(self):
        humidity, temperature = Adafruit_DHT.read_retry(22, 24)
        self.measurements['PROBE-Temp'] = temperature
        self.measurements['PROBE-Humidity'] = humidity

    def gatherData(self):
        self.getCPUTemp()
        self.getGPUTemp()
        self.getLoadLevel()
        self.getCPUuse()
        self.getWaterTemp()
        self.getTempAndHumidityOUT()
        self.getTempAndHumidityIN()

    def setINFan(self, value):
        GPIO.output(7, value)

    def setOUTFan(self, value):
        GPIO.output(8, value)

    def setHumidifier(self, value):
        GPIO.output(25, value)

if __name__ == '__main__':
    print "Running"
    m = mcp()
    m.connectToIBMForPush()
   
    while True:
        m.gatherData()
        m.pushData()
        time.sleep(1)
