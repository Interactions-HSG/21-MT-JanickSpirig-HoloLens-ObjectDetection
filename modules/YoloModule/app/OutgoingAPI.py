import requests
from StatusHandler import StatusHandler

class APIHandler:
    def __init__(self, holo_url, custom_classes=[]):

        self.holo_url = holo_url

        if len(custom_classes) > 0:
            self.statusHandler = StatusHandler(custom_classes)
        else:
            self.statusHandler = StatusHandler()
    
    def handleThing(self, thing, display):

        if self.statusHandler.statuses[thing] != display:
            
            url = "{}/?{}={}".format(self.holo_url, thing, str(display))
            print(url)
            
            # only send request to hololens if thing is there
            if (display == 1):
                r = requests.get(url)
                print(r)
                if r.status_code == 200:
                    print("Notified Hololens that thing {} is present successfully!".format(thing))
                else:
                    print("Reqeust {} failed with status code {}".format(url, r.status_code))
            
            # update the current state, whether we are displaying the thing on the Hololens or not
            self.statusHandler.statuses[thing] = display
        else:
            return