import cv2
import numpy as np
import serial
from time import sleep

useArduino = False  # ENABLE TO SEND GCODE!!!!!
sort_in_row = False # Test sorting in rows
slowgrip = False    # Test slow gripper

#SETTINGS PARAMETERS
FEEDRATE = 12000
ZFEEDRATE = 4000

# Z-levels
zbot = 64
zdropoff = 45

if sort_in_row:
    zmid = 5
else:
    zmid = 30

# Min/ max distance X
min_x = 0
max_x = 350

# Dropzones
yellowdropX = 50
yellowdropY = 400
greendropX = 180
greendropY = 400
bluedropX = 320
bluedropY = 400

#Stackdrop
stackdropX = 20
stackdropY = 60

#Calibration realworld dist
factor = 0.72
# Value in ~CM
offsetX = 39 / factor
offsetY = 80 / factor




if useArduino == True:
    s = serial.Serial('COM3', 115200)
    # Wake up grbl
    s.write("\r\n\r\n".encode())
    sleep(1)  # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input
    print("XYZ Zero ")
    s.write("G10 P0 L20 X0 Y0 Z0".encode())


def empty(img):
    pass


def send():
    print("Sending from file gotofile.txt \n")
    # Open g-code file
    f = open('gotofile.txt', 'r')
    s.write("\r\n\r\n".encode())
    sleep(1)  # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input
    print("XYZ Zero at current position")
    s.write("G10 P0 L20 X0 Y0 Z0".encode())

    # Stream g-code to grbl
    for line in f:
        l = line.strip()  # Strip all EOL characters for consistency
        print('Sending: ' + l)
        s.write(l.encode() + '\n'.encode())  # Send g-code block to grbl
        grbl_out = s.readline()  # Wait for grbl response with carriage return

    f.close()
    return


def pickallof_color(listsize, colorlistx, colorlisty, dropofx, dropofy):
    counter = 0
    y_row = 10
    stackem = zbot-5
    while counter < listsize:
        listx = colorlistx[counter]
        listx = calibX(listx, factor, offsetX) #CALIBRATE COORD X , input X.

        listy = colorlisty[counter]
        listy = calibY(listy, factor, offsetY)  # CALIBRATE COORD Y , input Y.

        if sort_in_row == True:
            if min_x < listx < max_x:
                pickandleave(listx, listy, zbot, stackem, stackdropX, stackdropY)
                print("X", listx, " Y", listy)
            else:
                print("X : OUT OF RANGE")
        else:
            if min_x < listx < max_x:
                pickandleave(listx, listy, zbot, zdropoff, dropofx, dropofy)
                print("X", listx, " Y", listy)
            else:
                print("X : OUT OF RANGE")
        counter += 1
        y_row += 60
        stackem -= 10


def pickandleave(x, y, zbot, dropoff, dropX, dropY):
    addXYcoords(x, y)
    addZmove(zbot)
    addGRIPclose()
    addZmove(zmid)
    addXYcoords(dropX, dropY)
    addZmove(dropoff)
    if slowgrip==True:
        addGRIPopenslow()
    else:
        addGRIPopen()
    addZmove(zmid)


def newGcodestart():
    # OPEN FILE TO CLEAR OUT AND MAKE NEW G91 START
    fileOPEN = open("gotofile.txt", "w")
    fileOPEN.write("G21\n")
    fileOPEN.write("G90\n")
    fileOPEN.close()
    addGRIPopen()
    addZmove(1)
    return


def addReturnmove():
    # OPEN FILE and add returnmove
    fileOPEN = open("gotofile.txt", "a")
    fileOPEN.write("G1 Z0 F3000\n")
    fileOPEN.write("G1 X0Y0 F4000\n")
    fileOPEN.close()
    return


def addXYcoords(x, y):
    # OPEN FILE and adds XY coords
    fileOPEN = open("gotofile.txt", "a")
    fileOPEN.write("G1 X " + str(x) + "Y " + str(y) + "F" + str(FEEDRATE) + "\n")
    fileOPEN.close()
    return


