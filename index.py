# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import io
import json
import os
import re
import sys
import time
from os import listdir
from random import randint, random
from PIL import Image

import mss
import numpy as np
import pyautogui
import requests
import yaml
from cv2 import cv2
import pytesseract

from src.logger import logger

stream = open("config.yaml", "r")
c = yaml.safe_load(stream)
ct = c["threshold"]
pause = c["time_intervals"]["interval_between_movements"]
pyautogui.PAUSE = pause
screen_text = "screen{}"

REPORT_PATH = '.\\report\\'

cat = """
>>---> Press ctrl + c to kill the bot.

>>---> Some configs can be found in the config.yaml file.
#########################################################
###                                                   ###
###                     Donate                        ###
###    0xc0A75D88D49D38fFa0E96EA2ec808965cF090521     ###
###                                                   ###
#########################################################
"""


def add_randomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    return int(randomized_n)


def move_to_with_randomness(x, y, t):
    try:
        pyautogui.moveTo(add_randomness(x, 10), add_randomness(y, 10),
                         t + random() / 2)
    except:
        logger('Error move to with randomness')


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def load_images(dir_path="./targets/"):
    file_names = listdir(dir_path)
    targets = {}
    for file in file_names:
        path = "targets/" + file
        targets[remove_suffix(file, ".png")] = cv2.imread(path)

    return targets


def click_btn(img, timeout=3, threshold=ct["default"]):
    logger(None, progress_indicator=True)
    start = time.time()
    has_timed_out = False
    while not has_timed_out:
        matches = positions(img, threshold=threshold)

        if len(matches) == 0:
            has_timed_out = time.time() - start > timeout
            continue

        x, y, w, h = matches[0]
        pos_click_x = x + w / 2
        pos_click_y = y + h / 2
        move_to_with_randomness(pos_click_x, pos_click_y, 1)
        pyautogui.click()
        return True

    return False


def check_screen(img, timeout=3, threshold=ct["default"]):
    logger(None, progress_indicator=True)
    start = time.time()
    has_timed_out = False
    while not has_timed_out:
        matches = positions(img, threshold=threshold)

        if len(matches) == 0:
            has_timed_out = time.time() - start > timeout
            continue
        return True

    return False


def check_on_print(img, x, y, timeout=3, threshold=ct["common"]):
    logger(None, progress_indicator=True)
    start = time.time()
    has_timed_out = False
    while not has_timed_out:
        matches = positions_of(img, x, y, threshold=threshold)

        if len(matches) == 0:
            has_timed_out = time.time() - start > timeout
            continue
        return True

    return False


def check_on_offset(img, x, y, w, h, timeout=3, threshold=ct["common"]):
    logger(None, progress_indicator=True)
    start = time.time()
    has_timed_out = False
    while not has_timed_out:
        matches = positions_of_offset(img, x, y, w, h, threshold=threshold)

        if len(matches) == 0:
            has_timed_out = time.time() - start > timeout
            continue
        return True

    return False


def print_screen():
    with mss.mss() as sct:
        monitor_crop = {
            "top": 0,
            "left": 0,
            "width": c["window_width"],
            "height": c["window_height"],
        }
        sct_img = np.array(sct.grab(monitor_crop))
        return sct_img[:, :, :3]


def print_of_offset(x, y, w, h):
    with mss.mss() as sct:
        monitor_crop = {
            "top": y,
            "left": x,
            "width": w,
            "height": h,
        }
        # x = sct.grab(monitor_crop)
        # output = "sct-{top}x{left}_{width}x{height}.png".format(**monitor_crop)
        # mss.tools.to_png(x.rgb, x.size, output=output)
        sct_img = np.array(sct.grab(monitor_crop))
        return sct_img[:, :, :3]


def positions(target, threshold=ct["default"], img=None):
    if img is None:
        img = print_screen()
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def positions_of(target, x, y, threshold=ct["default"], img=None):
    if img is None:
        img = print_of_offset(x - 20, y - 110, 90, 120)
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def positions_of_offset(target, x, y, w, h, threshold=ct["default"], img=None):
    if img is None:
        img = print_of_offset(x, y, w, h)
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def positions_of_heroes(threshold=ct["default"], img=None):
    if img is None:
        img = print_screen()

    rectangles = []
    target = images["three-energy"]
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    target = images["two-energy"]
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    target = images["one-energy"]
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def get_heroes_ready(x, y):
    heroes_list = []
    heroes = positions_of_offset(x,
                                 y,
                                 460,
                                 320,
                                 images["three-energy"],
                                 threshold=ct['energy_3'])
    logger('🦸 Found {} heroes energy 3/3'.format(len(heroes)))
    for h in heroes:
        heroes_list.append(h)
    heroes = positions_of_offset(x,
                                 y,
                                 460,
                                 320,
                                 images["two-energy"],
                                 threshold=ct['energy_2'])
    logger('🦸 Found {} heroes energy 2/3'.format(len(heroes)))
    for h in heroes:
        heroes_list.append(h)
    heroes = positions_of_offset(x,
                                 y,
                                 460,
                                 320,
                                 images["one-energy"],
                                 threshold=ct['energy_1'])
    logger('🦸 Found {} heroes energy 1/3'.format(len(heroes)))
    for h in heroes:
        heroes_list.append(h)

    return heroes_list


