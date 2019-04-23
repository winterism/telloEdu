#-*- coding: utf-8 -*-
'''
2019 4.22
작성자 한국교원대학교 컴퓨터교육과 전형기
가속도 적용 인터페이스
----------키 설명----------- 
화살표 위 아래 : 고도 변경
화살표 좌 우 : 좌우 각도 변경
w s a d : 앞/뒤/왼쪽/오른쪽
'''

from tello import Tello #tello 모듈로 부터 Tello를 불러온다.
from tello import VideoStreamer
import sys
import time # 시간 관련 모듈
import tkinter

tello = Tello() # tello 인스턴스 를 생성한다. tello모듈에 객체의 명세가 기록되어 있다.
video = VideoStreamer()  # 스트림 인스턴스 생성한다. 
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
  이 함수는 키 눌림에 따라 하여 반환
  반영되는 속도는 최고 속도를 초과하지 않음
  """  
  if abs(value+cmd * multiply) < tello.max_speed:
    value = value + cmd * multiply
  else :
    value = tello.max_speed * (abs(value)/value)
  return value

def accelHeight(cmd):
  """
  이 함수는 키보드 눌림에 따라 텔로의 상하 이동 속도에 반영
  """  
  tello.speed_ud = speedNormalize(tello.speed_ud,cmd,15)

def accelYaw(cmd):
  """
  이 함수는 키보드 눌림에 따라 텔로의 좌우 회전 속도에 반영
  """
  tello.speed_yaw = speedNormalize(tello.speed_yaw,cmd,15)

def accelFB(cmd):
  """
  이 함수는 키보드 눌림에 따라 텔로의 앞뒤 이동 속도에 반영
  """
  tello.speed_fb = speedNormalize(tello.speed_fb,cmd,15)

def accelLR(cmd):
  """
  이 함수는 키보드 눌림에 따라 텔로의 왼쪽 오른쪽 이동 속도에 반영
  """
  tello.speed_lr = speedNormalize(tello.speed_lr,cmd,15)

def brake():
  tello.contrlNoReturn("stop")

def streamVideoStart():
  tello.contrlNoReturn("streamon")
  video.startVideoStream()

"""
이 아래는 키보드 맵핑과 gui 화면에 관련된 내용
"""
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
window.bind('[', lambda _: streamVideoStart()) #


window.mainloop()