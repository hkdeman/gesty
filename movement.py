import pyautogui
pyautogui.PAUSE = 0.25
pyautogui.FAILSAFE = True

def go_to_left_desktop():
    pyautogui.hotkey('ctrl', 'left')

def go_to_right_desktop():
    pyautogui.hotkey('ctrl', 'right')

def lock_computer():
    pyautogui.hotkey('command', 'space')
    pyautogui.typewrite('lock')
    pyautogui.press('enter')

def press_right():
    pyautogui.press('right')

def press_left():
    pyautogui.press('left')

def scroll_up():
    pyautogui.scroll(10)

def scroll_down():
    pyautogui.scroll(-10)
