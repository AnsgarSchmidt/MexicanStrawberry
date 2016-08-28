import os
import time

class Hatch():

    def __init__(self):
        self.hatch = 0
        os.popen("gpio mode 1 pwm")
        os.popen("gpio pwm-ms")
        os.popen("gpio pwmc 1920")
        os.popen("gpio pwmr 200")

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

if __name__ == '__main__':
    h = Hatch()
    h.setHatch(0)
    time.sleep(2)
    h.setHatch(0.5)
    time.sleep(2)
    h.setHatch(1)
    time.sleep(2)
    h.setHatch(0)
    time.sleep(2)

