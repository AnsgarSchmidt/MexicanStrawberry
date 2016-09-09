import time
import datetime
import RPi.GPIO           as     GPIO
from IBMConnector         import IBMConnector
from Dallas               import Dallas
from DHT                  import DHT
from SystemData           import SystemData
from Weather              import Weather
from CSVPersistor         import CSVPersistor
from TimedDigitalActuator import TimedDigitalActuator
from Hatch                import Hatch
from Picture              import Picture
from Stepper              import Stepper

def commandCallback(cmd):

        print("Command received: %s with data: %s" % (cmd.command, cmd.data.d.value))

        if alloff:
            return

        if cmd.command == "InsideFan":
            insideFan.setTime(cmd.data.d.value)

        elif cmd.command == "OutsideFan":
            outsideFan.setTime(cmd.data.d.value)

        elif cmd.command == "Humidifier":
            humidifier.setTime(cmd.data.d.value)

        elif cmd.command == "Hatch":
            if cmd.data >= 0 and cmd.data <= 1:
                hatch.setHatch(cmd.data.d.value)

        elif cmd.command == "Stepper":
            stepper.setTime(cmd.data.d.value)

        elif cmd.command == "Picture":
            picture.makePicture()

        else:
            print "Unknown command"
            print(cmd.command)

if __name__ == '__main__':
    print "MS HAL start"

    #Connectors
    iotfClient       = IBMConnector(commandCallback)
    time.sleep(2)
    csvPersistor     = CSVPersistor("Plant1")
    time.sleep(1)

    #Sensors
    waterTemperature = Dallas()
    time.sleep(1)
    airInside        = DHT(23)
    time.sleep(1)
    airOutside       = DHT(24)
    time.sleep(1)
    systemData       = SystemData()
    time.sleep(1)
    weather          = Weather()
    time.sleep(1)

    #Actuators
    outsideFan = TimedDigitalActuator(20)
    time.sleep(1)
    insideFan  = TimedDigitalActuator(21)
    time.sleep(1)
    humidifier = TimedDigitalActuator(16)
    time.sleep(1)
    hatch = Hatch()
    time.sleep(1)
    stepper = Stepper()
    time.sleep(1)

    #picture
    picture = Picture("Plant1")

    #silencer
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    timeToSilence = 0
    alloff = False

    while True:

        if not GPIO.input(12):
            print "Silence"
            timeToSilence = time.time() + 60 * 60

        if timeToSilence > time.time():
            print "REMAINE SILENCE"
            hatch.setHatch(1)
            insideFan.setTime(0)
            outsideFan.setTime(0)
            humidifier.setTime(0)
            stepper.setTime(0)
            alloff = True
        else:
            alloff = False

        now = datetime.datetime.now()
        m = {}
        m['Timestamp']               = "%d-%d-%d-%d-%d-%d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        m['Watertemperature']        = waterTemperature.getWaterTemp()
        m['InsideHumidity']          = airInside.getHumidity()
        m['InsideTemperature']       = airInside.getTemperature()
        m['OutsideHumidity']         = airOutside.getHumidity()
        m['OutsideTemperature']      = airOutside.getTemperature()
        m['CPUTemperature']          = systemData.getCPUTemp()
        m['GPUTemperature']          = systemData.getGPUTemp()
        m['CPUUsage']                = systemData.getCPUuse()
        m['Loadlevel']               = systemData.getLoadLevel()
        m['WeatherHumidity']         = weather.getHumidity()
        m['WeatherPressure']         = weather.getPressure()
        m['WeatherPressureTrent']    = weather.getPressureTrent()
        m['WeatherUV']               = weather.getUV()
        m['WeatherPreciptionTotal']  = weather.getPrecipTotal()
        m['WeatherPreciptionHourly'] = weather.getPrecipHrly()
        m['OutsideFan']              = outsideFan.getState()
        m['InsideFan']               = insideFan.getState()
        m['Humidifier']              = humidifier.getState()
        m['Hatch']                   = hatch.getHatch()
        m['Stepper']                 = stepper.getState()
        m['StepperPosition']         = stepper.getCounter()
        m['AllOff']                  = alloff
        iotfClient.pushDataToIBM(m)
        csvPersistor.persist(m)
        time.sleep(1)
