
# is responsible for which objects and actions are currently displayed in the Hololens so that we know what the user is currently seeing

class StatusHandler:
    def __init__(self, custom_classes=[]):
        # the current location of the user
        self.lab_detected = False
        self.office_detected = False
        # here we track if objects are present in scene or not

        if len(custom_classes) > 0:
            # use custom classes
            self.statuses = dict()
            for thing in custom_classes:
                self.statuses[thing] = 0
        else:
            # use coco classes
            self.statuses = {
                "person":0,
                "bicycle":0,
                "car":0,
                "motorcycle":0,
                "airplane":0,
                "bus":0,
                "train":0,
                "truck":0,
                "boat":0,
                "traffic light":0,
                "fire hydrant":0,
                "stop sign":0,
                "parking meter":0,
                "bench":0,
                "bird":0,
                "cat":0,
                "dog":0,
                "horse":0,
                "sheep":0,
                "cow":0,
                "elephant":0,
                "bear":0,
                "zebra":0,
                "giraffe":0,
                "backpack":0,
                "umbrella":0,
                "handbag":0,
                "tie":0,
                "suitcase":0,
                "frisbee":0,
                "skis":0,
                "snowboard":0,
                "sports ball":0,
                "kite":0,
                "baseball bat":0,
                "baseball glove":0,
                "skateboard":0,
                "surfboard":0,
                "tennis racket":0,
                "bottle":0,
                "wine glass":0,
                "cup":0,
                "fork":0,
                "knife":0,
                "spoon":0,
                "bowl":0,
                "banana":0,
                "apple":0,
                "sandwich":0,
                "orange":0,
                "broccoli":0,
                "carrot":0,
                "hot dog":0,
                "pizza":0,
                "donut":0,
                "cake":0,
                "chair":0,
                "couch":0,
                "potted plant":0,
                "bed":0,
                "dining table":0,
                "toilet":0,
                "tv":0,
                "laptop":0,
                "mouse":0,
                "remote":0,
                "keyboard":0,
                "cell phone":0,
                "microwave":0,
                "oven":0,
                "toaster":0,
                "sink":0,
                "refrigerator":0,
                "book":0,
                "clock":0,
                "vase":0,
                "scissors":0,
                "teddy bear":0,
                "hair drier":0,
                "toothbrush":0
            }