def check_hero_ready(s):
    global last
    pyautogui.hotkey("ctrl", "1")
    click_ok()
    from_home = False
    name = last[s]['profile_name']
    if name == '':
        name = str(s).capitalize()
    if check_screen(images['boss-hunt'], timeout=1):
        click_btn(images['heros'])
        from_home = True

    if check_screen(
            images['boss-hunt-back-1'],
            timeout=1) and not check_screen(images['warrior-2'], timeout=1):
        goto_home()
        click_btn(images['heros'])
        from_home = True

    if check_screen(
            images['boss-hunt-back-2'],
            timeout=1) and not check_screen(images['warrior-2'], timeout=1):
        goto_home()
        click_btn(images['heros'])
        from_home = True
    pytesseract.pytesseract.tesseract_cmd = r'' + c['tesseract_cmd']
    if check_screen(images['warrior-2'], timeout=1):
        hero_ready = 0
        if not from_home:
            click_btn(images['boss-hunt-back-2'], timeout=3, threshold=0.6)
            click_btn(images['heros'])
        r = positions_of_offset(images["energy-x"],
                                80,
                                250,
                                460,
                                320,
                                threshold=ct['default'])
        # r = get_heroes_ready(80, 250)
        hero_ready = len(r)
        move_to_with_randomness(486, 595, 1)
        pyautogui.dragRel(0,
                          -c["click_and_drag_amount"],
                          duration=1,
                          button="left")
        time.sleep(2)
        r = positions_of_offset(images["energy-x"],
                                80,
                                320,
                                460,
                                320,
                                threshold=ct['default'])
        # r = get_heroes_ready(80, 320)
        hero_ready += len(r)
        if hero_ready > 15:
            hero_ready = 15
        if hero_ready >= c['hero_per_fight']:
            last[s]['ready'] = True
            logger('🦸 [{}] {} hero(s) ready to fight'.format(name, hero_ready))
        else:
            logger(
                '🦸 [{}] Found {} hero(s) have the energy. Not ready to boss hunt'
                .format(name, hero_ready))

        goto_home()


def scroll_heros():
    move_to_with_randomness(203, 517, 1)

    if not c["use_click_and_drag_instead_of_scroll"]:
        pyautogui.scroll(-c["scroll_size"])
    else:
        pyautogui.dragRel(0,
                          -c["click_and_drag_amount"],
                          duration=1,
                          button="left")


def scroll_maps():
    commoms = positions(images["match-complete"], threshold=ct["default"])
    logger(len(commoms))
    if len(commoms) == 0:
        return
    x, y, w, h = commoms[len(commoms) - 1]
    move_to_with_randomness(x, y, 1)
    logger(c["use_click_and_drag_instead_of_scroll"])
    if not c["use_click_and_drag_instead_of_scroll"]:
        pyautogui.scroll(-c["scroll_size"])
    else:
        pyautogui.dragRel(-c["click_and_drag_amount"], 0, duration=1)


def choose_heroes_team_fight(heroes, s):
    global last
    pytesseract.pytesseract.tesseract_cmd = r'' + c['tesseract_cmd']
    offset = 5
    scroll_attemps = 0
    reset_fight(s)
    choose_cnt = 0
    # click_btn(images['expand'])
    while True:
        hwe = positions(images["energy-x"], threshold=ct["common"])
        if len(hwe) > 0:
            i = 1
            for (x, y, w, h) in hwe:
                imgage_of_offset(x - 75, y - 99, 40, 12, 'id-{}.png'.format(i))
                image = cv2.imread('id-{}.png'.format(i))
                gray = get_grayscale(image)
                # thres = thresholding(gray)
                txt = pytesseract.image_to_string(gray,
                                                  lang='eng',
                                                  config='--psm 10')
                # logger(txt)
                logger(str(re.sub('[^0-9]', '', txt)))
                for th in heroes:
                    if str(th) == str(re.sub('[^0-9]', '', txt)):
                        move_to_with_randomness(x + offset + (w / 2),
                                                y + (h / 2), 1)
                        pyautogui.click()
                        choose_cnt += 1
                        if choose_cnt == len(heroes):
                            # click_btn(images['collapse'])
                            break
                if os.path.exists('id-{}.png'.format(i)):
                    os.remove('id-{}.png'.format(i))
                i += 1
        hero_in_fight = positions(images["damage"], threshold=ct["green_bar"])
        if len(hero_in_fight) == len(heroes):
            break
        # else:
        #     click_btn(images['expand'])

        if scroll_attemps < c["scroll_attemps"]:
            scroll_heros()
            scroll_attemps += 1
            time.sleep(3)
        else:
            break

def click_skip():
    click_btn(images['skip'], 1)
    click_btn(images['ok'], 1)
    
    
def check_map():
    m = positions(images["match-complete"], threshold=ct["default"])
    if c["stop_when_completed_map"] > 0 and len(
            m) == c["stop_when_completed_map"]:
        return False

    return True


def fight_boss(s):
    global last
    click_skip()
    click_btn(images["boss-hunt-btn"])
    if is_server_maintenance():
        return False
    if click_btn(images['x']):
        reset_fight(s)
        return True

    if check_screen(images["vs"], timeout=15):
        pyautogui.click()

    fighting = True
    now = time.time()
    start_time = int(round(now * 1000))
    name = last[s]['profile_name']
    if name == '':
        name = str(s).capitalize()

    while fighting:
        if game_error(s):
            return True
        if click_btn(images['x'], timeout=1):
            reset_fight(s)
            return True
        logger(None, progress_indicator=True)
        if click_btn(images["tap-open"]):
            if check_screen(images['tap-to-continue-win'], timeout=5):
                notify_working_screen("👉 [{}] Yeah!!! you win".format(name))
                write_report(last[s]['profile_name'], get_bonus())
                click_btn(images['tap-to-continue-win'], timeout=1)
            fighting = False
        elif check_screen(images["defeat"]):
            if check_screen(images['tap-to-continue-lose'], timeout=5):
                notify_working_screen("👇 [{}] Oops!!! you lose".format(name))
                write_report(last[s]['profile_name'], 0.0)
                click_btn(images['tap-to-continue-lose'], timeout=1)
            fighting = False

        n = int(round(time.time() * 1000))
        if (n - start_time > (n + (15 * (60 * 1000))) - n):
            notify_working_screen(
                '[{}] Boss hunt time over 15 minutes'.format(name), True)
            pyautogui.hotkey("ctrl", "f5")
            return False

    chk = True
    while chk:
        if game_error(s):
            return True
        if check_screen(images["match"], timeout=1):
            logger("👉 [{}] Yeah!! pass the map".format(name))
            chk = False
            last[s]['current_map'] = get_current_map()
            last[s]['current_boss'] = get_current_boss()
            if check_screen(images['match-10'], timeout=3, threshold=0.8):
                last[s]['map_10'] = True
                cm = '10/10'
                if last[s]['current_map'] != '' and last[s][
                        'current_map'] != 'x/10':
                    cm = last[s]['current_map']
                logger('[{}] Fighting on map {}'.format(name, cm))
            else:
                last[s]['map_10'] = False
                logger('[{}] Fighting on map {}'.format(
                    name, last[s]['current_map']))

            if not check_map():
                return False
            else:
                click_btn(images["match"], timeout=1)

        if check_screen(images["boss-hunt-btn"], timeout=1):
            chk = False

    return True


