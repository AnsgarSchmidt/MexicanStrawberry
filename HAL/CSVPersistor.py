import os
import threading
import time
import csv
import Queue
import datetime
import json
import swiftclient

class CSVPersistor(threading.Thread):

    def __init__(self, id):

        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.q = Queue.Queue()
        self.container_name = 'MexicanStrawberry-' + id

        objectstorage_creds = json.load(open("config.txt"))['Object-Storage'][0]['credentials']

        if objectstorage_creds:
            self.auth_url    = objectstorage_creds['auth_url' ] + '/v3'
            self.password    = objectstorage_creds['password' ]
            self.project_id  = objectstorage_creds['projectId']
            self.user_id     = objectstorage_creds['userId'   ]
            self.region_name = objectstorage_creds['region'   ]
            self.configOK    = True
        else:
            self.configOK    = False
            print "Error in configuration for swift client"

        now = datetime.datetime.now()
        self.file_name = "%d-%d-%d-%d.csv" % (now.year, now.month, now.day, now.hour)
        self.start()

    def getSwiftConnection(self):
        return swiftclient.Connection(key          = self.password,
                                      authurl      = self.auth_url,
                                      auth_version = '3',
                                      os_options={"project_id":   self.project_id,
                                                   "user_id":     self.user_id,
                                                   "region_name": self.region_name})

    def checkContainer(self):
        exists = False

        conn = self.getSwiftConnection()

        for i in conn.get_account()[1]:
            if i['name'] == self.container_name:
                exists = True

        if not exists:
            conn.put_container(self.container_name)
            print "Creating container"

        conn.close() # we get it every time to be safe against network problems

    def persist(self, measurements):
        self.q.put(measurements)

    def run(self):

        while True:

            now = datetime.datetime.now()
            file_name = "%d-%d-%d-%d.csv" % (now.year, now.month, now.day, now.hour)

            if file_name != self.file_name:

                # upload old file
                print "new file, upload old"

                self.checkContainer()
                conn = self.getSwiftConnection()

                with open(self.file_name, 'r') as file:
                    conn.put_object(self.container_name, self.file_name,
                                    contents=file.read(),
                                    content_type='text/plain')
                conn.close()

                os.remove(self.file_name)

                self.file_name = file_name

                with open(self.file_name, 'ab') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',')
                    d = ['Timestamp',
                         'Watertemperature',
                         'InsideHumidity',
                         'InsideTemperature',
                         'OutsideHumidity',
                         'OutsideTemperature',
                         'CPUTemperature',
                         'GPUTemperature',
                         'CPUUsage',
                         'Loadlevel',
                         'WeatherHumidity',
                         'WeatherPressure',
                         'WeatherPressureTrent',
                         'WeatherUV',
                         'WeatherPreciptionTotal',
                         'WeatherPreciptionHourly',
                         'OutsideFan',
                         'InsideFan',
                         'Humidifier'
                    ]
                    spamwriter.writerow(d)

            if not self.q.empty():

                m = self.q.get()

                with open(self.file_name, 'ab') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',')
                    d = [
                         m['Timestamp'],
                         m['Watertemperature'],
                         m['InsideHumidity'],
                         m['InsideTemperature'],
                         m['OutsideHumidity'],
                         m['OutsideTemperature'],
                         m['CPUTemperature'],
                         m['GPUTemperature'],
                         m['CPUUsage'],
                         m['Loadlevel'],
                         m['WeatherHumidity'],
                         m['WeatherPressure'],
                         m['WeatherPressureTrent'],
                         m['WeatherUV'],
                         m['WeatherPreciptionTotal'],
                         m['WeatherPreciptionHourly'],
                         m['OutsideFan'],
                         m['InsideFan'],
                         m['Humidifier']
                    ]
                    spamwriter.writerow(d)
                self.q.task_done()

            time.sleep(0.5)
