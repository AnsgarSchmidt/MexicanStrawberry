import threading
import time
import Adafruit_DHT

class DHT(threading.Thread):

    def __init__(self, pin):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.temperature = 0
        self.humidity    = 0
        self.pin         = pin
        self.start()

    def getTemperature(self):
        return self.temperature

    def getHumidity(self):
        return self.humidity

    def run(self):
        while True:
            self.humidity, self.temperature = Adafruit_DHT.read_retry(22, self.pin)
            time.sleep(1)

if __name__ == '__main__':
    d = DHT(24)
    d.start()
    time.sleep(3)
    print d.getHumidity()
    print d.getTemperature()