def game_error(s):
    global last
    name = last[s]['profile_name']
    if name == '':
        name = str(s).capitalize()
    if check_screen(images['bg'], timeout=1):
        notify_working_screen(
            "[{}] The Luna Rush has an error occured".format(name), True)
        pyautogui.hotkey("ctrl", "f5")
        return True
    if check_screen(images['logo'], timeout=1):
        notify_working_screen(
            "[{}] Game error couldn't load the game".format(name), True)
        pyautogui.hotkey("ctrl", "f5")
        if check_screen(images['logo'], timeout=15) or click_btn(
                images['alert-ok'], timeout=15):
            notify_working_screen(
                "[{}] Game still loading wating 30 minutes".format(name), True)
            time.sleep(1800)
        else:
            notify_working_screen('[{}] Game is come back'.format(name), True)
        return True
    if check_screen(images['ok'], timeout=1):
        return True

    return False


def remove_hero_when_no_energy():
    pytesseract.pytesseract.tesseract_cmd = r'' + c['tesseract_cmd']
    cf = positions(images["damage"], threshold=ct["green_bar"])
    for d in cf:
        x, y, w, h = d
        imgage_of_offset(x - 80, y - 85, 40, 17, 'e-{}.png'.format(0))
        image = cv2.imread('e-{}.png'.format(0))
        gray = get_grayscale(image)
        # cv2.imwrite('e-gray-{}.png'.format(0), gray)
        txt = pytesseract.image_to_string(gray, lang='eng', config='--psm 10')
        txt = txt.replace('V', '1/', 1)
        txt = re.sub('[^0-9/]', '', txt)

        logger(txt)
        if txt == '0/3':
            move_to_with_randomness(x + 30, y - 100, 1)
            pyautogui.click()

    time.sleep(1)


def choose_heroes(s):
    global last
    reset_fight(s)
    nc = 0
    offset = 5
    scroll_attemps = 0
    name = last[s]['profile_name']
    if name == '':
        name = str(s).capitalize()

    start = time.time()
    pytesseract.pytesseract.tesseract_cmd = r'' + c['tesseract_cmd']
    click_skip()
    while True:
        now = time.time()
        if now - start > add_randomness(30 * 60):
            msg = '🥸  Long time to choose heroes'
            notify_working_screen(msg, True)
            return False
        hrs = []
        heroes = positions(images["three-energy"], threshold=ct['energy_3'])
        logger('🦸 Found {} heroes energy 3/3'.format(len(heroes)))
        for h in heroes:
            hrs.append(h)
        # if len(heroes) <= 0:
        heroes = positions(images["two-energy"], threshold=ct['energy_2'])
        logger('🦸 Found {} heroes energy 2/3'.format(len(heroes)))
        for h in heroes:
            hrs.append(h)
        # if len(heroes) <= 0:
        heroes = positions(images["one-energy"], threshold=ct['energy_1'])
        logger('🦸 Found {} heroes energy 1/3'.format(len(heroes)))
        for h in heroes:
            hrs.append(h)
            
        heroes = hrs
        if (len(heroes) - nc) > 0:
            for (x, y, w, h) in heroes:
                if c['enable_lowest_rarity_fight_on_map10_only']:
                    if last[s]['map_10']:
                        if check_on_print(images['card'], x,
                                          y) or check_on_print(
                                              images['rare'], x, y):
                            move_to_with_randomness(x + offset + (w / 2),
                                                    y + (h / 2), 1)
                            pyautogui.click()
                            time.sleep(1)
                        else:
                            nc += 1
                            logger(
                                '🦸 [{}] Hero is not low rarity skip fight on map 10/10'
                                .format(name))

                    else:
                        move_to_with_randomness(x + offset + (w / 2),
                                                y + (h / 2), 1)
                        pyautogui.click()
                        time.sleep(1)

                else:
                    move_to_with_randomness(x + offset + (w / 2), y + (h / 2),
                                            1)
                    pyautogui.click()
                    time.sleep(1)

                hero_in_fight = positions(images["damage"],
                                          threshold=ct["green_bar"])
                if len(hero_in_fight) == c['hero_per_fight']:

                    if len(hero_in_fight) == c['hero_per_fight']:
                        nc = 0
                        scroll_attemps = 0
                        return True

            hero_in_fight = positions(images["damage"],
                                      threshold=ct["green_bar"])
            if len(hero_in_fight) == c['hero_per_fight']:
                return True
            else:
                scroll_heros()
                time.sleep(1)
                scroll_attemps += 1
                nc = 0
        else:
            if scroll_attemps < c["scroll_attemps"]:
                scroll_heros()
                time.sleep(1)
                scroll_attemps += 1
                nc = 0
            else:
                hero_in_fight = positions(images["damage"],
                                          threshold=ct["green_bar"])
                if len(hero_in_fight) == c['minimum_hero_per_fight']:
                    return True
                else:
                    reset_fight(s)
                    return False


