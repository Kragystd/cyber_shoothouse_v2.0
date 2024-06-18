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
from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import *

import pygame
import math
import random
import threading
import time

import cv2
import numpy as np
from core import ShootingRange


class Ui_HomePage_customed(Ui_HomePage):
    def setupUi(self, HomePage, clickedEventList):
        super().setupUi(HomePage)
        self.retranslateUi_customed(self, clickedEventList)

    def retranslateUi_customed(self, HomePage, clickedEventList):
        self.cap = cv2.VideoCapture('./videos/HomeBG.mp4')
        self.isplay = True
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)
        self.bt_start.clicked.connect(lambda: clickedEventList[0](4))
        self.bt_records.clicked.connect(lambda: clickedEventList[0](1))
        self.bt_setting.clicked.connect(lambda: clickedEventList[0](2))
        self.bt_quit.clicked.connect(clickedEventList[-1])
        # self.bt_quit.clicked.connect(clickedEventList[5])

    def update_frame(self):
        """
        HomePage视频画面更新
        :return:
        """
        if self.isplay:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(image)
                self.videoLable.setPixmap(
                    pixmap.scaled(self.videoLable.width(), self.videoLable.height()))


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

        self.shootingRange = ShootingRange(0, '../imgs/st.png')
        self.timer = QTimer()

        self.timer.timeout.connect(lambda: self.update_frame(self.shootingRange.getCurrentData()))
        self.timer.start(10)

    def update_frame(self, frameData):

        cam = frameData[0]
        real_target = frameData[1]
        hitpoint = frameData[2]
        score = frameData[3]

        image = QImage(cam.data, cam.shape[1], cam.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.camLabel.setPixmap(
            pixmap.scaled(self.camLabel.width(), self.camLabel.height()))

        image = QImage(real_target.data, real_target.shape[1], real_target.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.targetLabel.setPixmap(
            pixmap.scaled(self.targetLabel.width(), self.targetLabel.height()))


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
            self.ui[0].isplay = True
        self.page[self.current_page].setVisible(False)
        self.page[page_id].setVisible(True)
        self.current_page = page_id
        if self.current_page != 0:
            self.ui[0].isplay = False

    def play_bgm_thread_target(self):
        pygame.mixer.init()
        # while True:
        #     pygame.mixer.Channel(0).play(
        #         pygame.mixer.Sound(f'sound\\bgm.wav'))
        #     time.sleep(150)

        pygame.mixer.Channel(0).play(pygame.mixer.Sound(f'../sound/bgm.wav'), -1)
        while True:
            if self.threadingKiller == True:
                pygame.mixer.Channel(0).stop()
                return

    def quitAll(self):
        QCoreApplication.instance().quit()
        self.threadingKiller = True

if __name__=='__main__':
    from GUI import *
    import sys

    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())
