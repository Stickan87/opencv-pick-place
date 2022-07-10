# opencv-pick-place
python code for simple pick and place robot using opencv and grbl

Python interpreters used: Numpy v.1.22.1
                          opencv-python	4.5.5.62
                          pyserial	3.5
                          
Fist part of code is for user settings. Parts are commented so should be fairly straight forward.

useArduino == true starts the connection with the arduino/serialport. You need to know what port yours are using and change the line:
s = serial.Serial('COM3', 115200)
to the proper COM port.

send function is copy/pasted from another github file for sending gcode from a txtfile with GRBL.

Main part of the streaming code is in takepicture()
Code exits if there is no camera/webcam plugged in in any COM / USB

Calibration is done with a factor and in my case i did not want the robot to be able to move in all visable camera.