def boss_hunting(s):
    global last
    logger("🦸 Search for heroes to fight")
    name = last[s]['profile_name']
    click_skip()
    if name == '':
        name = str(s).capitalize()
    while True:
        if game_error(s):
            return

        if not check_screen(images["boss-hunt-btn"], timeout=1):
            return

        if c['enable_team_arrangement'] and c['tesseract_cmd'] != '':
            tr = last[s]['team_ready']
            if len(tr) <= 0:
                return

            teams = last[s]['teams']
            for tn in teams:
                for trn in tr:
                    if trn == tn:
                        heros_in_team = teams[tn]['heros']
                        if '10/10' == last[s]['current_map'] and not teams[tn][
                                'fight_map_10']:
                            logger('[{}] Skip fight on map 10/10'.format(name))
                            continue
                        choose_heroes_team_fight(heros_in_team, s)
                        if is_break_time():
                            return
                        while True:
                            cnt = 0
                            cf = positions(images["damage"],
                                           threshold=ct["green_bar"])
                            for d in cf:
                                x, y, w, h = d
                                e = positions_of_offset(
                                    images['energy-x'], x - 80, y - 90, 53, 30)
                                if len(e) > 0:
                                    cnt += 1
                            if cnt == len(heros_in_team):
                                if is_break_time():
                                    return
                                logger("⚒️  Team {} fighting with {} hero(s)".
                                       format(
                                           str(tn).upper(),
                                           len(heros_in_team)))
                                if not fight_boss(s):
                                    reset_fight(s)
                                    return
                            else:
                                reset_fight(s)
                                break
            reset_fight(s)
            break
        else:
            if not choose_heroes(s):
                break
            if is_break_time():
                return
            while True:
                cnt = 0
                cf = positions(images["damage"], threshold=ct["green_bar"])
                for d in cf:
                    x, y, w, h = d
                    imgage_of_offset(x - 80, y - 85, 40, 17,
                                     'e-{}.png'.format(0))
                    image = cv2.imread('e-{}.png'.format(0))
                    gray = get_grayscale(image)
                    # cv2.imwrite('e-gray-{}.png'.format(0), gray)
                    txt = pytesseract.image_to_string(gray,
                                                      lang='eng',
                                                      config='--psm 10')
                    txt = txt.replace('V', '1/', 1)
                    txt = re.sub('[^0-9/]', '', txt)
                    if not txt == '0/3':
                        cnt += 1
                if cnt == c['hero_per_fight'] or cnt == c[
                        'minimum_hero_per_fight']:
                    if is_break_time():
                        return

                    rcf = positions(images["damage"],
                                    threshold=ct["green_bar"])
                    if not (len(rcf) == c['hero_per_fight']) or not (
                            len(rcf) == c['minimum_hero_per_fight']):
                        logger(
                            '[{}] Heroes not equals hero per fight or minimum hero per fight.'
                            .format(name))
                        break
                    logger("⚒️  Fighting with {} hero(s)".format(cnt))
                    if not fight_boss(s):
                        reset_fight(s)
                        return
                else:
                    reset_fight(s)
                    break


def goto_boss_hunt(s):
    global last
    if click_btn(images["boss-hunt-back-2"], timeout=3):
        global login_attempts
        login_attempts = 0

    click_btn(images["boss-hunt"], timeout=3)
    time.sleep(1)
    click_skip()
    last[s]['current_map'] = get_current_map()
    last[s]['current_boss'] = get_current_boss()
    if check_screen(images['match-10'], timeout=3, threshold=0.8):
        last[s]['map_10'] = True
        cm = '10/10'
        if last[s]['current_map'] != '' and last[s]['current_map'] != 'x/10':
            cm = last[s]['current_map']
        logger('Fighting on map {}'.format(cm))
    else:
        last[s]['map_10'] = False
        logger('Fighting on map {}'.format(last[s]['current_map']))

    if not check_map():
        return False

    find_map = True
    scroll_attemps = 1
    found_not_complete_map = False
    while find_map:
        if click_btn(images["match"], timeout=10):
            find_map = False
            found_not_complete_map = True
        else:
            if scroll_attemps < c["scroll_map_attemps"]:
                scroll_maps()
                scroll_attemps += 1
            else:
                find_map = False

    if not found_not_complete_map:
        logger("No boss hunt map.")
        return False
    if check_screen(images["no-hero"]):
        logger("🦸 No heros, Please goto the shop to mint the heros")
        click_ok()
        return False

    return True


def goto_home():
    logger("🏠 Goto home!")
    click_btn(images["boss-hunt-back-2"])
    click_btn(images["boss-hunt-back-1"])


def login():
    global login_attempts
    logger("😿 Checking if game has disconnected")
    pyautogui.hotkey("ctrl", "f5")
    if check_screen(images["ok-2"], timeout=10):
        time.sleep(2)
        click_btn(images["ok-2"], timeout=0)
    if click_btn(images["login"], timeout=15):
        logger("🎉 Connect wallet button clicked, logging in!")

    if click_btn(images["sign"], timeout=10):
        logger("🎉 Sign button clicked, logging in!")

    if not check_screen(images["boss-hunt"], timeout=60):
        notify_working_screen(
            'Long time to login. Please goto your screen to login by yourself.',
            True)
    click_ok()


def boss_hunt(s):
    if is_break_time():
        return
    if not goto_boss_hunt(s):
        return
    if c["select_heroes_mode"] == "stamina":
        boss_hunting(s)
    else:
        logger("not implement")


