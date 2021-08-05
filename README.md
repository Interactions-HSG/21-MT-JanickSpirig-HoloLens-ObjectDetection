# Hololens YOLOv4 Object Recognition
With this repository you can access and evaluate the camera stream of your Microsoft Hololens to recognize at what objects the user is currently looking at. 
The code is largely a combination of two repositories.
- Access Hololens camera stream: [IntelligentEdgeHOL](https://github.com/Azure/IntelligentEdgeHOL)
- Run YOLOv4 object recognition for a single frame: [tensorflow-yolov4-tflite](https://github.com/theAIGuysCode/tensorflow-yolov4-tflite)

## Geeting Started

#### 1 Device Portal Credentials
Configure the Hololens Device Portal as explained in [this guide](https://docs.microsoft.com/en-us/windows/mixed-reality/develop/platform-capabilities-and-apis/using-the-windows-device-portal). Save and remember your user credentials that you defined in [this step](https://docs.microsoft.com/en-us/windows/mixed-reality/develop/platform-capabilities-and-apis/using-the-windows-device-portal#creating-a-username-and-password).

#### 2 Clone repository

#### 3 Setup YOLOv4
- Open a terminal window and cd to modules\YoloModule\app\detector
- Create your conda environment (either CPU or GPU) as explained [here](https://github.com/theAIGuysCode/tensorflow-yolov4-tflite#conda-recommended).  
Download the pre-traiend COCO weights ([yolov4.weights](https://drive.google.com/open?id=1cewMfusmPjYWbrnuJRuKhPMwRe_b9PaT), [yolov4-tiny.weights](https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights)) __OR__ train yolo for your custom classes by following the steps in [this video](https://www.youtube.com/watch?v=mmj3nxGT2YQ) 
- Move the according `.weights` file (pretrained or custom) into the folder detector\data. If you use custom wieights, make sure that the file is named as `custom.weights`
- If you use custom weights, comment out line 15 in file detector\core\config.py and comment line 14. It should look like that:  

<img width="541" alt="Screenshot 2021-08-05 at 17 05 09" src="https://user-images.githubusercontent.com/43849960/128373749-93844a5c-46dd-4f6c-90e9-1e20fde31e86.png">
  
- Convert the yolo weights from darkent to TensorFlow format by executing one of the commands below in the terminal (cd to folder detector)
```
# pretrained
python save_model.py --weights ./data/yolov4.weights --output ./checkpoints/yolov4-416 --input_size 416 --model yolov4 

# pretrained tiny
python save_model.py --weights ./data/yolov4-tiny.weights --output ./checkpoints/yolov4-tiny-416 --input_size 416 --model yolov4 --tiny

# custom
python save_model.py --weights ./data/custom.weights --output ./checkpoints/custom-416 --input_size 416 --model yolov4 
```

#### 4 Setup conifg.yml
Define the options in the file `config.yml` according to your needs.  
- Set `CUSTOM` to `TRUE` if you have set up YOLOv4 for custom classes
- Set `USE_YOLO-TINY`to `TRUE` if you use tiny weights
- For `VIDEO_SOURCE` copy the path below and replace __DEVICE-PORTAL-USER__, __DEVICE-PORTAL-PWD__ AND __HOLOLENS-IP__. The user and pwd are the ones you have defined when setting up the device portal. To come up with the IP address of the Hololens follow this guide.
```
https://<<DEVICE-PORTAL-USER>>:<<DEVICE-PORTAL-PWD>>@<<HOLOLENS-IP>>/api/holographic/stream/live.mp4?olo=true&pv=true&mic=true&loopback=true
```
