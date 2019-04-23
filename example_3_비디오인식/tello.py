'''
Tello class 설명
  __init__(self) : 생성자 
  send_command(self, command) :  명령 보내기
  _receive_thread(self) : 텔로로 부터 받은 가장 최근의 것을 self.response에 저장한다. 
  get_log() : 로그 받기
'''

import socket
import threading
import time
from stats import Stats
import cv2.cv2 as cv2
import numpy as np
# import libh264decoder

class VideoStreamer:
    stream_ip = '0.0.0.0'
    stream_port = 11111
    width = 1280
    height = 720
    buff = 2048
    num_of_chunks = width * height * 3 /buff
    code = b'start'

    def __init__(self):
        # 비디오스트림을 받기 위한 서버 소켓 설정
        self.streamSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 스트림 소켓 생성
        self.streamSocket.bind((self.stream_ip, self.stream_port)) #소켓을 IP와 포트에 바인드
        # self.decoder = libh264decoder.H264Decoder()
        self.frame = None

    def videoStream(self):
        while True:
            chunks = []
            start = False
            packet_data = ""
            while True:
                res_string, ip = self.streamSocket.recvfrom(2048)
                packet_data += res_string

                # chunk, _ = self.streamSocket.recvfrom(2048)

                # if start:
                #     chunks.append(chunk)
                # elif chunk.startswith(self.code):
                #     start = True

                byte_frame = b''.join(packet_data)

                frame = np.frombuffer(
                    byte_frame, dtype=np.uint8).reshape(self.height, self.width, 3)
                cv2.imshow('recv', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

 
    #             # end of frame
    #             if len(res_string) != 1460:
    #                 for frame in self._h264_decode(packet_data):
    #                     self.frame = frame
    #                 packet_data = ""

    # def _h264_decode(self, packet_data):
    #     """
    #     decode raw h264 format data from Tello
        
    #     :param packet_data: raw h264 data array
       
    #     :return: a list of decoded frame
    #     """
    #     res_frame_list = []
    #     frames = self.decoder.decode(packet_data)
    #     for framedata in frames:
    #         (frame, w, h, ls) = framedata
    #         if frame is not None:
    #             # print 'frame size %i bytes, w %i, h %i, linesize %i' % (len(frame), w, h, ls)

    #             frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
    #             frame = (frame.reshape((h, ls / 3, 3)))
    #             frame = frame[:, :w, :]
    #             res_frame_list.append(frame)
    #     return res_frame_list

    def startVideoStream(self):
        self.video_thread = threading.Thread(target=self.videoStream) #_receive_thread를 별도 쓰레드로 지정
        self.video_thread.daemon = True # 데몬으로 작동하도록 설정, 데몬쓰레드는 메인쓰레드가 끝나면 끝난다.
        self.video_thread.start()

class Tello:
    state = ''
   
    def __init__(self):
        self.local_ip = ''
        self.local_port = 8889
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 명령 소켓 생성
        self.socket.bind((self.local_ip, self.local_port)) #소켓을 로컬IP와 포트에 바인드
        # 응답이 보고될 쓰레드 생성하고 쓰레드 시작
        self.receive_thread = threading.Thread(target=self._receive_thread) #_receive_thread를 별도 쓰레드로 지정
        self.receive_thread.daemon = True # 데몬으로 작동하도록 설정, 데몬쓰레드는 메인쓰레드가 끝나면 끝난다.
        self.receive_thread.start()

        self.control_thread = threading.Thread(target=self._control_thread) #_receive_thread를 별도 쓰레드로 지정
        self.control_thread.daemon = True # 데몬으로 작동하도록 설정, 데몬쓰레드는 메인쓰레드가 끝나면 끝난다.
        self.control_thread.start()
        self.state = 'ready'

        #텔로 아이피 지정
        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889
        self.tello_adderss = (self.tello_ip, self.tello_port)
        self.log = []
        #타임아웃 시간 15초
        self.MAX_TIME_OUT = 15.0
        self.speed_lr = 0
        self.speed_fb = 0
        self.speed_ud = 0
        self.speed_yaw = 0
        self.max_speed = 100

    def sendCmd(self, command):
        """
        텔로 ip에 명령을 보냅니다. OK가 수신될때까지 이 함수에 머물게 됩니다.
        즉, 보낸명령이 수행되었다는 보고를 받기 전까진 다른 명령을 보낼 수 없습니다.
        """
        self.log.append(Stats(command, len(self.log))) #로그 저장
        self.socket.sendto(command.encode('utf-8'), self.tello_adderss) #명령을 보냄. 최중요 코드
        print('명령을 보내는중... 명령: %s IP %s'%(command, self.tello_ip))
        print("명령을 입력할 수 없음")

        #현재시간과 지연시간을 비교하여 초과하면 블록됨
        start = time.time() 
        while not self.log[-1].got_response():
            now = time.time()
            diff = now - start
            if diff > self.MAX_TIME_OUT:
                print('최대 대기시간을 초과했습니다... command %s'%(command))
                return
        
        #현재시간과 지연시간을 비교하여 초과하면 블록됨
        print('명령 보내기 성공: %s to %s'%(command, self.tello_ip))

    def contrlNoReturn(self, command):
        self.socket.sendto(command.encode('utf-8'), self.tello_adderss)

    def _control_thread(self):
        """
        이 함수는 속도를 감속 하여 반환합니다.
        반영되는 속도는 최고 속도를 넘지 않습니다.
        takeoff 상태에서만 작동합니다.
        """
        while True:
            if self.state == "takeoff":
                msg = ("rc %d %d %d %d" %(self.speed_lr, self.speed_fb, self.speed_ud, self.speed_yaw))
                self.socket.sendto(msg.encode('utf-8'), self.tello_adderss)
                time.sleep(0.1)
                print ("rc %d %d %d %d" %(self.speed_lr, self.speed_fb, self.speed_ud, self.speed_yaw))

                if abs(self.speed_fb) > 20:
                    temp = self.speed_fb
                    self.speed_fb=(abs(temp)/2)*(abs(temp)/temp)
                else :
                    self.speed_fb = 0
                if abs(self.speed_lr) > 20:
                    temp = self.speed_lr
                    self.speed_lr=(abs(temp)/2)*(abs(temp)/temp)
                else :
                    self.speed_lr = 0
                if abs(self.speed_ud) > 20:
                    temp = self.speed_ud
                    self.speed_ud=(abs(temp)/2)*(abs(temp)/temp)
                else :
                    self.speed_ud = 0
                if abs(self.speed_yaw) > 20:
                    temp = self.speed_yaw
                    self.speed_yaw=(abs(temp)/2)*(abs(temp)/temp)
                else :
                    self.speed_yaw = 0

            else:
                print("전송안함")
                time.sleep(1)

    def _receive_thread(self):
        """
        별도 쓰레드로 작동하며 명령에 대해 텔로로 부터 들은 응답이 보고됩니다.
        """
        while True:
            try:
                self.response, ip = self.socket.recvfrom(1024)
                print('IP %s 로 부터 온 응답: %s'%(ip, self.response))
                self.log[-1].add_response(self.response)
            except socket.error as exc:
                print("소켓 에러 발생 : %s"%(exc))

    def on_close(self):
        pass

    def get_log(self):
        return self.log