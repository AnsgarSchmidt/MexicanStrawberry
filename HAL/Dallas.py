import threading
import os
import time

class Dallas(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        self.temp_c = 0
        self.start()

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

if __name__ == '__main__':
    w = Dallas()
    w.start()
    time.sleep(2)
    print w.getWaterTemp()