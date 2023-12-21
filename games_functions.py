import random
import time

import math
import numpy as np
import mss
import mss.tools
from PIL import Image
import pyautogui

import utility_functions


cards_x_coord = [[858], [785, 930], [728, 862, 995], [662, 793, 927, 1060], [597, 730, 863, 995, 1125],
                 [580, 710, 845, 975, 1105, 1238],
                 [563, 695, 825, 955, 1088, 1220, 1350], [545, 675, 808, 940, 1070, 1200, 1332, 1462],
                 [530, 660, 790, 922, 1052, 1183, 1313, 1445, 1575]]  # place of cards in hand

positions = {
    1: [(858, 865)],
    2: [(785, 865), (930, 860)],
    3: [(728, 860), (862, 860), (995, 860)],
    4: [(662, 860), (793, 860), (927, 860), (1060, 860)],
    5: [(597, 863, 644), (730, 863, 777), (863, 860, 910), (995, 860, 1040), (1125, 860, 1175)],
    6: [(580, 863, 627), (710, 863, 760), (845, 863, 890), (975, 860, 1023), (1105, 860, 1155), (1238, 860, 1285)],
    7: [(563, 863, 612), (695, 863, 744), (825, 863, 874), (955, 860, 1005), (1088, 860, 1135), (1220, 860, 1267),
        (1350, 860, 1397)],
    8: [(545, 863, 595), (675, 863, 725), (808, 863, 855), (940, 863, 987), (1070, 860, 1119), (1200, 860, 1250),
        (1332, 860, 1380), (1462, 858, 1512)],
    9: [(530, 863, 577), (660, 863, 707), (790, 863, 837), (922, 862, 970), (1052, 860, 1100), (1183, 860, 1231),
        (1313, 860, 1362), (1445, 858, 1493), (1575, 858, 1623)]
}


def pick_card(cards_costs, position_in_order):
    """
    Playing a card from hand

    :param cards_costs: list of positions and costs of cards in hand
    :param position_in_order: Position of the card in the hand in order from the left edge
    """
    if position_in_order >= len(cards_costs):
        raise ValueError('Index out of range')
    print(f'Play card #{position_in_order}')
    card_x = cards_x_coord[len(cards_costs) - 1][position_in_order] + 80
    pyautogui.moveTo(card_x, 960, duration=random.randint(1, 5) / 10)
    time.sleep(1)
    pyautogui.moveTo(card_x, 550, duration=random.randint(1, 5) / 10)
    pyautogui.mouseDown()
    pyautogui.moveTo(1370, 280, duration=random.randint(1, 5) / 10)
    pyautogui.mouseUp()


def concede_check():
    """
    Checks whether the opponent has given up,
    in this case the game sometimes shows a message in which you need to press a button

    :return: True if message shown False if didn't
    """
    concede = utility_functions.image_processing(685, 495, 545, 30, 0, 0, 0, 122, 122, 255, mode='grab_text', psm=7)
    concede = concede if concede is not None else ''
    if 'shutdown' in concede:
        pyautogui.moveTo(955, 570, duration=random.randint(1, 5) / 10)
        utility_functions.click()
        time.sleep(1)
        return True
    return False


def taunt_check(card_position):
    """
    Сhecks whether the taunt is covering the opponent’s face

    :param card_position: Position of card which was blocked by taunt
    :return: True, if there was a taunt, False, if there wasn’t
    """
    taunt_message = utility_functions.image_processing(740, 90, 440, 35, 0, 0, 0, 122, 122, 255, mode='grab_text',
                                                       psm=7)
    taunt_message = taunt_message if taunt_message is not None else ''
    if 'target' in taunt_message:
        for i in range(0, 6):
            message_region = {"top": 300, "left": (450 + 170 * i), "width": 160, "height": 5}
            with mss.mss() as sct:
                img = np.array(sct.grab(message_region), dtype=np.uint8)
                img = Image.fromarray(np.flip(img[:, :, :3], 2))
            j = utility_functions.find_colors(img)
            if j:
                pyautogui.moveTo(card_position, 585, duration=random.randint(1, 5) / 10)
                pyautogui.mouseDown()
                pyautogui.moveTo((420 + j + 170 * i), 340, duration=random.randint(1, 5) / 10)
                pyautogui.mouseUp()
                time.sleep(2)
        return True
    return False


