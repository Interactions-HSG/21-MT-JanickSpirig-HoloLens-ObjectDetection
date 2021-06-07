from os import initgroups
import time
import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
from absl import app, flags, logging
from absl.flags import FLAGS

import detector.core.utils as utils
from detector.core.yolov4 import filter_boxes
from tensorflow.python.saved_model import tag_constants
from PIL import Image
import cv2
import numpy as np
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
from detector.core.config import cfg



class Detector:
    def __init__(self,
            tiny=False,
            framework='tf',
            model='yolov4',
            iou=0.45,
            score=0.25
            ):

        self.config = config = ConfigProto()
        self.config.gpu_options.allow_growth = True
        self.session = InteractiveSession(config=config)
        self.input_size = 416
        self.framework = framework
        self.model = model
        self.tiny = tiny
        self.iou = iou
        self.score = score
        self.STRIDES, self.ANCHORS, self.NUM_CLASS, self.XYSCALE = utils.load_config(self.tiny, self.model)

        if not self.tiny:
            # self.weights = './checkpoints/yolov4-416'
            self.weights = 'detector/checkpoints/yolov4-416'
        else:
            # self.weights = './checkpoints/yolov4-tiny-416'
            self.weights = 'detector/checkpoints/yolov4-tiny-416'
        
        if self.framework == 'tflite':
            self.interpreter = tf.lite.Interpreter(model_path=self.weights)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
        else:
            self.saved_model_loaded = tf.saved_model.load(self.weights, tags=[tag_constants.SERVING])
            self.infer = self.saved_model_loaded.signatures['serving_default']
        
        print("TensorFlow Yolo::__init__()")
        print("TensorFlow Model : %s" % (self.model))
        print("===============================================================")
        print("Initialising te TensorFlow model with the following parameters: ")
        print("   - Tiny            : " + str(self.tiny))
        print("   - Weights         : " + self.weights)
        print("")

    def detect(self, frame):
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_size = frame.shape[:2]
        image_data = cv2.resize(frame, (self.input_size, self.input_size))
        image_data = image_data / 255.
        image_data = image_data[np.newaxis, ...].astype(np.float32)
        start_time = time.time()

        if self.framework == 'tflite':
            self.interpreter.set_tensor(self.input_details[0]['index'], image_data)
            self.interpreter.invoke()
            pred = [self.interpreter.get_tensor(self.output_details[i]['index']) for i in range(len(self.output_details))]
            if self.model == 'yolov3' and self.tiny == True:
                boxes, pred_conf = filter_boxes(pred[1], pred[0], score_threshold=0.25,
                                                input_shape=tf.constant([self.input_size, self.configinput_size]))
            else:
                boxes, pred_conf = filter_boxes(pred[0], pred[1], score_threshold=0.25,
                                                input_shape=tf.constant([self.input_size, self.input_size]))
        else:
            batch_data = tf.constant(image_data)
            pred_bbox = self.infer(batch_data)
            for key, value in pred_bbox.items():
                boxes = value[:, :, 0:4]
                pred_conf = value[:, :, 4:]

        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(
                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=50,
            max_total_size=50,
            iou_threshold=self.iou,
            score_threshold=self.score
        )

        pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]
        
        detections, image = utils.draw_bbox(frame, pred_bbox)
        
        return detections, image