import requests
from StatusHandler import StatusHandler

class APIHandler:
    def __init__(self):
        # the hololens URL
        self.hololensUrl = "http://192.168.43.54"
        self.hololensPort = "5050"
        self.statusHandler = StatusHandler()
    
    def handleThing(self, thing, display):

        if self.statusHandler.statuses[thing] != display:

            url = "{}:{}/?{}={}".format(self.hololensUrl, self.hololensPort, thing, str(display))
            
            print(url)
            
            r = requests.get(url)
            if r.status_code == 200:
                print("State changed successfully!")
            else:
                print("Error while trying to change the state.")
            
            # update the current state, whether we are displaying the thing on the Hololens or not
            self.statusHandler.statuses[thing] = display
            
        else:
            return