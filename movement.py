import pyautogui
pyautogui.PAUSE = 2.5
pyautogui.FAILSAFE = True

def go_to_left_desktop():
    pyautogui.hotkey('ctrl', 'left')

def go_to_right_desktop():
    pyautogui.hotkey('ctrl', 'right')