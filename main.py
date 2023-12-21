import datetime
import os
import random
import time

import pyautogui
import pytesseract

import games_functions
import utility_functions
import personal_settings

pytesseract.pytesseract.tesseract_cmd = personal_settings.PYTESSERACT_PATH
pyautogui.FAILSAFE = False
count_of_games = 0

wins = 0
loses = 0
close_flag = 0

if __name__ == '__main__':

    while True:
        time.sleep(5)
        current_time = datetime.datetime.now()
        if count_of_games < random.randint(28, 35) and ((0 <= current_time.hour <= 2) or current_time.hour >= 7):

            if close_flag == 1:
                utility_functions.run_client()
                close_flag = 0

            if utility_functions.check_client_active():
                play_button_visible = utility_functions.image_processing(895, 820, 50, 15, 0, 0, 0, 0, 0, 255,
                                                                         mode='check_text', text='play')
                update_button_visible = utility_functions.image_processing(645, 915, 65, 20, 0, 0, 0, 150, 150, 150,
                                                                           mode='check_text', text='update')
                game_search_engaged = utility_functions.image_processing(325, 840, 40, 25, 0, 0, 0, 255, 20, 255,
                                                                         mode='check_text', text='00')
                continue_button_visible = utility_functions.image_processing(910, 795, 100, 15, 0, 0, 0, 0, 0, 255,
                                                                             mode='check_text', text='continue')
                skip_button_visible = utility_functions.image_processing(460, 258, 40, 15, 0, 0, 0, 0, 0, 255,
                                                                         mode='check_text', text='skip')
                confirm_button_visible = utility_functions.image_processing(850, 730, 250, 60, 0, 0, 0, 0, 0, 255,
                                                                            mode='check_text', text='confirm')
                one_time_print = True

                while not play_button_visible:

                    if one_time_print:
                        print('check play/update button')
                        one_time_print = False
                    time.sleep(1)
                    if update_button_visible:
                        pyautogui.moveTo(700, 925, duration=random.randint(1, 5) / 10)
                        utility_functions.click()
                        time.sleep(360)

                one_time_print = True

                while not game_search_engaged:
                    if one_time_print:
                        print('check 00 in search timer')
                        one_time_print = False
                    pyautogui.moveTo(920, 825, duration=random.randint(1, 5) / 10)
                    utility_functions.click()
                    time.sleep(2)
                    if confirm_button_visible:
                        break
                    if skip_button_visible:
                        pyautogui.moveTo(480, 265, duration=random.randint(1, 5) / 10)
                        utility_functions.click()
                        time.sleep(3)
                    if continue_button_visible:
                        pyautogui.moveTo(960, 800, duration=random.randint(1, 5) / 10)
                        utility_functions.click()
                        time.sleep(3)

                print('start search')
                close_flag = games_functions.check_game_loading()
                if close_flag == 1:
                    continue
                close_flag = games_functions.game()
                if close_flag == 1:
                    continue
                print('end game')
                time.sleep(2)

                result_of_game = utility_functions.image_processing(770, 550, 355, 115, 0, 0, 105, 30, 105, 255,
                                                                    mode='grab_text', psm=7)

                if 'v' in result_of_game:
                    wins += 1
                    count_of_games += 1
                    print(f'Win!  Stat: {wins} W - {loses} L')
                else:
                    loses += 1
                    count_of_games += 1
                    print(f'Lose!  Stat: {wins} W - {loses} L')

                time.sleep(2)
                utility_functions.terminate_client()
                time.sleep(2)
                utility_functions.run_client()
                one_time_print = True
                while not utility_functions.image_processing(880, 815, 70, 25, 0, 0, 0, 0, 0, 255, mode='check_text',
                                                             text='Play'):
                    if one_time_print:
                        print('check play/update button')
                        one_time_print = False
                    time.sleep(1)
                    if utility_functions.image_processing(645, 915, 65, 20, 0, 0, 0, 150, 150, 150, mode='check_text',
                                                          text='update'):
                        pyautogui.moveTo(700, 925, duration=random.randint(1, 5) / 10)
                        utility_functions.click()
                        time.sleep(360)

            else:
                utility_functions.run_client()
                close_flag = 0
        else:
            if utility_functions.check_client_active():
                utility_functions.terminate_client()
                with open('stat.txt', 'w', encoding='utf-8') as file:
                    file.write(f'{count_of_games} games: {wins} W - {loses} L')
                break

    # shutdown computer after bot finished with 1-minute delay
    os.system("shutdown -s -t  60 ")
