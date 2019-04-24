'''
2019 4.24

Tello class 설명
  __init__(self) : 생성자 
  send_command(self, command) :  명령 보내기
  _receive_thread(self) : 텔로로 부터 받은 가장 최근의 것을 self.response에 저장한다. 
  get_log() : 로그 받기

참고 : https://zzsza.github.io/data/2018/01/23/opencv-1/
'''

import socket
import threading
import time
import cv2

# from stats import Stats

class Tello:

    state = ""
    cap = None
    background_frame_read = None
    stream_on = False
    VS_UDP_IP = '0.0.0.0'
    VS_UDP_PORT = 11111
    streamAddress = 'udp://@0.0.0.0:11111'
    wifi = 0
    battery = 0
    tello_ip = '192.168.10.1'
    tello_port = 8889
    tello_adderss = (tello_ip, tello_port)
    freamCounter = 0

    def __init__(self):
        self.local_ip = ""
        self.local_port = 8889
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 명령 소켓 생성
        self.socket.bind((self.local_ip, self.local_port)) #소켓을 로컬IP와 포트에 바인드
        self.sendCmd("command") #sdk모드로 전환
        self.state = "ready"
        self.control_thread = threading.Thread(target=self._control_thread) #_receive_thread를 별도 쓰레드로 지정
        self.control_thread.daemon = True # 데몬으로 작동하도록 설정, 데몬쓰레드는 메인쓰레드가 끝나면 끝난다.
        self.control_thread.start()

        #텔로 아이피 지정

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
        self.socket.sendto(command.encode('utf-8'), self.tello_adderss) #명령을 보냄. 최중요 코드
        self.response, ip = self.socket.recvfrom(1024)
        print("response : "+str(self.response))

        
    def get_udp_video_address(self):
        return 'udp://@' + self.VS_UDP_IP + ':' + str(self.VS_UDP_PORT)  # + '?overrun_nonfatal=1&fifo_size=5000'

    def get_video_capture(self):
        """Get the VideoCapture object from the camera drone
        Returns:
            VideoCapture
        """
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.get_udp_video_address())

        if not self.cap.isOpened():
            self.cap.open(self.get_udp_video_address())

        return self.cap

    def get_frame_read(self):
        """
        백그라운드 프레임 가져오기
        """
        if self.background_frame_read is None:
            self.background_frame_read = BackgroundFrameRead(self, self.get_udp_video_address()).start()
        return self.background_frame_read

    def _control_thread(self):
        """
        이 함수는 속도를 감속 하여 반환합니다.
        반영되는 속도는 최고 속도를 넘지 않습니다.
        takeoff 상태에서만 작동합니다.
        """
        controlCounter = 0

        while True:
            print("텔로 상태"+self.state)
            if self.state == "takeoff":
                # self.sendCmd("takeoff")
                self.socket.sendto("takeoff".encode('utf-8'), self.tello_adderss)
                self.response, ip = self.socket.recvfrom(1024)
                if self.response == b'ok':
                    self.state = "flying"
            if self.state == "flying":
                msg = ("rc %d %d %d %d" %(self.speed_lr, self.speed_fb, self.speed_ud, self.speed_yaw))
                self.socket.sendto(msg.encode('utf-8'), self.tello_adderss)
                print ("제어 %d %d %d %d" %(self.speed_lr, self.speed_fb, self.speed_ud, self.speed_yaw))
            self.socket.sendto("wifi?".encode('utf-8'), self.tello_adderss)
            self.wifi, ip = self.socket.recvfrom(1024)
            self.socket.sendto("battery?".encode('utf-8'), self.tello_adderss)
            self.battery, ip = self.socket.recvfrom(1024)
            time.sleep(0.2)

    def on_close(self):
        pass

    def get_log(self):
        return self.log

class BackgroundFrameRead:
    """
    This class read frames from a VideoCapture in background. Then, just call backgroundFrameRead.frame to get the
    actual one.
    """
    frameCounter = 0

    def __init__(self, tello, address):
        tello.cap = cv2.VideoCapture(address)
        self.cap = tello.cap

        if not self.cap.isOpened():
            self.cap.open(address)

        self.grabbed, self.frame = self.cap.read()
        self.stopped = False
        self.frameCounter = 0

    def start(self):
        streamingThread = threading.Thread(target=self.update_frame, args=())
        streamingThread.daemon = True
        streamingThread.start()
        return self

    def update_frame(self):
        while not self.stopped:
            if not self.grabbed or not self.cap.isOpened(): # 읽히지 않았는지 또는 열리지 않았는지
                self.stop()
            else:
                (self.grabbed, self.frame) = self.cap.read() # grabbed가 True면 읽힌것, frame에는 읽은 프레임이 들어간다.
                self.frameCounter = self.frameCounter + 1
        
    def stop(self):
        self.stopped = True
