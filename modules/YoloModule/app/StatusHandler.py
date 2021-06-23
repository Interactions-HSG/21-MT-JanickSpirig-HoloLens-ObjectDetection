
# is responsible for which objects and actions are currently displayed in the Hololens so that we know what the user is currently seeing

class StatusHandler:
    def __init__(self):
        # here let's save all the actions that we have

        # here we track if objects are present in scene or not

        self.statuses = {
            "Cherrybot": 0,
            "Leubot": 0,
            "smart-bulb":0,
            "desk-lamp":0,
            "lab":0,
            "office": 0
            }