def reset_fight(s):
    if game_error(s):
        return

    damage = positions(images["damage"], threshold=ct["green_bar"])
    logger("🦸 Hero in fight -> {}".format(len(damage)))
    if len(damage) > 0:
        # for f in damage:
        #     x, y, w, h = f
        #     move_to_with_randomness(x + 30, y - 100, 1)
        #     pyautogui.click()
        click_btn(images['remove-all'], timeout=5)


def click_ok():
    if check_screen(images['ok'], timeout=1):
        notify_working_screen('Game Error/Warning', True)
        click_btn(images['ok'], timeout=1)
        notify_working_screen('Game after click OK', True)


def notify_working_screen(message="Working on screen", force=False):
    with mss.mss() as sct:
        monitor_crop = {
            "top": 0,
            "left": 0,
            "width": c["window_width"],
            "height": c["window_height"],
        }
        x = sct.grab(monitor_crop)
        output = "screen.png"
        mss.tools.to_png(x.rgb, x.size, output=output)
        notify_screen("screen.png", message, force)


def notify_screen(image, message="Report current screen", force=False):
    try:
        if c["enable_line_notify"]:
            if (c['enable_notify_with_picture']) or force:
                logger(message)
                img = {"imageFile": open(image, "rb")}
                data = {"message": message}
                headers = {"Authorization": "Bearer " + c["line_token"]}
                session = requests.Session()
                session_post = session.post(c["line_api_url"],
                                            headers=headers,
                                            files=img,
                                            data=data)
                logger("➡ " + session_post.text)
            else:
                notify(message)
    except:
        logger("Notify error.")
        pass


def notify(message):
    try:
        logger(message)
        if c["enable_line_notify"]:
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "Authorization": "Bearer " + c["line_token"],
            }
            s = requests.post(c["line_api_url"],
                              headers=headers,
                              data={"message": message})
            logger("➡ " + s.text)
    except:
        logger("Notify error.")
        pass


def is_break_time():
    if c['enable_break_time']:
        today = datetime.today()
        for bt in c['breaks']:
            start = datetime.strptime(
                '{} {}'.format(today.strftime('%d/%m/%Y'), bt['start']),
                '%d/%m/%Y %H:%M:%S')
            end = datetime.strptime(
                '{} {}'.format(today.strftime('%d/%m/%Y'), bt['end']),
                '%d/%m/%Y %H:%M:%S')
            if datetime.timestamp(start) > datetime.timestamp(end):
                end = end + timedelta(days=1)
            if (datetime.timestamp(today) >= datetime.timestamp(start)) and (
                    datetime.timestamp(today) <= datetime.timestamp(end)):
                return True
    return False


def init():
    global last
    w_width = c["window_width"]
    w_height = c["window_height"]
    mw_width = c["window_min_width"]
    mw_height = c["window_min_height"]
    wins = pyautogui.getWindowsWithTitle("Luna Rush")
    index = 1
    last = {}
    if len(wins):
        for win in wins:
            if index == 0:
                win.width = w_width
                win.height = w_height
                win.topleft = (0, 0)
            else:
                win.width = mw_width
                win.height = mw_height
                win.topleft = (0, (w_height + 10))

            last[screen_text.format(index)] = {
                "instance": win,
                "index": index,
                "login": 0,
                "heroes": 0,
                "actions": time.time(),
                "refresh_browser": time.time(),
                "ready": False,
                "map_10": False,
                "team_ready": [],
                "teams": {},
                "current_map": '',
                "current_boss": '',
                "profile_name": '',
            }
            index += 1

    else:
        logger("No Luna Rush game windows")


def switch_to_work(screen):
    global last
    global active_screen
    w_width = c["window_width"]
    w_height = c["window_height"]
    mw_width = c["window_min_width"]
    mw_height = c["window_min_height"]
    for s in last:
        win = last[s]["instance"]
        win.width = mw_width
        win.height = mw_height
        win.topleft = (0, (w_height + 10))

    logger("🖥  Working on screen {} [{}]".format(screen["index"],
                                                 screen['profile_name']))
    screen["instance"].width = w_width
    screen["instance"].height = w_height
    screen["instance"].topleft = (0, 0)
    try:
        screen["instance"].activate()
    except:
        click_btn(images["luna-rush"], timeout=1)

    active_screen = screen_text.format(screen["index"])
    pyautogui.hotkey("ctrl", "1")


def imgage_of_offset(x, y, w, h, file_name="image-0.png"):
    with mss.mss() as sct:
        monitor_crop = {
            "top": y,
            "left": x,
            "width": w,
            "height": h,
        }
        xx = sct.grab(monitor_crop)
        mss.tools.to_png(xx.rgb, xx.size, output=file_name)
        sct_img = np.array(sct.grab(monitor_crop))

        # x = sct.grab(monitor_crop)
        # output = "sct-{top}x{left}_{width}x{height}.png".format(**monitor_crop)
        # mss.tools.to_png(x.rgb, x.size, output=output)

        return sct.grab(monitor_crop)