def card_mana(x, y, shifted_x=None):
    """
    Finding the mana value of a card in hand

    :param x: x coordinate of mana value
    :param y: x coordinate of mana value
    :param shifted_x: When you first point the cards at your hand,
                        the cards shift slightly on the screen in X direction;
                        so in the future you need to use the shifted x value
    :return: Card mana value or max value
    """
    max_mana = 4
    a = utility_functions.image_processing(x, y, 25, 35, 0, 0, 230, 0, 0, 255, mode='grab_digit', use_bitwise_and=False,
                                           psm=7, whitelist='1234')
    if a.strip():
        return int(a)
    elif shifted_x:
        a = utility_functions.image_processing(shifted_x, y, 25, 35, 0, 0, 230, 0, 0, 255, mode='grab_digit',
                                               use_bitwise_and=False, psm=7, whitelist='1234')
        if a.strip():
            return int(a)

    return max_mana


def check_game_loading():
    """
    Checks if the game has loaded after it was found

    :return: 0 or 1 or None, 0 means the game ended due to some normal reason, 1 means the game ended due to an error,
             None means the game loaded fine
    """
    start_time = time.time()
    one_time_print = True
    while True:
        if one_time_print:
            print('wait until game loading')
            one_time_print = False
        if utility_functions.image_processing(850, 730, 250, 60, 0, 0, 0, 0, 0, 255, mode='check_text', text='confirm'):
            return 0

        if concede_check():
            return 0

        time.sleep(1)

        if time.time() - start_time > 360.0:
            return 1


def to_the_face(x, y):
    """
    Creature attack opponent`s face

    :param x: x coordinate of creature on the board
    :param y: y coordinate of creature on the board
    """
    pyautogui.moveTo(x, y, duration=random.randint(1, 5) / 10)
    pyautogui.mouseDown()
    pyautogui.moveTo(960, 150, duration=random.randint(1, 5) / 10)
    pyautogui.mouseUp()
    time.sleep(0.2)


def attack():
    """
    Attack with all creatures
    """
    card_x_positions = [560, 720, 810, 910, 1100, 1250, 1380]
    card_y_position = 590
    for position in card_x_positions:
        to_the_face(position, card_y_position)
        if taunt_check(position):
            to_the_face(position, card_y_position)
    if utility_functions.image_processing(760, 760, 130, 55, 0, 0, 0, 0, 0, 255, 'grab_digit', psm=7,
                                          whitelist='0123456789'):
        to_the_face(960, 800)


def count_of_mana():
    """
    Looks up the current mana value

    :return: current mana value
    """
    mana = 0
    for psm in [7, 6]:
        search_mana = utility_functions.image_processing(185, 950, 45, 60, 0, 0, 0, 0, 0, 255, mode='grab_digit',
                                                         psm=psm, whitelist='0123456789')
        if search_mana is not None:
            if len(search_mana) > 0:
                mana = int(search_mana)
                return mana
    return mana


def generate_combination(input_list, mana):
    """
    Generates combinations of cards that are best suited for mana and random choose one of them

    :param input_list: list of positions and costs of cards in hand
    :param mana: current amount of mana
    :return: One of best suited combinations of cards to play
    """
    order_list = [i for i in range(len(input_list))]
    combinations = []
    equal = []
    less = []
    card_costs_dict = {}
    card_combinations = []
    n = len(input_list)

    for i in range(1, 2 ** n):
        subset = [order_list[j] for j in range(n) if (i & (2 ** j)) > 0]
        combinations.append(tuple(subset))

    for combo in combinations:
        subset = [input_list[j] for j in combo]
        card_combinations.append(tuple(subset))

    summ_combinations = [sum(i) for i in card_combinations]
    for i in range(len(card_combinations)):
        card_costs_dict[combinations[i]] = summ_combinations[i]

    for key, value in card_costs_dict.items():
        if value == mana:
            equal.append(key)
        if value < mana:
            less.append(key)

    if equal:
        result = random.choice(equal)
    elif less:
        result = random.choice(less)
    else:
        result = ()

    return result


def pick_best_card(cards_costs, mana):
    """
    Plays cards that are best suited for mana

    :param cards_costs: list of positions and costs of cards in hand
    :param mana: current amount of mana
    :return: number of cards played
    """
    cards_played = 0
    combo = generate_combination(cards_costs, mana)
    print(combo)
    for value in combo:
        pick_card(cards_costs, value - cards_played)
        cards_costs.pop(value - cards_played)
        cards_played += 1

        print(f'Hand -> {cards_costs}')

    return cards_played


def check_game_state():
    """
    Checking the game state during the opponent's turn

    :return: 0 or 1 or 2, 0 means game is over normally, 1 means opponent concede, 2 means opponent's turn is over
    """
    start_time = time.time()
    one_time_print = True
    while utility_functions.image_processing(1600, 445, 5, 5, 0, 0, 0, 255, 255, 252, mode='find_color') is not None:
        if one_time_print:
            print('wait opp turn')
            one_time_print = False
        if utility_functions.image_processing(870, 970, 170, 30, 0, 0, 0, 0, 0, 255, mode='check_text', text='continue'):
            return 0
        if concede_check():
            return 1
        if time.time() - start_time > 300.0:
            return 1
    return 2


