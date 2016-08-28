import ibmiotf.device
import time
import json

class IBMConnector():

    def __init__(self, callback):
        self.callback = callback

    def connectToIBM(self):
        try:
            self.client = ibmiotf.device.Client(json.load(open("clientconfig.txt")))
            self.client.connect()
            self.client.commandCallback = self.callback
        except:
            print "Error connection to IBM"

    def pushDataToIBM(self, measurements):
        try:
            measurements['test'] = 42
            data = {}
            data['d'] = measurements
            self.client.publishEvent("Measurements", "json", data)
            #print "Data send:" + str(data)
        except:
            self.connectToIBM()
