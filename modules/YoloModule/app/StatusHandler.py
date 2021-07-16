
# is responsible for which objects and actions are currently displayed in the Hololens so that we know what the user is currently seeing

class StatusHandler:
    def __init__(self):
        # the current location of the user
        self.lab_detected = False
        self.office_detected = False
        # here we track if objects are present in scene or not

        self.statuses = {
            "Cherrybot": 0,
            "Leubot": 0,
            "smart-bulb":0,
            "desk-lamp":0,
            "lab":0,
            "office": 0,
            "smartcard":0,
            "window":0,
            "ceiling-light":0,
            "hue":0
            }