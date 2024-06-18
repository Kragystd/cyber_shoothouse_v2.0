# -*- coding: utf-8 -*-
# @Time    : 2023/6/11 0:00
# @Author  : Kragy
# @File    : uitest.py


from ui.ui_HomePage import Ui_HomePage
from ui.ui_Records import Ui_Records
from ui.ui_Setting import Ui_Setting
from ui.ui_Calibrate import Ui_Calibrate
from ui.ui_StartMode import Ui_StartMode
from ui.ui_PlayPage import Ui_PlayPage

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import pygame
import threading
import time

import cv2
from queue import Queue
from src.wasted.core_optimized import ShootingRange

HomePageDecode2Play = Queue()
CoreDecode2Play = Queue()


class HomeBGcvDecode(QThread):
    def __init__(self):
        super(HomeBGcvDecode, self).__init__()
        self.threadFlag = True  # 控制线程退出
        self.pause = False
        self.cap = cv2.VideoCapture("videos/HomeBG.mp4")

    def run(self):
        while self.threadFlag:
            if not self.pause:
                if self.cap.isOpened():
                    ret, frame = self.cap.read()
                    time.sleep(0.01)  # 控制读取录像的时间，连实时视频的时候改成time.sleep(0.001)，多线程的情况下最好加上，否则不同线程间容易抢占资源
                    if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 控制循环播放
                    if ret:
                        HomePageDecode2Play.put(frame)  # 解码后的数据放到队列中
                    del frame  # 释放资源
            else:
                time.sleep(0.01)


class HomeBGPlayWork(QThread):
    def __init__(self):
        super(HomeBGPlayWork, self).__init__()
        self.threadFlag = True  # 控制线程退出
        self.pause = False  # 控制播放/暂停
        self.playLabel = QLabel()  # 初始化QLabel对象

    def run(self):
        while self.threadFlag:
            if not self.pause:
                if not HomePageDecode2Play.empty():
                    frame = HomePageDecode2Play.get()
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    qimg = QImage(frame.data, frame.shape[1], frame.shape[0],
                                  QImage.Format_RGB888)  # 在这里可以对每帧图像进行处理，
                    self.playLabel.setPixmap(QPixmap.fromImage(qimg))  # 图像在QLabel上展示
            else:
                time.sleep(1)
        time.sleep(0.01)


class CorecvDecode(QThread):
    def __init__(self):
        super(CorecvDecode, self).__init__()
        self.threadFlag = True  # 控制线程退出
        self.pause = True
        self.shr = ShootingRange(0, '../imgs/st.png')

    def run(self):
        while self.threadFlag:
            if not self.pause:
                if self.shr.cap.isOpened():
                    frameData = self.shr.getCurrentData()
                    time.sleep(0.001)  # 控制读取录像的时间，连实时视频的时候改成time.sleep(0.001)，多线程的情况下最好加上，否则不同线程间容易抢占资源
                    CoreDecode2Play.put(frameData)  # 解码后的数据放到队列中
                    del frameData  # 释放资源
            else:
                time.sleep(1)


class CorePlayWork(QThread):
    def __init__(self):
        super(CorePlayWork, self).__init__()
        self.threadFlag = True  # 控制线程退出
        self.pause = True  # 控制播放/暂停

        self.camLabel = QLabel()
        self.targetLabel = QLabel()
        self.hitpointLabel = QLabel()
        self.scoreLabel = QLabel()
        self.accuracyLabel = QLabel()
        self.avgscoreLabel = QLabel()
        self.headshotRateLabel = QLabel()

    def run(self):
        while self.threadFlag:
            if not self.pause:
                if not CoreDecode2Play.empty():
                    frameData = CoreDecode2Play.get()
                    cam = frameData[0]
                    target = frameData[1]
                    hitpoint = frameData[2]
                    score = frameData[3]
                    accuracy = frameData[4]
                    avgscore = frameData[5]
                    headshotRate = frameData[6]

                    cam = cv2.cvtColor(cam, cv2.COLOR_RGB2BGR)
                    camImg = QImage(cam.data, cam.shape[1], cam.shape[0], QImage.Format_RGB888)
                    self.camLabel.setPixmap(QPixmap.fromImage(camImg))  # 图像在QLabel上展示
                    if target is not None:
                        target = cv2.cvtColor(target, cv2.COLOR_RGB2BGR)
                        targetImg = QImage(target.data, target.shape[1], target.shape[0], QImage.Format_RGB888)
                        self.targetLabel.setPixmap(QPixmap.fromImage(targetImg))  # 图像在QLabel上展示
            else:
                time.sleep(1)
            time.sleep(0.001)


class Ui_HomePage_customed(Ui_HomePage):
    def setupUi(self, HomePage, clickedEventList):
        super().setupUi(HomePage)
        self.retranslateUi_customed(self, clickedEventList)

    def retranslateUi_customed(self, HomePage, clickedEventList):
        self.bt_start.clicked.connect(lambda: clickedEventList[0](4))
        self.bt_records.clicked.connect(lambda: clickedEventList[0](1))
        self.bt_setting.clicked.connect(lambda: clickedEventList[0](2))
        self.bt_quit.clicked.connect(clickedEventList[-1])

        # BGV播放
        self.decodework = HomeBGcvDecode()
        self.playwork = HomeBGPlayWork()
        self.playwork.playLabel = self.videoLable
        self.playBGV()

    def playBGV(self):
        self.decodework.start()
        self.playwork.start()

    def pauseBGV(self):
        self.decodework.pause = True
        self.playwork.pause = True

    def resumeBGV(self):
        self.decodework.pause = False
        self.playwork.pause = False

    def stopBGV(self):
        print("关闭线程")
        # Qt需要先退出循环才能关闭线程
        if self.decodework.isRunning():
            self.decodework.threadFlag = 0
            self.decodework.quit()
        if self.playwork.isRunning():
            self.playwork.threadFlag = 0
            self.playwork.quit()