def check_team_to_fight(s):
    if not c['enable_team_arrangement']:
        return False
    if c['tesseract_cmd'] == '':
        return False

    global last
    name = last[s]['profile_name']
    if name == '':
        name = str(s).capitalize()
    pytesseract.pytesseract.tesseract_cmd = r'' + c['tesseract_cmd']
    from_home = False
    if check_screen(images['boss-hunt'], timeout=1):
        click_btn(images['heros'])
        from_home = True

    if check_screen(
            images['boss-hunt-back-1'],
            timeout=1) and not check_screen(images['warrior-2'], timeout=1):
        goto_home()
        click_btn(images['heros'])
        from_home = True

    if check_screen(
            images['boss-hunt-back-2'],
            timeout=1) and not check_screen(images['warrior-2'], timeout=1):
        goto_home()
        click_btn(images['heros'])
        from_home = True

    if check_screen(images['warrior-2'], timeout=1):
        if not from_home:
            click_btn(images['boss-hunt-back-2'], timeout=3, threshold=0.6)
            click_btn(images['heros'])

    # if len(last[s]['teams']) <= 0:
    #     logger('[{}] Initialize teams arrangement'.format(name))
    # conf_teams = c['teams']
    # if len(conf_teams) > 0:
    #     try:
    #         for st in conf_teams:
    #             cards = positions(images["warrior-2"],
    #                               threshold=ct["green_bar"])
    #             x, y, w, h = cards[0]
    #             imgage_of_offset(x + 34, y + 122, 45, 15,
    #                              'id-{}.png'.format(0))
    #             pytesseract.pytesseract.tesseract_cmd = r'' + c[
    #                 'tesseract_cmd']
    #             image = cv2.imread('id-{}.png'.format(0))
    #             gray = get_grayscale(image)
    #             txt = pytesseract.image_to_string(gray,
    #                                               lang='eng',
    #                                               config='--psm 10')
    #             logger(txt)
    #             hid = re.sub('[^0-9]', '', txt)
    #             for tn in st:
    #                 heroes = st[tn]['heros']
    #                 for hh in heroes:
    #                     if str(hh) == str(hid):
    #                         last[s]['teams'] = st
    #                         break
    #                 if len(last[s]['teams']) > 0:
    #                     break
    #         if os.path.exists('id-{}.png'.format(0)):
    #             os.remove('id-{}.png'.format(0))
    #     except:
    #         logger(
    #             '[{}] Initialize teams fail. Please check your configurations.'
    #             .format(name))
    #         logger('[{}] Switch to normal fight.'.format(name))
    #         return False
    # else:
    #     logger('[{}] Initialize teams fail. No teams in configurations.'.
    #            format(name))
    #     logger('[{}] Switch to normal fight.'.format(name))
    #     return False

    logger('[{}] Fighting with teams arrangement'.format(name))
    h_ready = []
    r = positions_of_offset(images["energy-x"],
                            80,
                            250,
                            460,
                            320,
                            threshold=ct["default"])
    if len(r) > 0:
        i = 1
        for (x, y, w, h) in r:
            imgage_of_offset((x + 80) - 83, (y + 250) - 112, 40, 15,
                             'id-{}.png'.format(i))
            image = cv2.imread('id-{}.png'.format(i))
            gray = get_grayscale(image)
            txt = pytesseract.image_to_string(gray,
                                              lang='eng',
                                              config='--psm 10')
            # logger(txt)
            if os.path.exists('id-{}.png'.format(i)):
                os.remove('id-{}.png'.format(i))
            h_ready.append(re.sub('[^0-9]', '', txt))
            i += 1

    commoms = positions(images["card"], threshold=ct["default"])
    if len(commoms) == 0:
        return
    x, y, w, h = commoms[len(commoms) - 1]
    move_to_with_randomness(x, y, 1)
    pyautogui.dragRel(0, -300, duration=1, button="left")
    time.sleep(3)

    # r = positions(images["energy-x"], threshold=ct["default"])
    r = positions_of_offset(images["energy-x"],
                            80,
                            320,
                            460,
                            320,
                            threshold=ct["default"])
    if len(r) > 0:
        i = 1
        for (x, y, w, h) in r:
            # imgage_of_offset(x - 30, y - 115, 45, 15, 'id-{}.png'.format(i))
            imgage_of_offset((x + 80) - 83, (y + 320) - 112, 40, 15,
                             'id-{}.png'.format(i))
            image = cv2.imread('id-{}.png'.format(i))
            gray = get_grayscale(image)
            txt = pytesseract.image_to_string(gray,
                                              lang='eng',
                                              config='--psm 10')
            # logger(txt)
            if os.path.exists('id-{}.png'.format(i)):
                os.remove('id-{}.png'.format(i))
            h_ready.append(re.sub('[^0-9]', '', txt))
            i += 1
    # logger(h_ready)
    teams = last[s]['teams']
    team_ready = []
    for tn in teams:
        heros_in_team = teams[tn]['heros']
        cnt = 0
        cnt_hero_in_teams = len(heros_in_team)
        for h in heros_in_team:
            for hr in h_ready:
                if str(h) == str(hr):
                    cnt += 1

        if cnt == cnt_hero_in_teams:
            team_ready.append(tn)
            logger('Team {} ready to fight'.format(tn))
        else:
            logger('Team {} not ready to fight'.format(tn))

    if len(team_ready) > 0:
        last[s]['ready'] = True
        last[s]['team_ready'] = team_ready

    goto_home()

    return True


def get_current_boss():
    try:
        if c['tesseract_cmd'] != '':
            pytesseract.pytesseract.tesseract_cmd = r'' + c['tesseract_cmd']
            fm = positions(images["match"], threshold=ct["default"])
            x, y, w, h = fm[0]
            imgage_of_offset(x - 15, y - 115, 45, 15, 'boss-{}.png'.format(0))
            image = cv2.imread('boss-{}.png'.format(0))
            gray = get_grayscale(image)
            txt = pytesseract.image_to_string(gray,
                                              lang='eng',
                                              config='--psm 10')
            txt = txt.replace('O', '0')
            txt = txt.replace('i', '1')
            if os.path.exists('boss-{}.png'.format(0)):
                os.remove('boss-{}.png'.format(0))
                b = re.sub('[^0-9]', '', txt)
                if b == '':
                    b = 'Boss1'
                else:
                    b = 'Boss{}'.format(str(b))
                return b
    except:
        logger('Get current boss fail')
    return ''


