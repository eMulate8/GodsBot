import os
from ctypes import windll, create_unicode_buffer
import time

import cv2
from fuzzywuzzy import fuzz
import wmi
import pyautogui
import pytesseract
import numpy as np

import personal_settings


def find_colors(img):
    """
    Looks for bright colors in an image
    :param img: the image on which the search will be carried out in array format
    :return: coordinate of the center of bright spot
    """
    width, height = img.size[:2]
    px = np.array(img)

    for i in range(height):
        for j in range(width):
            if px[i, j, 0] > 150 & px[i, j, 1] > 150 & px[i, j, 2] > 100:
                return int(j)


def image_processing(screen_x, screen_y, width, height, a1, a2, a3, b1, b2, b3, mode, psm=6, whitelist=None,
                     text=None, use_bitwise_and=True):
    """
    Processing a screen area;
    in the find_color mode, a specified color is searched;
    in the grab_text and grab_digit modes, text or numbers are captured from the area;
    in the check_text mode, the text in the area is checked for compliance with a given pattern

    :param screen_x: x coordinates of the upper left corner of the treated area on the screen
    :param screen_y: y coordinates of the upper left corner of the treated area on the screen
    :param width: width of the treated area on the screen
    :param height: height of the treated area on the screen
    :param a1: lower border of hsv
    :param a2: lower border of hsv
    :param a3: lower border of hsv
    :param b1: upper border of hsv
    :param b2: upper border of hsv
    :param b3: upper border of hsv
    :param mode: function operating mode: find_color, check_text, grab_text or grab_digit
    :param psm: pytesseract recognize text setting, choose 7 or 6
    :param whitelist: list of valid values
    :param text: text for search
    :param use_bitwise_and: uses cv2.bitwise_and or not
    :return: in find_color mode - pixel coordinates with the desired color,
             in check_text mode - True if the texts matches, False if its don't,
             in grab_text or grab_digit mode - recognized text or digit(s)
    """
    monitor = (screen_x, screen_y, width, height)

    config = f'--psm {psm}'
    config = f'{config} -c tessedit_char_whitelist={whitelist}' if whitelist else config

    lower_color = np.array([a1, a2, a3])
    upper_color = np.array([b1, b2, b3])
    pyautogui.screenshot('image_scr.png', region=monitor)
    im = cv2.imread('image_scr.png')
    try:
        image = np.asarray(im)
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)

    if use_bitwise_and:
        result = cv2.bitwise_and(image, image, mask=mask)
        rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    else:
        rgb = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

    cv2.imwrite('rgb_test.png', rgb)

    if mode == 'find_color':
        coord = cv2.findNonZero(mask)
        return coord

    if mode == 'check_text' and text:
        for psm_value in range(psm, psm + 2):
            try:
                recognized_text = pytesseract.image_to_string(rgb, lang='eng', config=f'--psm {psm_value} {whitelist}')
                if (fuzz.ratio(recognized_text.lower(), text.lower()) > 50) or (
                        text.lower() in recognized_text.lower()):
                    return True
            except pytesseract.TesseractError as e:
                print(f"Error recognizing text: {e}")

        return False

    if mode in ['grab_text', 'grab_digit']:
        try:
            recognized_text = pytesseract.image_to_string(rgb, lang='eng', config=config)
            if recognized_text == '':
                recognized_text = pytesseract.image_to_string(rgb, lang='rus', config=config)
            return recognized_text.lower()
        except pytesseract.TesseractError as e:
            print(f"Error recognizing text: {e}")
            return ''


def run_client():
    """
    Launches the game client at the specified path
    """
    terminate_client()
    time.sleep(15)
    print('run client')
    os.startfile(personal_settings.CLIENT_PATH)
    time.sleep(10)


def click():
    """
    Left mouse click
    """
    pyautogui.mouseDown()
    time.sleep(0.01)
    pyautogui.mouseUp()


def terminate_client():
    """
    Kill game's process(es)
    """
    c = wmi.WMI()
    for proc in c.Win32_Process(name="Gods Unchained.exe"):
        print(proc.ProcessId, proc.Name)
        try:
            proc.Terminate()
        except Exception:
            pass


def get_foreground_window_title():
    """
    Get active window title
    :return: window title or None
    """
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    if buf.value:
        return buf.value
    return None


def check_client_active():
    """
    Check if the game is running
    :return: True if game is running, False if it does not
    """
    print('check_client_active')
    window_name = get_foreground_window_title()
    if window_name == 'Gods Unchained' or window_name == 'gods':
        return True
    return False
