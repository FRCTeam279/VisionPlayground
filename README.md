# VisionPlayground 

### cameraCalibration.py
Loops through any png files in the folder, and generates a calibration matrix, which is then used to generate an undistorted image. This is just test code mostly copied from the WPI documentation on OpenCV.

### vision.py
This is a library generated by GRIP, and creates a processed image that contains only the detected objects.

### detect.py
Takes an image using the RPi camera, and generates a new image using vision.py that contains only the detected objects.
