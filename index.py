# -*- coding: utf-8 -*-
import sys
import time
from os import listdir
from random import randint, random

import mss
import numpy as np
import pyautogui
import requests
import yaml
from cv2 import cv2

from src.logger import logger

stream = open("config.yaml", "r")
c = yaml.safe_load(stream)
ct = c["threshold"]
pause = c["time_intervals"]["interval_between_movements"]
pyautogui.PAUSE = pause
screen_text = "screen{}"

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
    pyautogui.moveTo(add_randomness(x, 10), add_randomness(y, 10),
                     t + random() / 2)


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


def print_card(x, y):
    with mss.mss() as sct:
        monitor_crop = {
            "top": y - 110,
            "left": x - 30,
            "width": 90,
            "height": 120,
        }
        # xx = sct.grab(monitor_crop)
        # output = "sct-{top}x{left}_{width}x{height}.png".format(**monitor_crop)
        # mss.tools.to_png(xx.rgb, xx.size, output=output)
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
        img = print_card(x, y)
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


def check_hero_ready(s):
    global last
    pyautogui.hotkey("ctrl", "1")
    if check_screen(images['boss-hunt'], timeout=1):
        click_btn(images['heros'])

    if check_screen(images['boss-hunt-back-1'], timeout=1) and not check_screen(images['warrior-2'], timeout=1):
        goto_home()
        click_btn(images['heros'])

    if check_screen(images['boss-hunt-back-2'], timeout=1) and not check_screen(images['warrior-2'], timeout=1):
        goto_home()
        click_btn(images['heros'])

    if check_screen(images['warrior-2'], timeout=1):
        click_btn(images['boss-hunt-back-2'], timeout=3, threshold=0.6)
        click_btn(images['heros'])
        r = positions(images["energy"], threshold=ct["default"])
        if len(r) > 0:
            last[s]['ready'] = True
            logger('🦸 {} hero(s) ready to fight'.format(len(r)))
            return
        else:
            logger('🦸 Heros is not ready')

        commoms = positions(images["card"], threshold=ct["default"])
        if len(commoms) == 0:
            return
        x, y, w, h = commoms[len(commoms) - 1]
        move_to_with_randomness(x, y, 1)
        pyautogui.dragRel(0,
                          -c["click_and_drag_amount"],
                          duration=1,
                          button="left")
        r = positions(images["energy"], threshold=ct["default"])
        if len(r) > 0:
            last[s]['ready'] = True
            logger('🦸 {} hero(s) ready to fight'.format(len(r)))
        else:
            logger('🦸 Heros is not ready')

        commoms = positions(images["card"], threshold=ct["default"])
        if len(commoms) == 0:
            return
        x, y, w, h = commoms[0]
        move_to_with_randomness(x, y, 1)
        pyautogui.dragRel(0,
                          c["click_and_drag_amount"],
                          duration=1,
                          button="left")
        time.sleep(1)


def scroll_heros():
    commoms = positions(images["card"], threshold=ct["green_bar"])

    if len(commoms) == 0:
        return
    x, y, w, h = commoms[len(commoms) - 1]
    move_to_with_randomness(x, y, 1)

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


def get_hero_with_energy():
    stamina_bars = positions(images["energy"], threshold=ct["common"])
    logger("🦸 Hero have a energy -> {}".format(len(stamina_bars)))
    hero_with_energy = []
    for eng in stamina_bars:
        hero_with_energy.append(eng)

    return hero_with_energy


def check_map():
    m = positions(images["match-complete"], threshold=ct["default"])
    if c["stop_when_completed_map"] > 0 and len(
            m) == c["stop_when_completed_map"]:
        return False

    return True