def get_current_map():
    try:
        if c['tesseract_cmd'] != '':
            pytesseract.pytesseract.tesseract_cmd = r'' + c['tesseract_cmd']
            fm = positions(images["match"], threshold=ct["default"])
            if len(fm) > 0:
                x, y, w, h = fm[0]
                imgage_of_offset(x - 30, y - 2, 70, 26, 'map-{}.png'.format(0))
                image = cv2.imread('map-{}.png'.format(0))
                gray = get_grayscale(image)
                txt = pytesseract.image_to_string(gray,
                                                  lang='eng',
                                                  config='--psm 10')
                # logger(txt)
                txt = txt.replace('FIO', '7/10')
                # logger(txt)
                if os.path.exists('map-{}.png'.format(0)):
                    os.remove('map-{}.png'.format(0))
                return re.sub('[^0-9\/]', '', txt)
    except:
        logger('Get current boss fail')
    return 'x/10'


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_noise(image):
    return cv2.medianBlur(image, 5)


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def dilate(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


def erode(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


def opening(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


def canny(image):
    return cv2.Canny(image, 100, 200)


def get_bonus():
    try:
        if c['tesseract_cmd'] != '':
            pytesseract.pytesseract.tesseract_cmd = r'' + c['tesseract_cmd']
            fm = positions(images["ml-b"], threshold=ct["default"])
            if len(fm) > 0:
                x, y, w, h = fm[0]
                imgage_of_offset(x - 125, y - 20, 127, 80,
                                 'ml-{}.png'.format(0))

                image = cv2.imread('ml-{}.png'.format(0))
                gray = get_grayscale(image)
                thresh = thresholding(gray)
                txt = pytesseract.image_to_string(thresh,
                                                  lang='eng',
                                                  config='--psm 10')
                b = re.sub('[^0-9.]', '', txt)
                if b == '' or float(b) > 2:
                    today = datetime.today()
                    os.rename(
                        'ml-{}.png'.format(0), 'ml-{}.png'.format(
                            today.strftime('%Y-%m-%d-%H-%M-%S')))

                if b == '':
                    b = 0.0
                b = float(b)
                if os.path.exists('ml-{}.png'.format(0)):
                    os.remove('ml-{}.png'.format(0))
                return b
    except:
        logger('Get current boss fail')
    return 0.0


def get_profile_name():
    try:
        if c['tesseract_cmd'] != '':
            pytesseract.pytesseract.tesseract_cmd = r'' + c['tesseract_cmd']
            if not check_screen(images['user-icon']):
                goto_home()
            click_btn(images['user-icon'], 0.9)
            if check_screen(images['edit-btn']):
                fm = positions(images["edit-btn"], threshold=ct["default"])
                if len(fm) > 0:
                    x, y, w, h = fm[0]
                    imgage_of_offset(x - 410, y, 350, 32,
                                     'pn-{}.png'.format(0))
                    image = cv2.imread('pn-{}.png'.format(0))
                    gray = get_grayscale(image)
                    thresh = thresholding(gray)
                    txt = pytesseract.image_to_string(thresh,
                                                      lang='eng',
                                                      config='--psm 10')
                    if os.path.exists('pn-{}.png'.format(0)):
                        os.remove('pn-{}.png'.format(0))
                    return re.sub('[^a-zA-Z0-9]', '', txt)
    except:
        logger('Get profile name fail')
    return ''


def get_wallet_id():
    try:
        if c['tesseract_cmd'] != '':
            pytesseract.pytesseract.tesseract_cmd = r'' + c['tesseract_cmd']
            fm = positions(images["edit-btn"], threshold=ct["default"])
            if len(fm) > 0:
                x, y, w, h = fm[0]
                imgage_of_offset(x - 410, y + 32, 350, 20,
                                 'n-{}.png'.format(0))
                image = cv2.imread('n-{}.png'.format(0))
                gray = get_grayscale(image)
                thresh = thresholding(gray)
                txt = pytesseract.image_to_string(thresh,
                                                  lang='eng',
                                                  config='--psm 10')
                logger(re.sub('[^a-z0-9]', '', txt))
                logger(txt)
                if os.path.exists('n-{}.png'.format(0)):
                    os.remove('n-{}.png'.format(0))
                return re.sub('[^a-zA-Z0-9]', '', txt)
    except:
        logger('Get wallet id fail')
    return ''


def is_server_maintenance():
    global server_is_maintenance
    global last_check_server_maintenance
    now = time.time()
    t = c["time_intervals"]
    if not server_is_maintenance:
        if check_screen(images['server-maintenance'], 3):
            pyautogui.hotkey("ctrl", "f5")
            if check_screen(images['server-maintenance'], 15):
                server_is_maintenance = True
                last_check_server_maintenance = now
                msg = '🥸  Server maintenance. Next check server online in {} minutes'.format(
                    str(t["check_server_online"]))
                notify_working_screen(msg, True)
                sys.stdout.flush()
                time.sleep(1)
                return True
            else:
                server_is_maintenance = False
        else:
            server_is_maintenance = False
    else:
        if now - last_check_server_maintenance > add_randomness(
                t["check_server_online"] * 60):
            pyautogui.hotkey("ctrl", "f5")
            if check_screen(images['server-maintenance'], 15):
                server_is_maintenance = True
                last_check_server_maintenance = now
                msg = '🥸  Server still maintenance. Next check server online in {} minutes'.format(
                    str(t["check_server_online"]))
                notify_working_screen(msg, True)
                sys.stdout.flush()
                time.sleep(1)
                return True
            else:
                server_is_maintenance = False
        else:
            logger(None, progress_indicator=True)
            sys.stdout.flush()
            time.sleep(1)
            return True

    return False


def set_profile(s):
    global last
    if last[s]['profile_name'] == '':
        last[s]['profile_name'] = get_profile_name()
        logger('Hi! {}'.format(last[s]['profile_name']))
        if c['enable_team_arrangement']:
            last[s]['teams'] = c['teams'][last[s]['profile_name']]
        goto_home()


def startupCheck(file_name):
    if os.path.isfile(os.path.join(REPORT_PATH, file_name)) and os.access(
            os.path.join(REPORT_PATH, file_name), os.R_OK):
        pass
    else:
        with io.open(os.path.join(REPORT_PATH, file_name), 'w') as db_file:
            db_file.write(json.dumps({}))


def write_report(profile_name, mlus):
    if not c['enable_write_report']:
        return
    today = datetime.today()
    file_name = 'report-{}.json'.format(today.strftime('%Y-%b'))
    startupCheck(file_name)
    date = today.strftime('%Y-%m-%d')
    time = today.strftime('%H:%M:%S')
    with open(REPORT_PATH + file_name, 'r') as report_file:
        json_object = json.load(report_file)
        if profile_name in json_object:
            old = json_object[profile_name]
            if date in old:
                old[date]['mlus'].append(mlus)
                old[date]['time'].append(time)
            else:
                old[date] = {
                    'mlus': [mlus],
                    'time': [time],
                }
            json_object[profile_name] = old
        else:
            json_object[profile_name] = {
                today.strftime('%Y-%m-%d'): {
                    'mlus': [mlus],
                    'time': [time],
                }
            }
        with open(REPORT_PATH + file_name, 'w') as output:
            json.dump(json_object, output)


def main():
    # ==Setup==
    global login_attempts
    global last_log_is_progress
    global last
    global active_screen
    login_attempts = 0
    last_log_is_progress = False

    global images
    images = load_images()
    active_screen = ""

    print(cat)
    t = c["time_intervals"]

    init()
    last_action = time.time()
    action_notify_msg = "No action long time on {}"
    if len(last) > 0:
        switch_to_work(last['screen1'])

    # choose_heroes('screen1')
    # return
    global server_is_maintenance
    global last_check_server_maintenance
    server_is_maintenance = False
    last_check_server_maintenance = 0
    while True:
        now = time.time()
        if c["refresh_browser"] > 0:
            logger("refresh browser")
            
        click_btn(images["ok-2"], timeout=0)

        if server_is_maintenance and now - last_check_server_maintenance < add_randomness(
                t["check_server_online"] * 60):
            logger(None, progress_indicator=True)
            sys.stdout.flush()
            time.sleep(1)
            continue

        if is_break_time():
            logger(None, progress_indicator=True)
            sys.stdout.flush()
            time.sleep(1)
            continue

        for s in last:
            click_btn(images["ok-2"], timeout=0)
            if server_is_maintenance and now - last_check_server_maintenance < add_randomness(
                    t["check_server_online"] * 60):
                logger(None, progress_indicator=True)
                sys.stdout.flush()
                time.sleep(1)
                continue

            click_ok()
            if game_error(s):
                continue

            if is_break_time():
                logger(None, progress_indicator=True)
                sys.stdout.flush()
                time.sleep(1)
                continue

            if now - last[s]["login"] > add_randomness(
                    t["check_for_login"] * 60):
                if not (screen_text.format(last[s]["index"])) == active_screen:
                    switch_to_work(last[s])
                else:
                    try:
                        last[s]["instance"].activate()
                    except:
                        click_btn(images["luna-rush"], timeout=1)

                pyautogui.hotkey("ctrl", "1")
                if is_server_maintenance():
                    pyautogui.hotkey("ctrl", "2")
                    continue
                if check_screen(images["login"], timeout=1):
                    click_ok()
                    login()

                pyautogui.hotkey("ctrl", "2")
                last[s]["login"] = now

            if (now - last[s]["heroes"]) > add_randomness(
                    t["send_heros_for_fight"] * 60) or last[s]["ready"]:
                if not (screen_text.format(last[s]["index"])) == active_screen:
                    switch_to_work(last[s])
                else:
                    try:
                        last[s]["instance"].activate()
                    except:
                        click_btn(images["luna-rush"], timeout=1)

                pyautogui.hotkey("ctrl", "1")
                if is_server_maintenance():
                    pyautogui.hotkey("ctrl", "2")
                    continue
                click_ok()
                set_profile(s)
                if not last[s]["ready"]:
                    if not check_team_to_fight(s):
                        check_hero_ready(s)
                if last[s]['ready']:
                    boss_hunt(s)
                    last[s]["ready"] = False
                    last[s]['team_ready'] = []
                    goto_home()

                pyautogui.hotkey("ctrl", "2")
                last[s]["heroes"] = now
                last[s]["actions"] = now
                last_action = now
            elif now - last[s]["actions"] > add_randomness(
                    t["boss_hunt_action"] * 60):
                if not (screen_text.format(last[s]["index"])) == active_screen:
                    switch_to_work(last[s])
                else:
                    try:
                        last[s]["instance"].activate()
                    except:
                        click_btn(images["luna-rush"], timeout=1)

                pyautogui.hotkey("ctrl", "1")
                if is_server_maintenance():
                    pyautogui.hotkey("ctrl", "2")
                    continue
                click_ok()
                set_profile(s)
                if not check_team_to_fight(s):
                    check_hero_ready(s)
                pyautogui.hotkey("ctrl", "2")
                last[s]["actions"] = now
                last_action = now
            else:
                if c["waiting_fight_move_mouse"]:
                    move_to_with_randomness(add_randomness(500),
                                            add_randomness(500), 3)

            if now - last_action > add_randomness(t["report_no_action"] * 60):
                notify(action_notify_msg.format(s))
                logger(action_notify_msg.format(s))
                last_action = now

            logger(None, progress_indicator=True)

            sys.stdout.flush()

            time.sleep(1)

        if not server_is_maintenance and now - last_action > add_randomness(
                t["report_no_action"] * 60):
            notify(action_notify_msg.format(s))
            logger(action_notify_msg.format(s))
            last_action = now


if __name__ == "__main__":

    main()
