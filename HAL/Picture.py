import threading
import json
import swiftclient
import picamera
import time

class Picture(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.camera = picamera.PiCamera()
        self.makepic = False
        self.container_name = 'MexicanStrawberryPictures'

        objectstorage_creds = json.load(open("config.txt"))['Object-Storage'][0]['credentials']

        if objectstorage_creds:
            auth_url = objectstorage_creds['auth_url'] + '/v3'  # authorization URL
            password = objectstorage_creds['password']  # password
            project_id = objectstorage_creds['projectId']  # project id
            user_id = objectstorage_creds['userId']  # user id
            region_name = objectstorage_creds['region']  # region name

        conn = swiftclient.Connection(key=password,
                                       authurl=auth_url,
                                       auth_version='3',
                                       os_options={"project_id": project_id,
                                                   "user_id": user_id,
                                                   "region_name": region_name})


        exists = False

        for i in conn.get_account()[1]:
            if i['name'] == self.container_name:
                exists = True

        if not exists:
            conn.put_container(self.container_name)
            print "Creating container"

        conn.close()

    def makePicture(self):
        self.makepic = True

    def run(self):
        while True:
            if self.makepic:
                self.makepic = False
                now = datetime.datetime.now()
                file_name = "%d-%d-%d-%d-%d-%d.jpg" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
                self.camera.capture(file_name)

                objectstorage_creds = json.load(open("config.txt"))['Object-Storage'][0]['credentials']

                if objectstorage_creds:
                    auth_url = objectstorage_creds['auth_url'] + '/v3'  # authorization URL
                    password = objectstorage_creds['password']  # password
                    project_id = objectstorage_creds['projectId']  # project id
                    user_id = objectstorage_creds['userId']  # user id
                    region_name = objectstorage_creds['region']  # region name

                conn = swiftclient.Connection(key=password,
                                              authurl=auth_url,
                                              auth_version='3',
                                              os_options={"project_id": project_id,
                                                          "user_id": user_id,
                                                          "region_name": region_name})

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
    p = Picture()
    p.start()
    p.makePicture()
    time.sleep(100)