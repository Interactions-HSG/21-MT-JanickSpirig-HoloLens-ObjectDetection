# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import os
import random
import sys
import time
import json
import yaml

import VideoCapture
from VideoCapture import VideoCapture

def main(
        videoPath,
        verbose,
        videoWidth,
        videoHeight,
        fontScale,
        inference,
        confidenceLevel,
        custom,
        tiny,
        show,
        output,
        min_time
        ):

    global videoCapture

    try:
        print("\nPython %s\n" % sys.version )
        print("Yolo Capture Module. Press Ctrl-C to exit." )

        with VideoCapture(videoPath,
                         verbose,
                         videoWidth,
                         videoHeight,
                         fontScale,
                         inference,
                         confidenceLevel,
                         custom,
                         tiny,
                         show,
                         output,
                         min_time
                         ) as videoCapture:
                         
            videoCapture.start()

    except KeyboardInterrupt:
        print("Camera capture module stopped" )

def Run():
    try:
        with open("config.yml", "r") as ymlfile:
            cfg = yaml.load(ymlfile)

        if cfg['USE_WEBCAM']:
            VIDEO_PATH = 0
        else:
            VIDEO_PATH = cfg['VIDEO_SOURCE']
        
        INFERENCE = cfg['RUN_INFERENCE']
        CONFIDENCE_LEVEL = cfg['MIN_CONFIDENCE_LEVEL']
        TINY = cfg['USE_YOLO-TINY']
        SHOW = cfg['SHOW_OUTPUT']
        OUTPUT_PATH = cfg['RESULT_PATH']
        CUSTOM = cfg['CUSTOM']
        MIN_TIME = cfg['MIN_TIME']
        
        # no idea why these parameters exist
        VERBOSE = False
        VIDEO_WIDTH = 0
        VIDEO_HEIGHT = 0
        FONT_SCALE = 1
        
    except ValueError as error:
        print(error )
        sys.exit(1)

    main(VIDEO_PATH, VERBOSE, VIDEO_WIDTH, VIDEO_HEIGHT, FONT_SCALE, INFERENCE, CONFIDENCE_LEVEL, CUSTOM, TINY, SHOW, OUTPUT_PATH, MIN_TIME)

if __name__ == '__main__':
    Run()