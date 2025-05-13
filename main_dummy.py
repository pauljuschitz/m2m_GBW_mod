# grinder_ui/main.py
from machine import Pin
import time
import ujson as json
import os

# File path for persistent config
CONFIG_FILE = "config.json"

# Default settings
default_config = {
    "single_dose": 8.5,
    "double_dose": 17.0
}

# Load or create config
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        save_config(default_config)
        return default_config


def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f)

# Display mock (replace with real screen code)
def display_config(cfg):
    print("Single Dose: {:.1f}g".format(cfg['single_dose']))
    print("Double Dose: {:.1f}g".format(cfg['double_dose']))

# Init buttons (use correct GPIOs for your Core Gray)
btn_single = Pin(39, Pin.IN)  # Button A
btn_double = Pin(38, Pin.IN)  # Button B
btn_menu = Pin(37, Pin.IN)    # Button C

cfg = load_config()
menu_mode = False
selection = "single_dose"

def handle_buttons():
    global menu_mode, cfg, selection

    if not btn_menu.value():  # Button C pressed
        menu_mode = not menu_mode
        print("Menu mode:", menu_mode)
        time.sleep(0.3)

    if menu_mode:
        if not btn_single.value():
            cfg[selection] = round(cfg[selection] + 0.1, 1)
            save_config(cfg)
            display_config(cfg)
            time.sleep(0.2)
        if not btn_double.value():
            cfg[selection] = round(cfg[selection] - 0.1, 1)
            save_config(cfg)
            display_config(cfg)
            time.sleep(0.2)
    else:
        if not btn_single.value():
            print("Start single shot: {:.1f}g".format(cfg["single_dose"]))
            time.sleep(0.2)
        if not btn_double.value():
            print("Start double shot: {:.1f}g".format(cfg["double_dose"]))
            time.sleep(0.2)

print("Grinder Controller Ready")
display_config(cfg)

while True:
    handle_buttons()
    time.sleep(1)