class Ui_Records_customed(Ui_Records):
    def setupUi(self, Records, clickedEventList):
        super().setupUi(Records)
        self.retranslateUi_customed(self, clickedEventList)

    def retranslateUi_customed(self, Records, clickedEventList):
        self.bt_back.clicked.connect(lambda: clickedEventList[0](0))


class Ui_Setting_customed(Ui_Setting):
    def setupUi(self, Setting, clickedEventList):
        super().setupUi(Setting)
        self.retranslateUi_customed(self, clickedEventList)

    def retranslateUi_customed(self, Setting, clickedEventList):
        self.bt_back.clicked.connect(lambda: clickedEventList[0](0))


class Ui_Calibrate_customed(Ui_Calibrate):
    def setupUi(self, Calibrate, clickedEventList):
        super().setupUi(Calibrate)
        self.retranslateUi_customed(self, clickedEventList)

    def retranslateUi_customed(self, Calibrate, clickedEventList):
        self.bt_back.clicked.connect(lambda: clickedEventList[0](0))


class Ui_StartMode_customed(Ui_StartMode):
    def setupUi(self, StartMode, clickedEventList):
        super().setupUi(StartMode)
        self.retranslateUi_customed(self, clickedEventList)

    def retranslateUi_customed(self, StartMode, clickedEventList):
        self.bt_back.clicked.connect(lambda: clickedEventList[0](0))
        self.bt_Mode1.clicked.connect(lambda: clickedEventList[0](5))


class Ui_PlayPage_customed(Ui_PlayPage):

    def setupUi(self, PlayPage, clickedEventList):
        super().setupUi(PlayPage)
        self.retranslateUi_customed(self, clickedEventList)

    def retranslateUi_customed(self, PlayPage, clickedEventList):
        self.bt_back.clicked.connect(lambda: clickedEventList[0](0))

        # 核心功能
        self.decodework = CorecvDecode()
        self.playwork = CorePlayWork()

        self.playwork.camLabel = self.camLabel
        self.playwork.targetLabel = self.targetLabel
        self.playwork.hitpointLabel = self.hitpointLabel
        self.playwork.scoreLabel = self.scoreLabel
        self.playwork.accuracyLabel = self.accuracyLabel
        self.playwork.avgscoreLabel = self.avgscoreLabel
        self.playwork.headshotRateLabel = self.headshotRateLabel

        self.playCore()

    def playCore(self):
        self.decodework.start()
        self.playwork.start()

    def pauseCore(self):
        self.decodework.pause = True
        self.playwork.pause = True

    def resumeCore(self):
        self.decodework.pause = False
        self.playwork.pause = False

    def stopCore(self):
        print("关闭线程")
        # Qt需要先退出循环才能关闭线程
        if self.decodework.isRunning():
            self.decodework.threadFlag = 0
            self.decodework.quit()
        if self.playwork.isRunning():
            self.playwork.threadFlag = 0
            self.playwork.quit()


class mainWindow(QMainWindow):
    def __init__(self):
        self.clickedEventList = [self.toPage, self.quitAll]
        # 初始化UI
        # 创建UI对象
        super().__init__()
        self.ui = [
            Ui_HomePage_customed(),
            Ui_Records_customed(),
            Ui_Setting_customed(),
            Ui_Calibrate_customed(),
            Ui_StartMode_customed(),
            Ui_PlayPage_customed()
        ]

        # UI对象绑定到widget上
        self.page = [QWidget(self) for i in range(len(self.ui))]
        for i in range(len(self.page)):
            self.ui[i].setupUi(self.page[i], self.clickedEventList)
            self.page[i].setVisible(False)
        self.page[0].setVisible(True)
        self.current_page = 0

        # 显示窗口
        self.setFixedSize(1920, 1080)
        self.showFullScreen()

        # 播放BGM
        self.threadingKiller = False
        self.bgmPlayer_thread = threading.Thread(target=self.play_bgm_thread_target)
        self.bgmPlayer_thread.start()

    # 槽函数
    def toPage(self, page_id):
        if page_id == 0:
            self.ui[0].resumeBGV()
        if page_id == 5:
            self.ui[5].resumeCore()

        self.page[self.current_page].setVisible(False)
        self.page[page_id].setVisible(True)
        self.current_page = page_id

        if self.current_page != 0:
            self.ui[0].pauseBGV()
        if page_id != 5:
            self.ui[5].pauseCore()

    def play_bgm_thread_target(self):
        pygame.mixer.init()
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(f'../sound/bgm.wav'), -1)
        while True:
            time.sleep(1)
            if self.threadingKiller == True:
                pygame.mixer.Channel(0).stop()
                return

    def quitAll(self):
        QCoreApplication.instance().quit()
        self.threadingKiller = True
        self.ui[0].stopBGV()
        self.ui[5].stopCore()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())
