#-*- coding: utf-8 -*-
'''
2019 4.21
작성자 한국교원대학교 컴퓨터교육과 전형기
UI삽입용
'''

from tello import Tello #tello 모듈로 부터 Tello를 불러온다.
import sys
from datetime import datetime
import time # 시간 관련 모듈
import tkinter


tello = Tello() # tello 객체를 생성한다. tello모듈에 객체의 명세가 기록되어 있다.
tello.sendCmd("command")

def keyCmd(cmd):
  if cmd=="takeoff" or cmd=="land" or cmd=="command":
    tello.sendCmd(cmd)
    tello.state = "takeoff"
  elif cmd=="land":
    tello.sendCmd(cmd)
    tello.state = "land"
  elif cmd=="command":
    tello.sendCmd(cmd)
    tello.state = "ready"
  else:
    tello.sendCmd(cmd+" 20")


def speedNormalize(value,cmd,multiply):
  """
  이 함수는 속도를 가속화 하여 반환
  반영되는 속도는 최고 속도를 초과하지 않음
  """  
  if abs(value) < tello.max_speed-10:
    value = value + cmd * multiply
  else :
    value = tello.max_speed * (abs(value)/value)
  return value

def accelHeight(cmd):
  tello.speed_ud = speedNormalize(tello.speed_ud,cmd,20)

def accelYaw(cmd):
  tello.speed_yaw = speedNormalize(tello.speed_yaw,cmd,20)

def accelFB(cmd):
  tello.speed_fb = speedNormalize(tello.speed_fb,cmd,20)

def accelLR(cmd):
  tello.speed_lr = speedNormalize(tello.speed_lr,cmd,20)

def brake():
  tello.contrlNoReturn("stop")

window=tkinter.Tk()
label=tkinter.Label(window, text=tello.state)
label.pack()
canvas=tkinter.Canvas(window, relief="solid", bd=2)
canvas.pack(expand=True, fill="both")

window.bind('<Return>', lambda _: keyCmd("command")) #
window.bind('<Shift-Up>', lambda _: keyCmd("takeoff")) #
window.bind('<Shift-Down>', lambda _: keyCmd("land")) #
window.bind('<Up>', lambda _: accelHeight(1)) #
window.bind('<Down>', lambda _: accelHeight(-1)) #
window.bind('<Right>', lambda _: accelYaw(1)) #
window.bind('<Left>', lambda _: accelYaw(-1)) #
window.bind('a', lambda _: accelLR(-1)) #
window.bind('d', lambda _: accelLR(1)) #
window.bind('w', lambda _: accelFB(1)) #
window.bind('s', lambda _: accelFB(-1)) #

window.mainloop()