def playing_cards_or_power(extra_mana, cards_in_hand):
    """
    Selection of actions depending on game parameters

    :param extra_mana: extra mana counter, 3 maximum
    :param cards_in_hand: number of cards in hand
    :return: number of cards in hand and extra mana counter for further turns
    """
    mana = count_of_mana()

    if mana > 1:
        if extra_mana < 3:
            pyautogui.moveTo(300, 1020, duration=random.randint(1, 5) / 10)
            utility_functions.click()
            extra_mana += 1
            time.sleep(2)
            mana = count_of_mana()

    print(f'mana - {mana}')

    while mana != 0:
        start_mana = mana
        print(f'I have {mana} mana')
        cards_costs = [card_mana(*pos) for pos in positions.get(cards_in_hand, [])]
        print(f'Cards in hand - {len(cards_costs)}')
        print(cards_costs)
        full_board = full_board_check()
        if not full_board:
            cards_played = pick_best_card(cards_costs, mana)
            cards_in_hand -= cards_played
        time.sleep(2)
        mana = count_of_mana()

        if start_mana == mana:
            if mana >= 2:
                if not full_board:
                    pyautogui.moveTo(1080, 730, duration=random.randint(1, 5) / 10)  # hero power
                    utility_functions.click()
            mana = 0
        time.sleep(1)
        cards_costs.clear()

    return cards_in_hand, extra_mana


def full_board_check():
    """
    Checks if the board is filled with creatures

    :return: True if board is filled, False if it does not
    """
    if utility_functions.image_processing(442, 642, 28, 33, 0, 0, 0, 0, 0, 255, 'grab_digit', psm=7,
                                          whitelist='0123456789'):
        return True
    return False


def random_mouse_moves():
    """
    Random mouse movements after a move, imitation of human actions
    """
    for j in range(0, random.randint(0, 2)):
        SIZE_X = random.randint(200, 800)
        SIZE_Y = random.randint(200, 800)
        num_steps = random.randint(2, 3)
        for i in range(num_steps):
            t = (((i / num_steps) * 2) * math.pi)
            if i < num_steps // 2:
                x = math.cos(t)
                y = math.sin(t)
                pyautogui.moveTo(SIZE_X / 2 + (SIZE_Y / 3) * x, SIZE_Y / 2 + (SIZE_Y / 3) * y,
                                 duration=random.randint(3, 8) / 10)
            else:
                x = abs(math.sin(t))
                y = abs(math.cos(t))
                pyautogui.moveTo(SIZE_X / 3 + (SIZE_Y / 2) * x, SIZE_Y + (SIZE_Y / 4) * y,
                                 duration=random.randint(3, 8) / 10)


def game():
    """
    Main game function

    :return: 0 or 1 where 0 means successful completion, 1 means an error occurred during execution
    """
    pyautogui.moveTo(940, 460, duration=random.randint(1, 5) / 10)  # choose 2nd hero power
    utility_functions.click()
    time.sleep(1)
    pyautogui.moveTo(950, 760, duration=random.randint(1, 5) / 10)  # confirm
    utility_functions.click()
    pyautogui.moveTo(950, 915, duration=random.randint(1, 5) / 10)  # keep this

    print('start game')
    timing_ = time.time()
    one_time_print = True
    while not utility_functions.image_processing(185, 950, 45, 55, 0, 0, 0, 0, 0, 255, mode='check_text', text='1'):
        if one_time_print:
            print('wait opp choice and turn')
            one_time_print = False
        utility_functions.click()
        print('wait')
        time.sleep(1)
        if time.time() - timing_ > 180.0:
            break

    time.sleep(2)
    pyautogui.moveTo(300, 480, duration=random.randint(1, 5) / 10)
    time.sleep(2)
    cards_in_hand = 4
    timing_ = time.time()
    extra_mana = 0
    one_time_print = True
    while not utility_functions.image_processing(870, 970, 170, 30, 0, 0, 0, 0, 0, 255, mode='check_text',
                                                 text='continue'):
        if one_time_print:
            print('main loop game start while does not appear continue button after win or lose')
            one_time_print = False

        cards_in_hand, extra_mana = playing_cards_or_power(extra_mana, cards_in_hand)

        if concede_check():
            return 1

        attack()

        if not full_board_check():
            cards_in_hand, extra_mana = playing_cards_or_power(extra_mana, cards_in_hand)

        pyautogui.moveTo(1630, 500, duration=random.randint(1, 5) / 10)
        utility_functions.click()

        random_mouse_moves()

        for i in range(2):
            flag = check_game_state()
            if flag != 2:
                return flag
            time.sleep(1)

        time.sleep(3)
        cards_in_hand += 1

        if time.time() - timing_ > 1800.0:
            return 1

    return 0
