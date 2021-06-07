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

#import YoloInference
#from YoloInference import YoloInference

import detector
from detector.detector import Detector
from detector.core.utils import draw_bbox

class VideoCapture(object):

    def __init__(
            self,
            videoPath = "",
            verbose = True,
            videoW = 0,
            videoH = 0,
            fontScale = 1.0,
            inference = True,
            confidenceLevel = 0.5,
            tiny = True,
            show=False,
            result_path="/Users/janickspirig/Desktop/results.avi"
            ):

        self.videoPath = videoPath
        self.verbose = verbose
        self.videoW = videoW
        self.videoH = videoH
        self.inference = inference
        self.confidenceLevel = confidenceLevel
        self.useStream = False
        self.useWebcam = False
        self.useMovieFile = False
        self.frameCount = 0
        self.vStream = None
        self.vCapture = None
        self.displayFrame = None
        self.fontScale = float(fontScale)
        self.captureInProgress = False
        self.tiny = tiny
        self.show_result = show
        self.result_path = result_path

        print("VideoCapture::__init__()")
        print("OpenCV Version : %s" % (cv2.__version__))
        print("===============================================================")
        print("Initialising Video Capture with the following parameters: ")
        print("   - Video path      : " + str(self.videoPath))
        print("   - Video width     : " + str(self.videoW))
        print("   - Video height    : " + str(self.videoH))
        print("   - Font Scale      : " + str(self.fontScale))
        print("   - Inference?      : " + str(self.inference))
        print("   - ConficenceLevel : " + str(self.confidenceLevel))
        print("")

        self.yoloInference = Detector(tiny=self.tiny) # yolov4

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

        if self.verbose:
            print("videoCapture::__enter__()")

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

        # check if stream is opened
        if self.useStream:
            print("stream is opnened {}".format(self.vStream.stream.isOpened()))
        elif self.useWebcam:
            print("stream is opnened {}".format(self.vCapture.isOpened()))

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
            out = cv2.VideoWriter(self.result_path, codec, 20, (frame_width, frame_height))

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
                print("FPS: %.2f" % fps)
                if self.show_result:
                    result = np.asarray(image)
                    result = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    out.write(result)
                '''
                if self.show:
                    # cv2.imshow("result", result)
                    cv2.imshow('result' , result)

                if cv2.waitKey(1) & 0xFF == ord('q'): break
                '''
                if len(detections) > 0:
                    for detection in detections:
                        classLabel, confidence = detection[0], detection[1]
                        if confidence > self.confidenceLevel:
                            # here we can now do something with the detection now as it is aboved the defined confidence level
                            print("Object: {}".format(classLabel))
                            print("Confidence: {}".format(confidence))

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
                #if self.verbose:
                    #print("  Wait time between frames :" + str(int(waitTimeBetweenFrames)))
                time.sleep(waitTimeBetweenFrames/1000.0)

    def __exit__(self, exception_type, exception_value, traceback):

        if self.vCapture:
            self.vCapture.release()

        # self.imageServer.close()
        cv2.destroyAllWindows()