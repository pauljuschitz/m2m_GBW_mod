import os, sys, io
import M5
from M5 import *
from hardware import I2C
from hardware import Pin
from machine import Pin
from unit import WeightI2CUnit
from unit import RelayUnit
import time
import math

# UI elements
title0 = None
grind_label = None
single_label = None
double_label = None
grid_rects = []

# State variables
t = 0
weight = 0.0
mode = "grind"  # can be "grind", "set_single", or "set_double"
single_dose = 9.0  # grams
double_dose = 18.0  # grams
grinding_active = False
grind_target = 0.0
blink = True  # for blinking rectangle
c_hold_triggered = False
relay_0 = None
tare_offset = 0.0
calib = 0.0474


SETTINGS_FILE = "/flash/dose_settings.txt"

def save_doses():
  with open(SETTINGS_FILE, "w") as f:
    f.write("{:.1f},{:.1f}".format(single_dose, double_dose))
  print("Saved doses: {:.1f}, {:.1f}".format(single_dose, double_dose))

def load_doses():
  global single_dose, double_dose
  try:
    with open(SETTINGS_FILE, "r") as f:
      data = f.read().strip().split(",")
      single_dose = float(data[0])
      double_dose = float(data[1])
    print("Loaded doses: {:.1f}, {:.1f}".format(single_dose, double_dose))
  except Exception as e:
    print("No saved doses or load error:", e)

def setup():
  global title0, grind_label, single_label, double_label, grid_rects, i2c0, weight_i2c_0, relay_0, relay_pin, tare_offset, weight
  
  i2c0 = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
  weight_i2c_0 = WeightI2CUnit(i2c0, 0x26)
  relay_pin = Pin(26, Pin.OUT)

  M5.begin()
  Widgets.fillScreen(0x000000)

  load_doses()

  single_label = Widgets.Label("{:.1f}".format(single_dose), 41, 28, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu56)
  single_label.setVisible(True)
  double_label = Widgets.Label("{:.1f}".format(double_dose), 175, 28, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu56)
  double_label.setVisible(True)
  grind_label = Widgets.Label("0.0", 41, 148, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu56)
  grind_label.setVisible(True)
  
  weight_i2c_0.set_average_filter_level(20)
  weight_i2c_0.set_calibration(0, 8649015, 451, 9643602)
  weight_i2c_0.set_reset_offset()
  weight = weight_i2c_0.get_weight_float

def loop():
  global t, weight, mode, grind_label, single_dose, double_dose, grinding_active, grind_target, single_label, double_label, blink,i2c0, weight_i2c_0, relay_0, relay_pin, tare_offset, calib

  M5.update()
  t += 0.1
  weight = weight_i2c_0.get_weight_float

  if grinding_active:
    grinding_step()

  # Update display values
  single_label.setText("{:.1f}".format(single_dose))
  double_label.setText("{:.1f}".format(double_dose))
  grind_label.setText("{:.1f}".format(weight))

  if mode == "set_single":
      single_label.setVisible(True)
      double_label.setVisible(False)
      grind_label.setVisible(False)
  elif mode == "set_double":
      double_label.setVisible(True)
      single_label.setVisible(False)
      grind_label.setVisible(False)
  else:
      single_label.setVisible(True)
      double_label.setVisible(True)
      grind_label.setVisible(True)

  if BtnA.wasPressed():
    if mode == "grind" and not grinding_active:
      grind_target = single_dose
      grinding_active = True
    elif mode == "set_single":
      single_dose = max(0.5, single_dose - 0.1)
      save_doses()
      print("Setting single dose to {:.2f} g".format(single_dose))
    elif mode == "set_double":
      double_dose = max(0.5, double_dose - 0.1)
      save_doses()
      print("Setting double dose to {:.2f} g".format(double_dose))

  if BtnB.wasPressed() and not grinding_active:
    if mode == "grind" and not grinding_active:
      grind_target = double_dose
      grinding_active = True
    elif mode == "set_single":
      single_dose = min(15, single_dose + 0.1)
      save_doses()
      print("Setting single dose to {:.2f} g".format(single_dose))
    elif mode == "set_double":
      double_dose = min(30, double_dose + 0.1)
      save_doses()
      print("Setting double dose to {:.2f} g".format(double_dose))

  if BtnC.wasHold() and BtnC.isPressed():
    print("Button C was hold")
    weight_i2c_0.set_reset_offset()
    print("Weight reset via hold")
  else:
    c_hold_triggered = False

  if BtnC.wasSingleClicked():
    if mode == "grind":
      mode = "set_single"
    elif mode == "set_single":
      mode = "set_double"
    else:
      mode = "grind"
  print("ADC raw weight reading: {:.2f}".format(weight_i2c_0.get_adc_raw))
  print(weight_i2c_0.get_weight_str)

  relay_pin.value(grinding_active)
  time.sleep(0.2)

def grinding_step():
  global weight, grinding_active, grind_target
  grindspeed = 0.1
#   weight += grindspeed
  if weight >= grind_target or BtnB.wasPressed():
    grinding_active = False
    print("Grinding complete. Final weight: {:.2f} g".format(weight))
  else:
      print("Grinding active, current weight: {:.2f} g".format(weight))
      
def any_button_pressed():
  return BtnA.wasPressed() or BtnB.wasPressed() or BtnC.wasPressed()

if __name__ == '__main__':
  try:
    setup()
    while True:
      loop()
  except (Exception, KeyboardInterrupt) as e:
    try:
      from utility import print_error_msg
      print_error_msg(e)
    except ImportError:
      print("please update to latest firmware")


