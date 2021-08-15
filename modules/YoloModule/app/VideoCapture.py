#To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import

import cv2
import numpy as np
import requests
import time
import json
import os
import signal
import time

import VideoStream
from VideoStream import VideoStream
from OutgoingAPI import APIHandler

#import YoloInference
#from YoloInference import YoloInference

import detector
from detector.detector import Detector
from detector.core.utils import draw_bbox

class VideoCapture(object):

    def __init__(
            self,
            videoPath,
            inference,
            confidenceLevel,
            custom,
            custom_classes,
            tiny,
            show,
            result_path,
            min_time,
            holo_endpoint,
            holo_url
            ):

        self.videoPath = videoPath
        self.inference = inference
        self.confidenceLevel = confidenceLevel
        self.useStream = False
        self.useWebcam = False
        self.useMovieFile = False
        self.frameCount = 0
        self.vStream = None
        self.vCapture = None
        self.displayFrame = None
        self.captureInProgress = False
        self.custom = custom
        self.custom_classes = custom_classes
        self.tiny = tiny
        self.show_result = show
        self.result_path = result_path
        self.recommendation_thresh = min_time
        self.holo_endpoint = holo_endpoint

        print("VideoCapture::__init__()")
        print("OpenCV Version : %s" % (cv2.__version__))
        print("===============================================================")
        print("Initialising Video Capture with the following parameters: ")
        print("   - Video path       : " + str(self.videoPath))
        print("   - Inference?       : " + str(self.inference))
        print("   - ConficenceLevel  : " + str(self.confidenceLevel))
        print("   - CustomDetection? : " + str(self.custom))
        if self.custom:
            print("   - Custom Classes   : " + str(self.custom_classes))
        print("   - HololensEndpoint?: " + str(self.holo_endpoint))
        if self.holo_endpoint:
            print("   - HololensUrl      : " + str(holo_url))
        print("")

        self.yoloInference = Detector(tiny=self.tiny, custom=self.custom) # yolov4

        if self.custom:
            self.apiHandler = APIHandler(holo_url, self.custom_classes)
        else:
            self.apiHandler =APIHandler(holo_url)

    def __IsCaptureDev(self, videoPath):
        try: 
            return '/dev/video' in videoPath.lower()
        except (ValueError, AttributeError):
            return videoPath == 0

    def __IsRtsp(self, videoPath):
        try:
            if 'rtsp:' in videoPath.lower() or '/api/holographic/stream' in videoPath.lower(): #or '0' in videoPath:
                return True
        except ValueError:
            return False

    def __enter__(self):

        self.setVideoSource(self.videoPath)

        return self

    def setVideoSource(self, newVideoPath):

        if self.captureInProgress:
            self.captureInProgress = False
            time.sleep(1.0)
            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None
            elif self.vStream:
                self.vStream.stop()
                self.vStream = None

        if self.__IsRtsp(str(newVideoPath)):
            print("\r\n===> RTSP Video Source")

            self.useStream = True
            self.useMovieFile = False
            self.useWebcam = False
            self.videoPath = newVideoPath

            if self.vStream:
                self.vStream.start()
                self.vStream = None

            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None

            self.vStream = VideoStream(newVideoPath).start()
            # Needed to load at least one frame into the VideoStream class
            time.sleep(1.0)
            self.captureInProgress = True

        elif self.__IsCaptureDev(newVideoPath):
            print("===> Webcam Video Source")
            if self.vStream:
                self.vStream.start()
                self.vStream = None

            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None

            self.videoPath = newVideoPath
            self.useMovieFile = False
            self.useStream = False
            self.useWebcam = True
            self.vCapture = cv2.VideoCapture(newVideoPath)
            if self.vCapture.isOpened():
                self.captureInProgress = True
            else:
                print("===========================\r\nWARNING : Failed to Open Video Source\r\n===========================\r\n")
        else:
            print("===========================\r\nWARNING : No Video Source\r\n===========================\r\n")
            self.useStream = False
            self.useYouTube = False
            self.vCapture = None
            self.vStream = None
        return self

    def get_display_frame(self):
        return self.displayFrame

    def videoStreamReadTimeoutHandler(signum, frame):
        raise Exception("VideoStream Read Timeout") 

    def start(self):
        while True:
            if self.captureInProgress:
                self.__Run__()

            if not self.captureInProgress:
                time.sleep(1.0)

    def __Run__(self):

        print("===============================================================")
        print("videoCapture::__Run__()")
        print("   - Stream          : " + str(self.useStream))
        print("   - useMovieFile    : " + str(self.useMovieFile))
        print("   - useWebcam       : " + str(self.useWebcam))

        '''
        # check if stream is opened
        if self.useStream:
            print("Stream is opnened {}".format(self.vStream.stream.isOpened()))
        elif self.useWebcam:
            print("Stream is opnened {}".format(self.vCapture.isOpened()))
        '''

        # Check camera's FPS
        if self.useStream:
            cameraFPS = int(self.vStream.stream.get(cv2.CAP_PROP_FPS))
            frame_width = int(self.vStream.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.vStream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        elif self.useWebcam:
            cameraFPS = int(self.vCapture.get(cv2.CAP_PROP_FPS))
            frame_width = int(self.vCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.vCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if cameraFPS == 0:
            print("Error : Could not get FPS")
            raise Exception("Unable to acquire FPS for Video Source")
            return

        print("Frame rate (FPS)     : " + str(cameraFPS))

        currentFPS = cameraFPS
        perFrameTimeInMs = 1000 / cameraFPS

        # by default VideoCapture returns float instead of int
        if self.show_result: 
            codec = cv2.VideoWriter_fourcc(*"XVID")
            out = cv2.VideoWriter(self.result_path, codec, cameraFPS, (frame_width, frame_height))

        index_boundary = None
        detections_queue = []
        last_fps = 0

        while True:
            tFrameStart = time.time()

            if not self.captureInProgress:
                break
            try:
                if self.useStream:
                    frame = self.vStream.read()
                    
                else:
                    frame = self.vCapture.read()[1]
                    
            except Exception as e:
                print("ERROR : Exception during capturing")
                raise(e)

            # Run Object Detection
            if self.inference:
                detections, image = self.yoloInference.detect(frame)

                fps = 1.0 / (time.time() - tFrameStart)

                # do we need to update index_boundary (this is the case when fps rate has changed significantly)
                if (fps - last_fps) > 0.3:
                    index_boundary = int(round(fps / (1/self.recommendation_thresh), 0))
            
                print("FPS: %.2f" % fps)

                last_fps = fps

                if self.show_result:
                    result = np.asarray(image)
                    result = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    out.write(result)
                
                # handle Object presence
                if len(detections) > 0:
                    queue_list = []
                    for detection in detections:
                        classLabel, confidence = detection[0], detection[1]
                        if confidence > self.confidenceLevel:
                            
                            if "hue" in classLabel:
                                classLabel = "hue"

                            queue_list.append(classLabel)
                            
                            print("Object: {}".format(classLabel))
                            print("Confidence: {}".format(confidence))

                            if self.holo_endpoint:
                                try:
                                    if self.apiHandler.statusHandler.statuses[classLabel] != 1:

                                        ThingIsThere = True
                                        
                                        if len(detections_queue) >= index_boundary:  
                                            for i in detections_queue:
                                                # check if thing has been detected x seconds ago
                                                # print(i)
                                                if any(classLabel in sl for sl in i):
                                                    continue
                                                else:
                                                    ThingIsThere = False
                                                    break 
                                        else:
                                            ThingIsThere = False
                                        
                                        if ThingIsThere:
                                            print("Thing is there")
                                            self.apiHandler.handleThing(thing=classLabel, display=1) # send call to display all actions on the Hololens that are related with this object
                                # when thing is not of interest to us
                                except KeyError:
                                    pass

                # build the new queue element
                try:
                    if len(queue_list) > 0:
                        detections_queue.append(queue_list)
                        queue_list = []
                    else:
                        # confidence too low or no detections at all
                        detections_queue.append(["NaN"])
                except NameError:
                    # no detections at all
                    detections_queue.append(["NaN"])
                         
                # update queue
                first_element = len(detections_queue) - index_boundary
                if first_element > 0:
                    detections_queue = detections_queue[first_element:]

                print(detections_queue)

                # check if all object are still there
                things_displayed = [thing for thing, pres in self.apiHandler.statusHandler.statuses.items() if pres == 1]

                for thing in things_displayed: 
                    # check if thing is still somewhere in the queue
                    ThingIsThere = False
                    for i in detections_queue:
                        if any(thing in sl for sl in i):
                            ThingIsThere = True
                            break
                    
                    if not ThingIsThere:
                        
                        self.apiHandler.handleThing(thing=thing, display=0)
                        print("Thing {} is not present anymore.".format(thing))
                
            # Calculate FPS
            timeElapsedInMs = (time.time() - tFrameStart) * 1000
            currentFPS = 1000.0 / timeElapsedInMs

            if (currentFPS > cameraFPS):
                # Cannot go faster than Camera's FPS
                currentFPS = cameraFPS

            timeElapsedInMs = (time.time() - tFrameStart) * 1000

            if (1000 / cameraFPS) > timeElapsedInMs:
                # This is faster than image source (e.g. camera) can feed.  
                waitTimeBetweenFrames = perFrameTimeInMs - timeElapsedInMs
                time.sleep(waitTimeBetweenFrames/1000.0)

    def __exit__(self, exception_type, exception_value, traceback):

        if self.vCapture:
            self.vCapture.release()

        # self.imageServer.close()
        cv2.destroyAllWindows()