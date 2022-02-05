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
    pyautogui.moveTo(add_randomness(x, 10), add_randomness(y, 10), t + random() / 2)


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[: -len(suffix)]
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


def print_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
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


def scroll():
    commoms = positions(images["card"], threshold=ct["green_bar"])

    if len(commoms) == 0:
        return
    x, y, w, h = commoms[len(commoms) - 1]
    move_to_with_randomness(x, y + 50, 1)

    if not c["use_click_and_drag_instead_of_scroll"]:
        pyautogui.scroll(-c["scroll_size"])
    else:
        pyautogui.dragRel(0, -c["click_and_drag_amount"], duration=1, button="left")


def get_hero_with_energy():
    stamina_bars = positions(images["energy"], threshold=ct["common"])
    logger("🦸 Hero have a energy -> {}".format(len(stamina_bars)))
    hero_with_energy = []
    for eng in stamina_bars:
        hero_with_energy.append(eng)

    return hero_with_energy


def fight_boss():
    click_btn(images["boss-hunt-btn"])
    click_btn(images["vs"], timeout=15)
    fighting = True
    while fighting:
        logger(None, progress_indicator=True)
        if click_btn(images["tap-open"]):
            logger("👉 Yeah!!! We are the winner")
            click_btn(images["victory"])
            fighting = False
        elif click_btn(images["defeat"]):
            logger("👇 Oops!!! i'm lose")
            fighting = False

    chk = True
    while chk:
        if click_btn(images["match"], timeout=1):
            logger("👉 Yeah!! pass the map")
            chk = False
        if check_screen(images["boss-hunt-btn"], timeout=1):
            chk = False

    reset_fight()


def boss_hunting():
    reset_fight()
    logger("🦸 Search for heroes to fight")
    hunting = True
    offset = 5
    scroll_attemps = 0
    while hunting:
        plus = positions(images["plus"], threshold=ct["green_bar"])
        if len(plus) > 0:
            heros = get_hero_with_energy()
            if len(heros) > 0:
                for (x, y, w, h) in heros:
                    move_to_with_randomness(x + offset + (w / 2), y + (h / 2), 1)
                    pyautogui.click()
                    hero_in_fight = positions(images["plus"], threshold=ct["green_bar"])
                    if len(hero_in_fight) < 1:
                        logger(
                            "⚒️ Fighting with {} hero(s)".format(3 - len(hero_in_fight))
                        )
                        fight_boss()
                        scroll_attemps = 0
                        break
            else:
                if scroll_attemps < c["scroll_attemps"]:
                    scroll()
                    scroll_attemps += 1
                else:
                    hero_in_fight = positions(images["plus"], threshold=ct["green_bar"])
                    if len(hero_in_fight) < 3:
                        logger(
                            "⚒️ Fighting with {} hero(s)".format(3 - len(hero_in_fight))
                        )
                        fight_boss()
                        scroll_attemps = 0
                    else:
                        hunting = False
        else:
            reset_fight()


def goto_boss_hunt():
    if click_btn(images["boss-hunt-back-2"]):
        global login_attempts
        login_attempts = 0

    click_btn(images["boss-hunt"], timeout=10)
    click_btn(images["match"], timeout=10)


def goto_home():
    logger("🏠 Goto home!")
    click_btn(images["boss-hunt-back-2"])
    click_btn(images["boss-hunt-back-1"])


def login():
    global login_attempts
    global last
    logger("😿 Checking if game has disconnected")

    if login_attempts > 3:
        logger("🔃 Too many login attempts, refreshing")
        login_attempts = 0
        pyautogui.hotkey("ctrl", "f5")
        return
    if click_btn(images["login"], timeout=1):
        logger("🎉 Connect wallet button clicked, logging in!")
        login_attempts = login_attempts + 1

    if click_btn(images["sign"], timeout=10):
        login_attempts = login_attempts + 1
        logger("🎉 Sign button clicked, logging in!")
    if check_screen(images["boss-hunt"], timeout=15):
        pass


def boss_hunt():
    goto_boss_hunt()
    if c["select_heroes_mode"] == "stamina":
        boss_hunting()
    else:
        logger("not implement")


def reset_fight():
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


def notify_screen(image, message="Report current screen"):
    if c["enable_line_notify"]:
        img = {"imageFile": open(image, "rb")}
        data = {"message": message}
        headers = {"Authorization": "Bearer " + c["line_token"]}
        session = requests.Session()
        session_post = session.post(
            c["line_api_url"], headers=headers, files=img, data=data
        )
        logger("➡ " + session_post.text)


def notify(message):
    if c["enable_line_notify"]:
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer " + c["line_token"],
        }
        s = requests.post(c["line_api_url"], headers=headers, data={"message": message})
        logger("➡ " + s.text)


def main():
    # ==Setup==
    global login_attempts
    global last_log_is_progress
    global last
    login_attempts = 0
    last_log_is_progress = False

    global images
    images = load_images()

    print(cat)
    time.sleep(5)
    t = c["time_intervals"]

    last = {"login": 0, "heroes": 0, "actions": time.time()}
    click_btn(images["luna-rush"])
    while True:
        now = time.time()
        if check_screen(images["login"]):
            login()

        if now - last["heroes"] > add_randomness(t["send_heros_for_fight"] * 60):
            pyautogui.hotkey("ctrl", "1")
            if (
                check_screen(images["boss-hunt"])
                or check_screen(images["boss-hunt-btn"])
                or check_screen(images["match"])
            ):
                boss_hunt()
                goto_home()
                pyautogui.hotkey("ctrl", "2")
                last["heroes"] = now
        elif now - last["actions"] > add_randomness(t["boss_hunt_action"] * 60):
            pyautogui.hotkey("ctrl", "1")
            goto_boss_hunt()
            goto_home()
            pyautogui.hotkey("ctrl", "2")
            last["actions"] = now
        else:
            if c["waiting_fight_move_mouse"]:
                move_to_with_randomness(add_randomness(500), add_randomness(500), 3)

        logger(None, progress_indicator=True)

        sys.stdout.flush()

        time.sleep(1)


if __name__ == "__main__":

    main()