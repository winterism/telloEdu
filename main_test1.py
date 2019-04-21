#-*- coding: utf-8 -*-
'''
2019 4.21
작성자 한국교원대학교 컴퓨터교육과 전형기
map 기능 테스트
'''
from tello import Tello #tello 모듈로 부터 Tello를 불러온다.
import sys
from datetime import datetime
import time # 시간 관련 모듈

tello = Tello() # tello 객체를 생성한다. tello모듈에 객체의 명세가 기록되어 있다.

'''
Tello class 에서 제공하는 함수
  send_command(command) :  명령 보내기
  get_log() : 로그 받기
'''
#명령의 시작과 이륙
tello.send_command("command")
tello.send_command("takeoff")
time.sleep(1)

#맵인식켜기 : mon
tello.send_command("mon")

#맵 인식방향 설정 : 
tello.send_command("mdirection 0")
time.sleep(0.5)

#맵 기반 좌표 설정 : go x y z v m
#  x y z s m은 각각 x좌표 y좌표 z좌표 속도 맵 번호다.
tello.send_command("go 0 0 90 10 m1")
time.sleep(0.1)

# 90에서 50으로 순차적으로 고도 조정
for i in range(90, 50, -10):
  tello.send_command("go 0 0 %d 10 m1" %i)
  time.sleep(0.5)

# 맵간 이동 : 
tello.send_command("jump 0 0 100 10 0 m1 m2")
time.sleep(0.5)
tello.send_command("go 0 0 50 10 m2")
time.sleep(0.5)
tello.send_command("up 100")
time.sleep(0.5)
tello.send_command("jump 0 0 100 10 0 m2 m3")
time.sleep(0.5)
tello.send_command("go 0 0 50 10 m3")
time.sleep(0.5)
tello.send_command("up 100")
time.sleep(0.5)
tello.send_command("jump 0 0 100 10 0 m3 m4")
time.sleep(0.5)
tello.send_command("up 100")
time.sleep(0.5)
tello.send_command("jump 0 0 100 10 0 m4 m1")
time.sleep(0.5)
tello.send_command("up 100")
time.sleep(0.5)

# 착륙
tello.send_command("moff")
tello.send_command("land")
