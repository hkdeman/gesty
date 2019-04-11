import cv2
import numpy as np
from collections import deque
import movement

cv2.namedWindow("preview")
vc = cv2.VideoCapture(1)

vc.set(3, 160)
vc.set(4, 120)

width = vc.get(3)
height = vc.get(4)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

swipe_movement_buffer = deque(maxlen=15)

def get_roi(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_skin_tone = np.array([0, 80, 30])
    upper_skin_tone = np.array([35, 160,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_skin_tone, upper_skin_tone)
    
    mask = cv2.erode(mask, np.ones((2,2)), iterations=1)

    return mask


def get_contours(grayscale, frame):
    ret, thresh = cv2.threshold(grayscale, 127, 255, 0)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # print(len(contours))
    c = max(contours, key = cv2.contourArea)
    area = cv2.contourArea(c)
    if  area > 1000:
        return c
    else:
        return None

def get_fingers(contour, frame):
    extLeft = tuple(contour[contour[:, :, 0].argmin()][0])
    extRight = tuple(contour[contour[:, :, 0].argmax()][0])
    extTop = tuple(contour[contour[:, :, 1].argmin()][0])
    extBot = tuple(contour[contour[:, :, 1].argmax()][0])

    # print(extLeft, extRight, extTop, extBot)

    if abs(extBot[1]-height) < 20:
        cv2.drawContours(frame, [contour], -1, (0,255,0), 3)
        cv2.circle(frame, extLeft, 8, (0, 0, 255), -1)
        cv2.circle(frame, extRight, 8, (0, 255, 0), -1)
        cv2.circle(frame, extTop, 8, (255, 0, 0), -1)
        cv2.circle(frame, extBot, 8, (255, 255, 0), -1)
        swipe_movement_buffer.append(extTop)
    else:
        swipe_movement_buffer.clear()


while rval:
    rval, frame = vc.read()
    blurred = cv2.GaussianBlur(frame.copy(), (11, 11), 0)
    f = get_roi(blurred)
    contour = get_contours(f, frame)
    if contour is not None:
        fingers = get_fingers(contour, frame)

    if len(swipe_movement_buffer) == swipe_movement_buffer.maxlen:
        swipe_strength = swipe_movement_buffer[-1][0] - swipe_movement_buffer[0][0]
        print(swipe_strength)
        if abs(swipe_strength) > 100:
            if swipe_strength < 0:
                movement.go_to_left_desktop()
            else:
                movement.go_to_right_desktop()
            swipe_movement_buffer.clear()



    # frame = get_contours(frame)
    # cv2.imshow("preview", frame)
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

cv2.destroyWindow("preview")
vc.release()
