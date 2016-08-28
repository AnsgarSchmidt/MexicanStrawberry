import threading
import time
import RPi.GPIO as GPIO

PIN_ENABLE         = 17
PIN_DIRECTION      = 22
PIN_STEPPER_END    = 25
PIN_STEP           = 27

class Stepper(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.timeToKeepOn =     0
        self.status       =     0
        self.direction    = False
        self.counter      =   -10 # -1 undefined so we need to calibrate
        self.MAX          =  2700 # Max steps in one direction
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_ENABLE,      GPIO.OUT)
        GPIO.setup(PIN_STEP,        GPIO.OUT)
        GPIO.setup(PIN_DIRECTION,   GPIO.OUT)
        GPIO.setup(PIN_STEPPER_END, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.output(PIN_ENABLE,    True          ) # inverted therefore we switch it off
        GPIO.output(PIN_DIRECTION, self.direction)
        GPIO.output(PIN_STEP,      False         )
        self.calibrate()

    def calibrate(self):
        print "Start Calibrating"
        GPIO.output(PIN_ENABLE, False)  # inverted therefore we switch it on
        while GPIO.input(PIN_STEPPER_END):
            GPIO.output(PIN_STEP,   True )  # 1 mycro second are enough therefore no sleep
            GPIO.output(PIN_STEP,   False)
            time.sleep(0.01)
        GPIO.output(PIN_ENABLE, True)  # inverted therefore we switch it off
        self.counter = 0
        print "Calibration Done"
        self.start()

    def setTime(self, timeToAdd):
        self.timeToKeepOn = time.time() + timeToAdd

    def getState(self):
        return self.status

    def getCounter(self):
        return self.counter

    def step(self):
        GPIO.output(PIN_STEP, True)   # 1 mycro second are enough therefore no sleep
        GPIO.output(PIN_STEP, False)

        if self.direction:
            self.counter += 1
        else:
            self.counter -= 1

        if self.direction and self.counter >= self.MAX:
            self.direction = False
            GPIO.output(PIN_DIRECTION, self.direction)

        if not self.direction and self.counter <= 0:
            self.direction = True
            GPIO.output(PIN_DIRECTION, self.direction)

    def run(self):
        while True:

            if self.counter == -10: # If we are not calibrated do nothing
                time.sleep(1)
                continue

            if self.timeToKeepOn > time.time():
                GPIO.output(PIN_ENABLE, False) #inverted
                self.status = 1
                self.step()
                time.sleep(0.01) # Speed
            else:
                GPIO.output(PIN_ENABLE, True) #inverted
                self.status = 0
                time.sleep(1) # wait for a longer time when off

if __name__ == '__main__':
    s = Stepper()

    time.sleep(5)
    print "Start"
    s.setTime(30)

    time.sleep(10)

    s.setTime(20)

    time.sleep(60)