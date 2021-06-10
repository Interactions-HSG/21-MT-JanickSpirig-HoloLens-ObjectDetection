
# is responsible for which objects and actions are currently displayed in the Hololens so that we know what the user is currently seeing

class StatusHandler:
    def __init__(self):
        # here let's save all the actions that we have

        # here we track if objects are present in scene or not

        self.statuses = {
            "Cherrybot": 1,
            "Leubot": 1,
            "smart-bulb":0,
            "desk-lamp":0,
            "person":0
            }