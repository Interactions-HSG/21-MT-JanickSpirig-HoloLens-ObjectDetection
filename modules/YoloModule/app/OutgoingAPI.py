import requests
from StatusHandler import StatusHandler

class APIHandler:
    def __init__(self):
        # the hololens URL
        # self.hololensUrl = "http://10.2.1.85" #labnet lab
        self.hololensUrl = "http://10.2.1.233" # labnet office
        self.hololensPort = "5050"
        self.statusHandler = StatusHandler()
    
    def handleThing(self, thing, display):

        if self.statusHandler.statuses[thing] != display:
            
            #if thing == "Lab":
            
                #if self.statusHandler.lab_detected:
                   # return
            
            url = "{}:{}/?{}={}".format(self.hololensUrl, self.hololensPort, thing, str(display))
            print(url)
            
            # only send request to hololens if thing is there
            if (display == 1):
                r = requests.get(url)

                if r.status_code == 200:
                    print("State changed successfully!")
                else:
                    print("Error while trying to change the state.")
            
            # update the current state, whether we are displaying the thing on the Hololens or not
            self.statusHandler.statuses[thing] = display
        else:
            return