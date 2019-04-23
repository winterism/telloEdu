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
import sys
import cv2
import time # 시간 관련 모듈
import tkinter
import pygame
from pygame.locals import *
import numpy as np

FPS = 25
S = 60


class Interface:    
    def __init__(self):
        self.tello = Tello()
        self.tello.sendCmd("command") #sdk모드로 전환
        self.tello.sendCmd("streamon") #sdk모드로 전환
        pygame.init()
        pygame.display.set_caption("KNUE Drone Stream")
        self.screen = pygame.display.set_mode([1280, 720]) 
        pygame.time.set_timer(USEREVENT + 1, 50)

    def run(self):
        frame_read = self.tello.get_frame_read()
        time.sleep(1)

        exitEvent = False
        while not exitEvent:
            #이벤트 검사
            for event in pygame.event.get():
                if event.type == USEREVENT + 1:
                    pass
                elif event.type == KEYDOWN:
                    self.keyDown(event.key)
            
            #화면셋

            if frame_read.stopped:
                frame_read.stop()
                break

            self.screen.fill([0, 0, 0])                     # 스크린 칠하기(검정)
            frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB)   # 읽어온프레임의 색 형식 바꾸기
            frame = np.rot90(frame)                         # 90도 회전    
            frame = np.flipud(frame)                        # 위아래 전환
            face = pygame.surfarray.make_surface(frame)    # 화면 형식에 맞게 전환하고
            self.screen.blit(face, (0, 0))                 # 탐색필요
            pygame.display.update()                         # 화면갱신
            time.sleep(1 / FPS)

    def keyDown(self, key):
        if key == pygame.K_UP:  
            self.tello.speed_ud = self.speedNormalize(self.tello.speed_ud,1,15)
        elif key == pygame.K_HOME: 
            self.tello.sendCmd("takeoff")
        elif key == pygame.K_END: 
            self.tello.sendCmd("land")
        elif key == pygame.K_DOWN:
            self.tello.speed_ud = self.speedNormalize(self.tello.speed_ud,-1,15)        
        elif key == pygame.K_LEFT:
            self.tello.speed_yaw = self.speedNormalize(self.tello.speed_yaw,1,15)
        elif key == pygame.K_RIGHT:
            self.tello.speed_yaw = self.speedNormalize(self.tello.speed_yaw,-1,15)      
        elif key == pygame.K_w:
            self.tello.speed_fb = self.speedNormalize(self.tello.speed_fb,1,15)
        elif key == pygame.K_s:
            self.tello.speed_fb = self.speedNormalize(self.tello.speed_fb,-1,15)
        elif key == pygame.K_a:
            self.tello.speed_lr = self.speedNormalize(self.tello.speed_lr,1,15)
        elif key == pygame.K_d:
            self.tello.speed_lr = self.speedNormalize(self.tello.speed_lr,-1,15)


    def keyCmd(self, cmd):
        if cmd=="takeoff" or cmd=="land" or cmd=="command":
            self.tello.sendCmd(cmd)
            self.tello.state = "takeoff"
        elif cmd=="land":
            self.tello.sendCmd(cmd)
            self.tello.state = "land"
        elif cmd=="command":
            self.tello.sendCmd(cmd)
            self.tello.state = "ready"
        else:
            self.tello.sendCmd(cmd+" 20")

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

    def brake(self):
        self.tello.contrlNoReturn("stop")



def main():
    interface = Interface()
    # run frontend
    interface.run()


if __name__ == '__main__':
    main()