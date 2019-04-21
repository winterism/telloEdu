#-*- coding: utf-8 -*-
'''
2019 4.21
작성자 한국교원대학교 컴퓨터교육과 전형기
기본기능 테스트용
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

#명령대기 지시 : 텔로에게 명령을 줄테니 대기하라 라는 의미로  command 라는 문자열을 전송한다.
#wifi를 통해 명령이 전달된다.
#아무 일도 일어 나지 않으나 텔로는 대기 하고 있다.
tello.send_command("command")

#텔로 이륙시키기 : takeoff라는 문자열은 이륙을 지시한다.
tello.send_command("takeoff")

#시간지연하기 : time 모듈에 있는 sleep을 사용한다. sleep은 프로그램의 진행을 잠시 멈춘다. 단위는 1초 이며 소수도 받아들인다.
time.sleep(2)

#텔로 고도 상승 : up xx 문자열은 고도를 xx만큼 상승시킨다. 단위는 cm이며 최소값은 20, 최대값은 500
tello.send_command("up 20")
time.sleep(2)

#텔로 전진 : forward xx 문자열은 앞으로 전진시키며 xx는 전진할 거리다
tello.send_command("forward 20")
time.sleep(5)

#텔로 후진 : back xx 문자열은 뒤로 전진시키며 xx는 후진할 거리다
tello.send_command("back 20")
time.sleep(5)


#텔로 고도 하강 : down xx 문자열은 고도를 xx만큼 상승시킨다. 단위는 cm이며 최소값은 20, 최대값은 500
tello.send_command("down 20")
time.sleep(2)

#텔로 회전시키기 : 시계방향이 기준이다. cw xx 는 시계방향으로 xx도 만큼 자세를 회전시킨다.
#  xx는 최소 1도에서 360 정수만 가능
tello.send_command("cw 90")
time.sleep(2)

#텔로 회전시키기 : 시계방향이 기준이다. cw xx 는 시계방향으로 xx도 만큼 자세를 회전시킨다. 
#xx는 최소 1도에서 360 정수만 가능
tello.send_command("ccw 90")
time.sleep(2)


#뒤집기 : flip xx 는 뒤집기를 시도한다. 
#xx는 뒤집기 방향이며 xx가 각각 l/r/f/b 일때 
#왼쪽으로 뒤집기, 오른쪽으로 뒤집기 앞으로 뒤집기 뒤로 뒤집기를 시도한다.
tello.send_command("flip l")
time.sleep(1)
tello.send_command("flip r")
time.sleep(1)
tello.send_command("flip f")
time.sleep(1)
tello.send_command("flip b")
time.sleep(1)

#텔로 착륙시키기 : land라는 문자열은 착륙을 지시한다.
tello.send_command("land")