import cv2
import numpy as np
from collections import deque
import movement
import notify

mode_index = 0
modes = ['Desktop', 'Application']

notify.notify(modes[mode_index])

vc = cv2.VideoCapture(0)

vc.set(3, 120)
vc.set(4, 160)

width = vc.get(3)
height = vc.get(4)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

swipe_movement_buffer = deque(maxlen=30)

first_quarter = swipe_movement_buffer.maxlen//4
third_quarter = 3 * first_quarter

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
    if len(contours) == 0: return None
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

    if abs(extBot[1]-height) < 50:
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
        swipe_strength_x = swipe_movement_buffer[-1][0] - swipe_movement_buffer[0][0]
        swipe_strength_y = swipe_movement_buffer[-1][1] - swipe_movement_buffer[0][1]
        change_mode_strength = swipe_movement_buffer[first_quarter][1] - swipe_movement_buffer[third_quarter][1]
        # if (abs(change_mode_strength) > 100 and abs(swipe_strength) > 100):
        #     if swipe_strength < 0:
        #         mode_index = mode_index - 1 if mode_index > 0 else 0
        #     else:
        #         mode_index = mode_index + 1 if mode_index < len(modes) - 1  else len(modes) - 1
        #     notify.notify(modes[mode_index])
        #     swipe_movement_buffer.clear()
        if abs(swipe_strength_x) > 200:
            if (modes[mode_index] == 'Desktop'):
                if swipe_strength_x < 0:
                        movement.go_to_left_desktop()
                else:
                    movement.go_to_right_desktop()
            elif (modes[mode_index] == 'Application'):
                if swipe_strength_x < 0:
                        movement.press_left()
                else:
                    movement.press_right()
            swipe_movement_buffer.clear()
        elif abs(swipe_strength_y) > 100:
            if (modes[mode_index] == 'Desktop'):
                pass
            elif (modes[mode_index] == 'Application'):
                if swipe_strength_y < 0:
                        movement.scroll_down()
                else:
                    movement.scroll_up()
            
            swipe_movement_buffer.clear()

vc.release()
