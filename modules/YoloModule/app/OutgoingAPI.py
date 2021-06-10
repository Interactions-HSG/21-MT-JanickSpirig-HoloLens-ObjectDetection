import requests
from StatusHandler import StatusHandler

class APIHandler:
    def __init__(self):
        # the hololens URL
        self.hololensUrl = "http://127.0.0.1:5050"
        self.statusHandler = StatusHandler()
    
    def handleThing(self, thing, display):

        '''
        Structure of Switcher:
            Thing
                Action
                    param_key, param_values
                                [0] to show action to user
                                [1] to hide action for user
        '''

        if self.statusHandler.statuses[thing] != display:
            url = "{}/?{}={}".format(self.hololensUrl, thing, display)
            
            '''
            r = requests.get(url)
            
            if r.status_code == 200:
                print("State changed successfully!")
            else:
                print("Error while trying to change the state.")
            '''
            # update the current state, whether we are displaying the thing on the Hololens or not
            self.statusHandler.statuses[thing] = display
        else:
            return