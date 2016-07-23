import threading
import time
import json
import Queue
import datetime
import ibmiotf.device
import RPi.GPIO as GPIO
import Adafruit_DHT
import glob
import sys
import csv
import os
import wiringpi
import picamera
import json
import time
import swiftclient
import datetime
import json
import urllib2

PIN_DALLAS      =  4
PIN_LED_1       =  7
PIN_LED_2       =  8
PIN_BUTTON      = 12
PIN_HUMIDIFIER  = 16
PIN_ENABLE      = 17
PIN_SERVO       = 18
PIN_FAN_1       = 20
PIN_FAN_2       = 21
PIN_DIRECTION   = 22
PIN_INSIDE_AIR  = 23
PIN_OUTSIDE_AIR = 24
PIN_STEPPEN_END = 25
PIN_STEP        = 27

class Picture(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.camera = picamera.PiCamera()
        self.makepic = False
        self.container_name = 'MexicanStrawberryPictures'

        objectstorage_creds = json.load(open("config.txt"))['Object-Storage'][0]['credentials']

        if objectstorage_creds:
            auth_url = objectstorage_creds['auth_url'] + '/v3'  # authorization URL
            password = objectstorage_creds['password']  # password
            project_id = objectstorage_creds['projectId']  # project id
            user_id = objectstorage_creds['userId']  # user id
            region_name = objectstorage_creds['region']  # region name

        conn = swiftclient.Connection(key=password,
                                       authurl=auth_url,
                                       auth_version='3',
                                       os_options={"project_id": project_id,
                                                   "user_id": user_id,
                                                   "region_name": region_name})


        exists = False

        for i in conn.get_account()[1]:
            if i['name'] == self.container_name:
                exists = True

        if not exists:
            conn.put_container(self.container_name)
            print "Creating container"

        conn.close()

    def makePicture(self):
        self.makepic = True

    def run(self):
        while True:
            if self.makepic:
                self.makepic = False
                now = datetime.datetime.now()
                file_name = "%d-%d-%d-%d-%d-%d.jpg" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
                self.camera.capture(file_name)

                objectstorage_creds = json.load(open("config.txt"))['Object-Storage'][0]['credentials']

                if objectstorage_creds:
                    auth_url = objectstorage_creds['auth_url'] + '/v3'  # authorization URL
                    password = objectstorage_creds['password']  # password
                    project_id = objectstorage_creds['projectId']  # project id
                    user_id = objectstorage_creds['userId']  # user id
                    region_name = objectstorage_creds['region']  # region name

                conn = swiftclient.Connection(key=password,
                                              authurl=auth_url,
                                              auth_version='3',
                                              os_options={"project_id": project_id,
                                                          "user_id": user_id,
                                                          "region_name": region_name})

                with open(file_name, 'r') as file:
                    conn.put_object(self.container_name, file_name,
                                    contents=file.read(),
                                    content_type='image/jpeg')
                conn.close()
                os.remove(file_name)
                print "Update done"
            time.sleep(1)

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
        return lines

    def aquireWaterTemp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            self.temp_c = float(temp_string) / 1000.0

    def getWaterTemp(self):
        return self.temp_c

    def run(self):
        while True:
            self.aquireWaterTemp()
            time.sleep(1)

class SystemData(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cpu_temp = 0
        self.gpu_temp = 0
        self.cpu_use = 0
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
        tempFile = open("/sys/class/thermal/thermal_zone0/temp")
        cpu_temp = tempFile.read()
        tempFile.close()
        self.cpu_temp = float(cpu_temp) / 1000
        # GPU Temp
        res = os.popen('vcgencmd measure_temp').readline()
        self.gpu_temp = float(res.replace("temp=", "").replace("'C\n", ""))
        # CPU use
        use = os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip( \
            )
        self.cpu_use = float(use)
        # LoadLevel
        #ll = os.popen("uptime | cut -d \":\"  -f 5 | cut -d \",\" -f 1").readline().strip()
        #self.load_level = float(ll)
        time.sleep(1)

    def run(self):
        while True:
            self.aquireData()
            time.sleep(1)

class OutsideSensor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.temperature = 0
        self.humidity = 0

    def getTemperature(self):
        return self.temperature

    def getHumidity(self):
        return self.humidity

    def run(self):
        while True:
            self.humidity, self.temperature = Adafruit_DHT.read_retry(22, PIN_OUTSIDE_AIR)
            time.sleep(1)

class InsideSensor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.humidity = 0
        self.temperature = 0

    def getTemperature(self):
        return self.temperature

    def getHumidity(self):
        return self.humidity

    def run(self):
        while True:
            self.humidity, self.temperature = Adafruit_DHT.read_retry(22, PIN_INSIDE_AIR)
            time.sleep(1)

class Persistor(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.q = Queue.Queue()
        self.container_name = 'MexicanStrawberry'

        objectstorage_creds = json.load(open("config.txt"))['Object-Storage'][0]['credentials']

        if objectstorage_creds:
            auth_url = objectstorage_creds['auth_url'] + '/v3'  # authorization URL
            password = objectstorage_creds['password']  # password
            project_id = objectstorage_creds['projectId']  # project id
            user_id = objectstorage_creds['userId']  # user id
            region_name = objectstorage_creds['region']  # region name

        conn = swiftclient.Connection(key=password,
                                      authurl=auth_url,
                                      auth_version='3',
                                      os_options={"project_id": project_id,
                                                  "user_id": user_id,
                                                  "region_name": region_name})
        exists = False

        for i in conn.get_account()[1]:
            if i['name'] == self.container_name:
                exists = True

        if not exists:
            conn.put_container(self.container_name)
            print "Creating container"

        conn.close()

        now = datetime.datetime.now()
        self.file_name = "%d-%d-%d-%d.csv" % (now.year, now.month, now.day, now.hour)

    def persist(self, measurements):
        self.q.put(measurements)

    def run(self):
        while True:
            now = datetime.datetime.now()
            file_name = "%d-%d-%d-%d.csv" % (now.year, now.month, now.day, now.hour)
            if file_name != self.file_name:
                # upload old file
                print "new file, upload old"

                objectstorage_creds = json.load(open("config.txt"))['Object-Storage'][0]['credentials']

                if objectstorage_creds:
                    auth_url = objectstorage_creds['auth_url'] + '/v3'  # authorization URL
                    password = objectstorage_creds['password']  # password
                    project_id = objectstorage_creds['projectId']  # project id
                    user_id = objectstorage_creds['userId']  # user id
                    region_name = objectstorage_creds['region']  # region name

                conn = swiftclient.Connection(key=password,
                                              authurl=auth_url,
                                              auth_version='3',
                                              os_options={"project_id": project_id,
                                                          "user_id": user_id,
                                                          "region_name": region_name})

                with open(self.file_name, 'r') as file:
                    conn.put_object(self.container_name, self.file_name,
                                    contents=file.read(),
                                    content_type='text/plain')
                conn.close()
                os.remove(self.file_name)
                self.file_name = file_name
                with open(self.file_name, 'ab') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',')
                    d = ['Timestamp','WaterTemp','SystemCPUTemp','SystemGPUTemp','SystemLoadLevel','SystemCPUUse',
                        'OutsideSensorTemperature','OutsideSensorHumidity','InsideSensorTemperature',
                        'InsideSensorHumidity','FanIN', 'FanOUT', 'Humidifier','Hatch', 'SidePressure',
                        'SidePressureTrent', 'SideHumidity', 'SidePreciptionHourly', 'SidePreciptionTotal',
                        'SideUV'
                    ]
                    spamwriter.writerow(d)
            if not self.q.empty():
                m = self.q.get()
                with open(self.file_name, 'ab') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',')
                    d = [
                        measurements['Timestamp'],
                        measurements['WaterTemp'],
                        measurements['SystemCPUTemp'],
                        measurements['SystemGPUTemp'],
                        measurements['SystemLoadLevel'],
                        measurements['SystemCPUUse'],
                        measurements['OutsideSensorTemperature'],
                        measurements['OutsideSensorHumidity'],
                        measurements['InsideSensorTemperature'],
                        measurements['InsideSensorHumidity'],
                        measurements['FanIN'],
                        measurements['FanOUT'],
                        measurements['Humidifier'],
                        measurements['Hatch'],
                        measurements['SidePressure'],
                        measurements['SidePressureTrent'],
                        measurements['SideHumidity'],
                        measurements['SidePreciptionHourly'],
                        measurements['SidePreciptionTotal'],
                        measurements['SideUV']
                    ]
                    spamwriter.writerow(d)
                self.q.task_done()

            time.sleep(0.5)

class FanIN(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.timeToKeepOn = 0
        self.status = 0

    def setTime(self, timeToAdd):
        self.timeToKeepOn = time.time() + timeToAdd

    def getState(self):
        return self.status

    def run(self):
        while True:
            if self.timeToKeepOn > time.time():
                GPIO.output(PIN_FAN_1, True)
                self.status = 1
            else:
                GPIO.output(PIN_FAN_1, False)
                self.status = 0
            time.sleep(1)

class FanOUT(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.timeToKeepOn = 0
        self.status = 0

    def setTime(self, timeToAdd):
        self.timeToKeepOn = time.time() + timeToAdd

    def getState(self):
        return self.status

    def run(self):
        while True:
            if self.timeToKeepOn > time.time():
                GPIO.output(PIN_FAN_2, True)
                self.status = 1
            else:
                GPIO.output(PIN_FAN_2, False)
                self.status = 0
            time.sleep(1)

class Humidity(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.timeToKeepOn = 0
        self.status = 0

    def setTime(self, timeToAdd):
        self.timeToKeepOn = time.time() + timeToAdd

    def getState(self):
        return self.status

    def run(self):
        while True:
            if self.timeToKeepOn > time.time():
                GPIO.output(PIN_HUMIDIFIER, True)
                self.status = 1
            else:
                GPIO.output(PIN_HUMIDIFIER, False)
                self.status = 0
            time.sleep(1)

class Stepper(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.timeToKeepOn =   0
        self.status       =   0 # 0->OFF 1->CW 2->CCW
        self.counter      =  -1 # -1 undefined so we need to calibrate
        self.MAX          = 100 # Max steps in one direction
        GPIO.output(PIN_ENABLE,    True ) # inverted
        GPIO.output(PIN_DIRECTION, False)
        GPIO.output(PIN_STEP,      False)
        self.calibrate()

    def calibrate(self):
        self.counter = 0

    def setTime(self, timeToAdd):
        self.timeToKeepOn = time.time() + timeToAdd

    def getState(self):
        return self.status

    def run(self):
        while True:

            if self.counter == -1:
                continue

            if self.timeToKeepOn > time.time():
                GPIO.output(PIN_ENABLE, True)
                if self.counter >= 0 and self.counter < self.MAX:

                self.status = 1
            else:
                GPIO.output(PIN_ENABLE, False)
                self.status = 0
                time.sleep(1) # wait for a longer time when off

class Hatch():

    def __init__(self):
        self.hatch = 0

    def getHatch(self):
        return self.hatch

    def setHatch(self, value):
        # 19 zu
        # 16 halb
        # 13 offen
        if value >= 0 and value <= 1:
            self.hatch = value
            v = ((19 - 13) * (1 - value)) + 13
            os.popen("gpio pwm 1 %s" % int(v))

class Weather(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.credentials = json.load(open("config.txt"))['weatherinsights'][0]['credentials']
        self.credentials['url'] = 'https://twcservice.mybluemix.net/api/weather/v1/geocode/52.52/13.4049/observations.json?language=en-US&units=m'
        self.pressure = 0
        self.pressure_trent = 0
        self.rh = 0
        self.precip_hrly = 0
        self.precip_total = 0
        self.uv_index = 0

    def updateWeather(self):
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.credentials['url'], self.credentials['username'], self.credentials['password'])
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener  = urllib2.build_opener(handler)
        f       = opener.open(self.credentials['url'])
        j       = json.loads(f.read())
        #print json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))
        self.pressure       = j['observation']['pressure']
        self.pressure_trent = j['observation']['pressure_tend']
        self.rh             =  j['observation']['rh']
        self.precip_hrly    = j['observation']['precip_hrly']
        self.precip_total   = j['observation']['precip_total']
        self.uv_index       = j['observation']['uv_index']

    def getPressure(self):
        return self.pressure

    def getPressureTrent(self):
        return self.pressure_trent

    def getHumidity(self):
        return self.rh

    def getPrecipHrly(self):
        return self.precip_hrly

    def getPrecipTotal(self):
        return self.precip_total

    def getUV(self):
        return self.uv_index

    def run(self):
        while True:
            self.updateWeather()
            time.sleep(60*10)

def connectToIBM():
    client = ibmiotf.device.Client(json.load(open("clientconfig.txt")))
    client.connect()
    return client

def pushDataToIBM(client, measurements):
    measurements['test'] = 42
    data = {}
    data['v'] = measurements
    client.publishEvent("Plant1", "json", data)
    #print "Data send:" + str(data)

def setLedIN(value):
    GPIO.output(PIN_LED_1, value)

def setLedOUT(value):
    GPIO.output(PIN_LED_2, value)

def commandCallback(cmd):
        print("Command received: %s" % cmd.command)
        if cmd.command == "FanIN":
            if 'time' not in cmd.data:
                print("Error - FanIN is missing required information: 'time'")
            else:
                if cmd.data['time'] > 0:
                    fanIN.setTime(int(cmd.data['time']))

        elif cmd.command == "FanOUT":
            if 'time' not in cmd.data:
                print("Error - FanOUT is missing required information: 'time'")
            else:
                if cmd.data['time'] > 0:
                    fanOUT.setTime(int(cmd.data['time']))

        elif cmd.command == "Humidifier":
            if 'time' not in cmd.data:
                print("Error - Humidifier is missing required information: 'time'")
            else:
                if cmd.data['time'] > 0:
                    humidity.setTime(int(cmd.data['time']))

        elif cmd.command == "Hatch":
            if 'value' not in cmd.data:
                print("Error - Hatch is missing required information: 'value'")
            else:
                if cmd.data['value'] >= 0 and cmd.data['value'] <= 1:
                    hatch.setHatch(cmd.data['value'])

        elif cmd.command == "Picture":
            picture.makePicture()

        else:
            print "Unknown command"
            print(cmd.command)

if __name__ == '__main__':
    print "MS HAL start"

    global measurements
    measurements = {}

    print " 1.Setting GPIOs"
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    # GPIO.setup(PIN_DALLAS,      GPIO.IN)
    GPIO.setup(PIN_ENABLE,        GPIO.OUT)
    GPIO.setup(PIN_STEP,          GPIO.OUT)
    GPIO.setup(PIN_DIRECTION,     GPIO.OUT)
    GPIO.setup(PIN_STEPPEN_END,   GPIO.IN )
    # GPIO.setup(PIN_SERVO,       GPIO.OUT)
    # GPIO.setup(PIN_OUTSIDE_AIR, GPIO.OUT)
    # GPIO.setup(PIN_INSIDE_AIR,  GPIO.OUT)
    GPIO.setup(PIN_LED_1,         GPIO.OUT)
    GPIO.setup(PIN_LED_2,         GPIO.OUT)
    GPIO.setup(PIN_BUTTON,        GPIO.IN )
    GPIO.setup(PIN_HUMIDIFIER,    GPIO.OUT)
    GPIO.setup(PIN_FAN_1,         GPIO.OUT)
    GPIO.setup(PIN_FAN_2,         GPIO.OUT)
    time.sleep(1)

    print " 2. Setting pwm"
    os.popen("gpio mode 1 pwm")
    os.popen("gpio pwm-ms")
    os.popen("gpio pwmc 1920")
    os.popen("gpio pwmr 200")
    time.sleep(1)

    print " 3. Starting Watertemp Thread"
    waterTemp = WaterTemp()
    waterTemp.setDaemon(True)
    waterTemp.start()
    time.sleep(1)

    print " 4. Starting Systemdata Thread"
    systemData = SystemData()
    systemData.setDaemon(True)
    systemData.start()
    time.sleep(1)

    print " 5. Starting OutsideSensor Thread"
    outsideSensor = OutsideSensor()
    outsideSensor.setDaemon(True)
    outsideSensor.start()
    time.sleep(1)

    print " 6. Starting InsideSensor Thread"
    insideSensor = InsideSensor()
    insideSensor.setDaemon(True)
    insideSensor.start()
    time.sleep(1)

    print " 7. Starting Picture Thread"
    picture = Picture()
    picture.setDaemon(True)
    picture.start()
    time.sleep(1)

    print " 8. Starting Persistor Thread"
    persistor = Persistor()
    persistor.setDaemon(True)
    persistor.start()
    time.sleep(1)

    print " 9. Starting INFan Thread"
    fanIN = FanIN()
    fanIN.setDaemon(True)
    fanIN.start()
    time.sleep(1)

    print "10. Starting OutFan Thread"
    fanOUT = FanOUT()
    fanOUT.setDaemon(True)
    fanOUT.start()
    time.sleep(1)

    print "11. Starting Humidifier Thread"
    humidity = Humidity()
    humidity.setDaemon(True)
    humidity.start()
    time.sleep(1)

    print "12. Starting Weather Thread"
    weather = Weather()
    weather.setDaemon(True)
    weather.start()
    time.sleep(1)

    print "13. Starting Hatch"
    hatch = Hatch()
    time.sleep(1)

    print "14. Starting Watertemp Thread"
    client = connectToIBM()
    client.commandCallback = commandCallback
    time.sleep(1)

    print "15. Starting MainLoop"
    while True:
        measurements['Timestamp'] = time.time()
        measurements['WaterTemp'] = waterTemp.getWaterTemp()
        measurements['SystemCPUTemp'] = systemData.getCPUTemp()
        measurements['SystemGPUTemp'] = systemData.getGPUTemp()
        measurements['SystemLoadLevel'] = systemData.getLoadLevel()
        measurements['SystemCPUUse'] = systemData.getCPUuse()
        measurements['OutsideSensorTemperature'] = outsideSensor.getTemperature()
        measurements['OutsideSensorHumidity'] = outsideSensor.getHumidity()
        measurements['InsideSensorTemperature'] = insideSensor.getTemperature()
        measurements['InsideSensorHumidity'] = insideSensor.getHumidity()
        measurements['FanIN'] = fanIN.getState()
        measurements['FanOUT'] = fanOUT.getState()
        measurements['Humidifier'] = humidity.getState()
        measurements['Hatch'] = hatch.getHatch()
        measurements['SidePressure'] = weather.getPressure()
        measurements['SidePressureTrent'] = weather.getPressureTrent()
        measurements['SideHumidity'] = weather.getHumidity()
        measurements['SidePreciptionHourly'] = weather.getPrecipHrly()
        measurements['SidePreciptionTotal'] = weather.getPrecipTotal()
        measurements['SideUV'] = weather.getUV()

        pushDataToIBM(client, measurements)
        persistor.persist(measurements)
        time.sleep(1)
