# wm_object_detection
This repo will guide the user to train his custom object model to use with [YOLOV2](https://github.com/WalkingMachine/darknet_ros).

### Tutorial
A tutorial can be followed [here](https://github.com/WalkingMachine/sara_wiki/wiki/Create-a-custom-dataset-(YOLO)).

### Dependencies
* [ffmpeg](https://www.ffmpeg.org/)
* [Darknet](https://github.com/pjreddie/darknet)
* [CUDNN](https://developer.nvidia.com/cudnn)
* [CUDA](https://developer.nvidia.com/cuda-downloads?target_os=Linux)
* [BBoxLabelTool](https://github.com/puzzledqs/BBox-Label-Tool)

### YOLOV2 integration
1. Add the .cfg file to the package darknet_ros (darknet_ros/yolo_network_config/cfg/...)
2. Add the .weights file to the package darknet_ros (darknet_ros/yolo_network_config/weights/...)
3. Modify the .yaml file and add the classes names (darknet_ros/config/...)