def addZmove(z):
    # OPEN FILE and adds Z coords
    fileOPEN = open("gotofile.txt", "a")
    fileOPEN.write("G1 Z-" + str(z) + "F" + str(ZFEEDRATE) + "\n")
    fileOPEN.write("G90\n")
    fileOPEN.close()
    return


def addGRIPopen():
    # OPEN FILE and adds Z coords
    fileOPEN = open("gotofile.txt", "a")
    fileOPEN.write("G91 G1 Z-1 F220\n")
    fileOPEN.write("M3 S40\n")
    fileOPEN.write("G91 G1 Z1 F260\n")
    fileOPEN.write("G90\n")
    fileOPEN.close()
    return


def addGRIPopenslow():
    M3 = 90
    # OPEN FILE and adds Z coords
    fileOPEN = open("gotofile.txt", "a")

    while M3 > 40:
        fileOPEN.write("G91 G1 Z-0.01 F9\n")
        fileOPEN.write("M3 S" + str(M3) + "\n")
        M3 -= 1

    fileOPEN.write("G91 G1 Z1 F260\n")
    fileOPEN.write("G90\n")
    fileOPEN.close()
    return


def addGRIPclose():
    # OPEN FILE and adds Z coords
    fileOPEN = open("gotofile.txt", "a")
    fileOPEN.write("G91 G1 Z-1 F200\n")
    fileOPEN.write("M3 S100\n")
    fileOPEN.write("G91 G1 Z1 F250\n")
    fileOPEN.write("G90\n")
    fileOPEN.close()
    return


def makeTrackbars():
    # Create trackbars
    cv2.namedWindow("Trackbar")
    cv2.resizeWindow("Trackbar", 400, 800)

    cv2.createTrackbar("hue_min", "Trackbar", 10, 179, empty)
    cv2.createTrackbar("hue_max", "Trackbar", 35, 179, empty)
    cv2.createTrackbar("sat_min", "Trackbar", 44, 255, empty)
    cv2.createTrackbar("sat_max", "Trackbar", 165, 255, empty)

    cv2.createTrackbar("Green_hue_min", "Trackbar", 40, 179, empty)
    cv2.createTrackbar("Green_hue_max", "Trackbar", 83, 179, empty)
    cv2.createTrackbar("Green_sat_min", "Trackbar", 44, 255, empty)
    cv2.createTrackbar("Green_sat_max", "Trackbar", 121, 255, empty)

    cv2.createTrackbar("Blue_hue_min", "Trackbar", 90, 179, empty)
    cv2.createTrackbar("Blue_hue_max", "Trackbar", 130, 179, empty)
    cv2.createTrackbar("Blue_sat_min", "Trackbar", 30, 255, empty)
    cv2.createTrackbar("Blue_sat_max", "Trackbar", 151, 255, empty)

    cv2.createTrackbar("val_min", "Trackbar", 0, 255, empty)
    cv2.createTrackbar("val_max", "Trackbar", 255, 255, empty)
    cv2.createTrackbar("area_max", "Trackbar", 200, 7000, empty)


def calibX(xval, factor, offsetx):
    xval = (xval - offsetx) * factor
    xval = round(xval, 2)
    return xval


def calibY(yval, factor, offsety):
    yval = (480 - yval - offsety) * factor
    yval = round(yval, 2)
    return yval


