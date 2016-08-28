import threading
import json
import swiftclient
import picamera
import datetime
import time
import os

class Picture(threading.Thread):

    def __init__(self, id):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.makepic        = False
        self.container_name = 'MexicanStrawberryPictures-' + id

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

        self.start()

    def getSwiftConnection(self):
        return swiftclient.Connection(key =           self.password,
                                      authurl =      self.auth_url,
                                      auth_version = '3',
                                      os_options={"project_id":  self.project_id,
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

    def makePicture(self):
        self.makepic = True

    def run(self):

        while self.configOK:

            if self.makepic:
                self.makepic = False
                now = datetime.datetime.now()
                file_name = "%d-%d-%d-%d-%d-%d.jpg" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
                picamera.PiCamera().capture(file_name)
                self.checkContainer()
                conn = self.getSwiftConnection()
                with open(file_name, 'r') as file:
                    conn.put_object(self.container_name, file_name,
                                    contents=file.read(),
                                    content_type='image/jpeg')
                conn.close()
                os.remove(file_name)
                print "Update done"
            time.sleep(1)

if __name__ == '__main__':

    print "Testing Campera"
    p = Picture("dummy1")
    p.start()
    p.makePicture()
    time.sleep(15)