def fight_boss(s):
    global last
    click_btn(images["boss-hunt-btn"])
    if click_btn(images['x']):
        reset_fight()
        return True

    if check_screen(images["vs"], timeout=15):
        pyautogui.click()

    fighting = True
    now = time.time()
    start_time = int(round(now * 1000))
    while fighting:
        if game_error():
            return True
        if click_btn(images['x'], timeout=1):
            reset_fight()
            return True
        logger(None, progress_indicator=True)
        if click_btn(images["tap-open"]):
            time.sleep(3)
            logger("👉 Yeah!!! you win")
            notify_working_screen("👉 Yeah!!! you win")
            # click_btn(images["tap-open"])
            pyautogui.click()
            fighting = False
        elif check_screen(images["defeat"]):
            time.sleep(3)
            logger("👇 Oops!!! you lose")
            notify_working_screen("👇 Oops!!! you lose")
            pyautogui.click()
            fighting = False

        n = int(round(now * 1000))
        if (n - start_time > (n + (10 * (60 * 1000))) - n):
            notify('Boss hunt time over 10 minutes')
            pyautogui.hotkey("ctrl", "f5")
            return False

    chk = True
    while chk:
        if game_error():
            return True
        if check_screen(images["match"], timeout=1):
            logger("👉 Yeah!! pass the map")
            chk = False
            if check_screen(images['match-10'], timeout=3, threshold=0.8):
                last[s]['map_10'] = True
                logger('Fighting on map 10/10')
            else:
                last[s]['map_10'] = False
                logger('Fighting on map x/10')
                
            if not check_map():
                return False
            else:
                click_btn(images["match"], timeout=1)

        if check_screen(images["boss-hunt-btn"], timeout=1):
            chk = False

    reset_fight()
    return True


def game_error():
    if check_screen(images['bg'], timeout=1):
        logger("Game error")
        notify_working_screen("The Luna Rush has an error occured")
        pyautogui.hotkey("ctrl", "f5")
        return True

    return False


def boss_hunting(s):
    global last
    reset_fight()
    logger("🦸 Search for heroes to fight")
    hunting = True
    offset = 5
    scroll_attemps = 0
    nc = 0
    while hunting:
        if game_error():
            return

        if not check_screen(images["boss-hunt-btn"], timeout=1):
            return

        plus = positions(images["plus"], threshold=ct["green_bar"])
        if len(plus) > 0:
            heros = get_hero_with_energy()
            if (len(heros) - nc) > 0:
                for (x, y, w, h) in heros:
                    if game_error():
                        return

                    if c['enable_hero_low_rarity_map_10_only']:
                        if last[s]['map_10']:
                            if check_on_print(images['card'], x,
                                              y) or check_on_print(
                                                  images['rare'], x, y):
                                move_to_with_randomness(
                                    x + offset + (w / 2), y + (h / 2), 1)
                                pyautogui.click()
                            else:
                                nc += 1
                                logger(
                                    '🦸 [{}] Hero is not low rarity skip fight on map 10/10'.format(s)
                                )

                        else:
                            move_to_with_randomness(x + offset + (w / 2),
                                                    y + (h / 2), 1)
                            pyautogui.click()

                    else:
                        move_to_with_randomness(x + offset + (w / 2),
                                                y + (h / 2), 1)
                        pyautogui.click()

                    hero_in_fight = positions(images["plus"],
                                              threshold=ct["green_bar"])
                    if len(hero_in_fight) < 1:
                        logger("⚒️ Fighting with {} hero(s)".format(
                            3 - len(hero_in_fight)))
                        if not fight_boss(s):
                            reset_fight()
                            return
                        nc = 0
                        scroll_attemps = 0
                        break
            else:
                if scroll_attemps < c["scroll_attemps"]:
                    scroll_heros()
                    scroll_attemps += 1
                    nc = 0
                else:
                    hero_in_fight = positions(images["plus"],
                                              threshold=ct["green_bar"])
                    if len(hero_in_fight) <= (3 - c["hero_per_fight"]):
                        logger("⚒️ Fighting with {} hero(s)".format(
                            3 - len(hero_in_fight)))
                        if not fight_boss(s):
                            reset_fight()
                            return
                        nc = 0
                        scroll_attemps = 0
                    else:
                        hunting = False
                        reset_fight()
        else:
            reset_fight()


def goto_boss_hunt(s):
    global last
    if click_btn(images["boss-hunt-back-2"]):
        global login_attempts
        login_attempts = 0

    click_btn(images["boss-hunt"], timeout=10)
    time.sleep(1)
    if check_screen(images['match-10'], timeout=3, threshold=0.8):
        last[s]['map_10'] = True
        logger('Fighting on map 10/10')
    else:
        last[s]['map_10'] = False
        logger('Fighting on map x/10')

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
        click_btn(images["ok"])
        return False

    return True