def takepicture():
    video = cv2.VideoCapture(0)  # Gets videoimg from default webcam

    makeTrackbars()
    # MAIN CODE
    while True:
        # Get picture from CAM
        ret, img = video.read()

        if img is None:
            print("No camera found, closing...")
            video.release()
            break

        # FILTERS
        blur = cv2.GaussianBlur(img, (11, 11), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

        # TRACKBAR
        hue_min = cv2.getTrackbarPos("hue_min", "Trackbar")
        hue_max = cv2.getTrackbarPos("hue_max", "Trackbar")
        Green_hue_min = cv2.getTrackbarPos("Green_hue_min", "Trackbar")
        Green_hue_max = cv2.getTrackbarPos("Green_hue_max", "Trackbar")
        Blue_hue_min = cv2.getTrackbarPos("Blue_hue_min", "Trackbar")
        Blue_hue_max = cv2.getTrackbarPos("Blue_hue_max", "Trackbar")

        sat_min = cv2.getTrackbarPos("sat_min", "Trackbar")
        sat_max = cv2.getTrackbarPos("sat_max", "Trackbar")
        Green_sat_min = cv2.getTrackbarPos("Green_sat_min", "Trackbar")
        Green_sat_max = cv2.getTrackbarPos("Green_sat_max", "Trackbar")
        Blue_sat_min = cv2.getTrackbarPos("Blue_sat_min", "Trackbar")
        Blue_sat_max = cv2.getTrackbarPos("Blue_sat_max", "Trackbar")

        val_min = cv2.getTrackbarPos("val_min", "Trackbar")
        val_max = cv2.getTrackbarPos("val_max", "Trackbar")
        area_max = cv2.getTrackbarPos("area_max", "Trackbar")

        # CREATE ARRAYS FROM TRACKBARS
        lower = np.array([hue_min, sat_min, val_min])
        upper = np.array([hue_max, sat_max, val_max])
        Green_lower = np.array([Green_hue_min, Green_sat_min, val_min])
        Green_upper = np.array([Green_hue_max, Green_sat_max, val_max])
        Blue_lower = np.array([Blue_hue_min, Blue_sat_min, val_min])
        Blue_upper = np.array([Blue_hue_max, Blue_sat_max, val_max])

        # Mask
        mask = cv2.inRange(hsv, lower, upper)
        Green_mask = cv2.inRange(hsv, Green_lower, Green_upper)
        Blue_mask = cv2.inRange(hsv, Blue_lower, Blue_upper)

        # REMOVE NOISE
        kernel = np.ones((9, 9), np.uint8)

        # Remove unnecessary noise from mask
        # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  ##Remove black
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)  ##Remove white
        Green_mask = cv2.morphologyEx(Green_mask, cv2.MORPH_OPEN, kernel)  ##Remove white
        Blue_mask = cv2.morphologyEx(Blue_mask, cv2.MORPH_OPEN, kernel)  ##Remove white

        # Shows different windows
        #cv2.imshow("colorbgr", hsv)
        win_maskWidth = 400
        win_maskHeight = 400
        dim = (win_maskWidth, win_maskHeight)

        resizedYellow = cv2.resize(mask, dim, interpolation=cv2.INTER_AREA)
        resizedGreen = cv2.resize(Green_mask, dim, interpolation=cv2.INTER_AREA)
        resizedBlue = cv2.resize(Blue_mask, dim, interpolation=cv2.INTER_AREA)

        cv2.imshow("Yellow Mask", resizedYellow)
        cv2.imshow("Green Mask", resizedGreen)
        cv2.imshow("Blue Mask", resizedBlue)

        ##If color not visible give val:
        cx = cy = gx = gy = bx = by = 0

        #Create empty color lists
        yellowlistX = []
        yellowlistY = []

        greenlistX = []
        greenlistY = []

        bluelistX = []
        bluelistY = []

        ############## YELLOW #####################
        # FIND contours
        cnts, hei = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for i in cnts:
            area = cv2.contourArea(i)
            # CHECK AREA OF SHAPE
            if area > area_max:
                peri = cv2.arcLength(i, True)
                approx = cv2.approxPolyDP(i, 0.02 * peri, True)
                x, y, w, h = cv2.boundingRect(i)
                # CENTERMARK
                M = cv2.moments(i)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    yellowlistX.insert(0, cx)       ##MAKE LIST OF ALL YELLOW X

                    cy = int(M['m01'] / M['m00'])
                    yellowlistY.insert(0, cy)       ##MAKE LIST OF ALL YELLOW Y

                    cv2.drawContours(img, [i], -1, (12, 255, 255), 2)
                    cv2.circle(img, (cx, cy), 3, (244, 0, 255), -1)
                    cv2.putText(img, "", (cx - 20, cy - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                    cv2.putText(img, "X" + str(cx) + " Y" + str(480 - cy), (cx - 50, cy - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 100, 200), 1)
                cv2.putText(img, "Yellow", (cx - 20, cy + 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255), 1)

        ###############GREEN######################
        greencnts, hei = cv2.findContours(Green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for i in greencnts:
            area = cv2.contourArea(i)
            # CHECK AREA OF SHAPE
            if area > area_max:
                peri = cv2.arcLength(i, True)
                approx = cv2.approxPolyDP(i, 0.02 * peri, True)
                x, y, w, h = cv2.boundingRect(i)
                # CENTERMARK
                M = cv2.moments(i)
                if M['m00'] != 0:
                    gx = int(M['m10'] / M['m00'])
                    greenlistX.insert(0, gx)

                    gy = int(M['m01'] / M['m00'])
                    greenlistY.insert(0, gy)

                    cv2.drawContours(img, [i], -1, (0, 177, 0), 2)
                    cv2.circle(img, (gx, gy), 3, (255, 0, 255), -1)
                    cv2.putText(img, "", (gx - 20, gy - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                    cv2.putText(img, "X" + str(gx) + " Y" + str(480 - gy), (gx - 50, gy - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 100, 255), 1)
                cv2.putText(img, "GREEN", (gx - 20, gy + 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 1)

        ###############BLUE######################
        bluecnts, hei = cv2.findContours(Blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for i in bluecnts:
            area = cv2.contourArea(i)
            # CHECK AREA OF SHAPE
            if area > area_max:
                peri = cv2.arcLength(i, True)
                approx = cv2.approxPolyDP(i, 0.02 * peri, True)
                x, y, w, h = cv2.boundingRect(i)

                # CENTERMARK
                M = cv2.moments(i)
                if M['m00'] != 0:
                    bx = int(M['m10'] / M['m00'])
                    bluelistX.insert(0, bx)


                    by = int(M['m01'] / M['m00'])
                    bluelistY.insert(0, by)

                    cv2.drawContours(img, [i], -1, (255, 25, 0), 2)
                    cv2.circle(img, (bx, by), 3, (255, 0, 255), -1)
                    cv2.putText(img, "", (bx - 20, by - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                    cv2.putText(img, "X" + str(bx) + " Y" + str(480 - by), (bx - 50, by - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                    # END CENTERMARK
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 100, 255), 1)
                cv2.putText(img, "BLUE", (bx - 20, by + 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 54, 42), 2)

        ###############END OF ALL MASKS AND FILTERS####################

        # Show user-screen
        win_Width = 800
        win_Height = 800
        dim = (win_Width, win_Height)
        resizedMain = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        cv2.imshow("frame", resizedMain)
        # Lists number of objects detected
        yellow_listsize = len(yellowlistX)
        green_listsize = len(greenlistX)
        blue_listsize = len(bluelistX)

        #Wait for user input. SPACE = count all numbers and print ESC = quit, a= all objects y= all yellow. g = green. b = blue
        k = cv2.waitKey(1)

        if k % 256 == 32:  #####SPACE = Capture cords
            print("\nYellow pieces = ", yellow_listsize)
            print("Green pieces = ", green_listsize)
            print("Blue pieces = ", blue_listsize)

            totalpieces = yellow_listsize + green_listsize + blue_listsize
            print("\nTotal number of pieces = ", totalpieces)

        # Quit
        elif k == ord('q'):
            print("Escape hit, closing...")
            video.release()
            break
        # Yellow
        elif k == ord('y'):
            newGcodestart()
            pickallof_color(yellow_listsize, yellowlistX, yellowlistY, yellowdropX, yellowdropY)
            addReturnmove()
            send()
        # Green
        elif k == ord('g'):
            newGcodestart()
            pickallof_color(green_listsize, greenlistX, greenlistY, greendropX, greendropY)
            addReturnmove()
            send()
        # Blue
        elif k == ord('b'):
            newGcodestart()
            pickallof_color(blue_listsize, bluelistX, bluelistY, bluedropX, bluedropY)
            addReturnmove()
            send()
        # All colors
        elif k == ord('a'):
            newGcodestart()
            pickallof_color(yellow_listsize, yellowlistX, yellowlistY, yellowdropX, yellowdropY)
            pickallof_color(green_listsize, greenlistX, greenlistY, greendropX, greendropY)
            pickallof_color(blue_listsize, bluelistX, bluelistY, bluedropX, bluedropY)
            addReturnmove()
            sleep(0.5)
            send()

        sleep(0.1)


takepicture()

cv2.destroyAllWindows()