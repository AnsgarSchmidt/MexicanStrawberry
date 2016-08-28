import threading
import os
import time

class SystemData(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.cpu_temp   = 0
        self.gpu_temp   = 0
        self.cpu_use    = 0
        self.load_level = 0
        self.start()

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
        ll = os.popen("uptime | cut -d \":\"  -f 5 | cut -d \",\" -f 1").readline().strip()
        self.load_level = float(ll)
        time.sleep(1)

    def run(self):
        while True:
            self.aquireData()
            time.sleep(1)

if __name__ == '__main__':
    sd = SystemData()
    sd.start()
    time.sleep(5)
    print sd.getCPUTemp()
    print sd.getCPUuse()
    print sd.getGPUTemp()
    print sd.getLoadLevel()