def goto_home():
    logger("🏠 Goto home!")
    click_btn(images["boss-hunt-back-2"])
    click_btn(images["boss-hunt-back-1"])


def login():
    global login_attempts
    logger("😿 Checking if game has disconnected")

    if click_btn(images["login"], timeout=1):
        logger("🎉 Connect wallet button clicked, logging in!")

    if click_btn(images["sign"], timeout=10):
        logger("🎉 Sign button clicked, logging in!")
    if check_screen(images["boss-hunt"], timeout=15):
        pass


def boss_hunt(s):
    if not goto_boss_hunt(s):
        return
    if c["select_heroes_mode"] == "stamina":
        boss_hunting(s)
    else:
        logger("not implement")


def reset_fight():
    if game_error():
        return
    plus = positions(images["plus"], threshold=ct["green_bar"])
    logger("🦸 Hero in fight -> {}".format(3 - len(plus)))
    if len(plus) >= 3:
        return

    if check_screen(images["warrior"]):
        offset = 310
        matches = positions(images["warrior"])
        x, y, w, h = matches[0]
        move_to_with_randomness(x + offset, y + 85, 0)
        pyautogui.click()
        offset = 560
        move_to_with_randomness(x + offset, y + 85, 0)
        pyautogui.click()
        offset = 800
        move_to_with_randomness(x + offset, y + 85, 0)
        pyautogui.click()


def notify_working_screen(message="Working on screen"):
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
        notify_screen("screen.png", message)


def notify_screen(image, message="Report current screen"):
    try:
        if c["enable_line_notify"]:
            img = {"imageFile": open(image, "rb")}
            data = {"message": message}
            headers = {"Authorization": "Bearer " + c["line_token"]}
            session = requests.Session()
            session_post = session.post(c["line_api_url"],
                                        headers=headers,
                                        files=img,
                                        data=data)
            logger("➡ " + session_post.text)
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

    logger("🖥 Working on screen {}".format(screen["index"]))
    screen["instance"].width = w_width
    screen["instance"].height = w_height
    screen["instance"].topleft = (0, 0)
    try:
        screen["instance"].activate()
    except:
        click_btn(images["luna-rush"], timeout=1)

    active_screen = screen_text.format(screen["index"])
    pyautogui.hotkey("ctrl", "1")


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
    # time.sleep(5)
    t = c["time_intervals"]

    init()
    last_action = time.time()
    action_notify_msg = "No action long time on {}"
    # switch_to_work(last[screen_text.format(1)])
    # check_hero_ready(last[screen_text.format(1)])
    # return
    while True:
        now = time.time()
        if c["refresh_browser"] > 0:
            logger("refresh browser")

        for s in last:
            game_error()
            if check_screen(images["login"], timeout=1):
                if not (screen_text.format(last[s]["index"])) == active_screen:
                    switch_to_work(last[s])
                else:
                    try:
                        last[s]["instance"].activate()
                    except:
                        click_btn(images["luna-rush"], timeout=1)
                click_btn(images["ok"])
                login()

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
                # notify_working_screen()
                click_btn(images["ok"], timeout=1)
                if not last[s]["ready"]:
                    check_hero_ready(s)
                if last[s]['ready']:
                    goto_home()
                    if (check_screen(images["boss-hunt"])
                            or check_screen(images["boss-hunt-btn"])
                            or check_screen(images["match"])):
                        boss_hunt(s)
                        last[s]["ready"] = False
                        goto_home()
                        click_btn(images['heros'])
                        # if check_screen(images['boss-hunt']):

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
                click_btn(images["ok"], timeout=1)
                # goto_home()
                # goto_boss_hunt()
                # r = positions(images["energy"], threshold=ct["common"])
                # if len(r) > 0:
                #     last[s]["ready"] = True
                # goto_home()
                # click_btn(images['heros'])
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

        if now - last_action > add_randomness(t["report_no_action"] * 60):
            notify(action_notify_msg.format(s))
            logger(action_notify_msg.format(s))
            last_action = now


if __name__ == "__main__":

    main()
