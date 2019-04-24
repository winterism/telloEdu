#-*- coding: utf-8 -*-
'''
2019 4.24
작성자 한국교원대학교 컴퓨터교육과 전형기
단순동작
----------키 설명----------- 
화살표 위 아래 : 고도 변경
화살표 좌 우 : 좌우 각도 변경
w s a d : 앞/뒤/왼쪽/오른쪽

참고 
'''
from tello import Tello #tello 모듈로 부터 Tello를 불러온다.
import cv2 
import time # 시간 관련 모듈
import tkinter
import pygame
from pygame.locals import *
import numpy as np
bg_color = (128, 128, 128)
black = (0, 0, 0)
blue = (0, 50, 255)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 200, 0)

FPS = 25
S = 60

class Interface: 
   
    def __init__(self):
        self.tello = Tello()
        self.tello.sendCmd("streamon") #스트리밍 모드
        pygame.init()
        pygame.display.set_caption("KNUE Drone Stream")
        self.screen = pygame.display.set_mode([960, 720]) 
        pygame.time.set_timer(USEREVENT + 1, 50)
        
        self.font = pygame.font.Font("freesansbold.ttf", 14)
        
    def make_text(self, font, text, color, bgcolor, top, left, position = 0):
        surf = font.render(text, False, color, bgcolor)
        rect = surf.get_rect()
        if position:
            rect.center = (left, top)
        else:    
            rect.topleft = (left, top)
        self.screen.blit(surf, rect)
        return rect


    def run(self):
        '''
        프레임을 업데이트 하고 이벤트를 처리한다.
        '''
        frame_read = self.tello.get_frame_read()
        time.sleep(1)
        exitEvent = False
        previousCounter = 0
        while not exitEvent:
            #이벤트 검사
            for event in pygame.event.get():
                if event.type == USEREVENT + 1:
                    pass
                elif event.type == KEYDOWN:
                    keys = pygame.key.get_pressed()
                    self.keyDown(keys)
                elif event.type == KEYUP:
                    self.keyUp(keys)            
            if frame_read.stopped:
                frame_read.stop()
                break
            nowCounter = frame_read.frameCounter
            if nowCounter > previousCounter :
                self.screen.fill([0, 0, 0])                     # 스크린 칠하기(검정)
                frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB)   # 읽어온프레임의 색 형식 바꾸기
                frame = np.rot90(frame)                         # 90도 회전    
                frame = np.flipud(frame)                        # 위아래 전환
                face = pygame.surfarray.make_surface(frame)    # 화면 형식에 맞게 전환하고
                self.screen.blit(face, (0, 0))                 # 탐색필요
                self.frame_rect = self.make_text(self.font, "frameCount : "+str(nowCounter), blue, None, 20, 10)
                self.bat_rect = self.make_text(self.font, "batteryState : "+str(self.tello.battery), green, None, 40, 10)
                self.wifi_rect = self.make_text(self.font, "wifiState : "+str(self.tello.wifi), green, None, 60, 10)
                pygame.display.update()
                previousCounter =  frame_read.frameCounter     # 화면갱신
            pygame.display.update()
            time.sleep(1 / FPS)

    def keyDown(self, key):
        if key[pygame.K_HOME]: 
            self.tello.state = "takeoff"
        if key[pygame.K_END]: 
            self.tello.sendCmd("land")
            self.tello.state = "land"
        if key[pygame.K_UP]:  
            self.tello.speed_ud = 50
            print("key up")
        if key[pygame.K_DOWN]:
            self.tello.speed_ud = -50
            print("key down")
        if key[pygame.K_LEFT]:
            self.tello.speed_yaw = -50
            print("key left")
        if key[pygame.K_RIGHT]:
            self.tello.speed_yaw = 50
            print("key right")
        if key[pygame.K_w]:
            self.tello.speed_fb = 50
            print("key foward")
        if key[pygame.K_s]:
            self.tello.speed_fb = -50
            print("key back")
        if key[pygame.K_a]:
            self.tello.speed_lr = -50
        if key[pygame.K_d]:
            self.tello.speed_lr = 50

    def keyUp(self, key):
        if key[pygame.K_UP]:  
            self.tello.speed_ud = 0
        if key[pygame.K_DOWN]:
            self.tello.speed_ud = 0
        if key[pygame.K_LEFT]:
            self.tello.speed_yaw = 0
        if key[pygame.K_RIGHT]:
            self.tello.speed_yaw = 0
        if key[pygame.K_w]:
            self.tello.speed_fb = 0
        if key[pygame.K_s]:
            self.tello.speed_fb = 0
        if key[pygame.K_a]:
            self.tello.speed_lr = 0
        if key[pygame.K_d]:
            self.tello.speed_lr = 0


    def speedNormalize(self,value,cmd,multiply):
        """
        이 함수는 키 눌림에 따라 하여 반환
        반영되는 속도는 최고 속도를 초과하지 않음
        """  
        if abs(value+cmd * multiply) < self.tello.max_speed:
            value = value + cmd * multiply
        else :
            value = self.tello.max_speed * (abs(value)/value)
        return value

def main():
    interface = Interface()
    # run frontend 
    interface.run()

if __name__ == '__main__':
    main()