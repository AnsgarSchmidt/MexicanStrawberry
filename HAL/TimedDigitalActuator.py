import threading
import time
import RPi.GPIO as GPIO

class TimedDigitalActuator(threading.Thread):

    def __init__(self, pin):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.timeToKeepOn = 0
        self.status       = 0
        self.pin          = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.start()

    def setTime(self, timeToAdd):
        self.timeToKeepOn = time.time() + timeToAdd

    def getState(self):
        return self.status

    def run(self):
        while True:
            if self.timeToKeepOn > time.time():
                GPIO.output(self.pin, True)
                self.status = 1
            else:
                GPIO.output(self.pin, False)
                self.status = 0
            time.sleep(0.1)

if __name__ == '__main__':

    humidifier = TimedDigitalActuator(16)
    humidifier.start()

    fanin  = TimedDigitalActuator(21)
    fanin.start()

    fanout = TimedDigitalActuator(20)
    fanout.start()

    time.sleep(2)

    fanin.setTime(2)
    time.sleep(3)

    fanout.setTime(2)
    time.sleep(3)

    humidifier.setTime(2)
    time.sleep(3)
