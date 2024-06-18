# -*- coding: utf-8 -*-
# @Time    : 2023/6/11 0:00
# @Author  : Kragy
# @File    : uitest.py


from ui.ui_PlayPage import Ui_PlayPage

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import pygame
import threading
import time

import cv2
from src.wasted.core_optimized import ShootingRange


class Ui_PlayPage_customed(Ui_PlayPage):
    def __init__(self):
        self.label = None

    def setupUi(self, PlayPage):
        super().setupUi(PlayPage)
        # 核心功能
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)  # 30 ms 捕获一帧
        self.sr = ShootingRange('http://192.168.137.203:4747/video', '../imgs/st.png')  # 摄像头索引，可以根据需要进行调整

    def update_frame(self):
        frameData = self.sr.getCurrentData()
        frame = frameData[0]

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.camLabel.setPixmap(pixmap.scaled(self.camLabel.width(), self.camLabel.height()))

        target = frameData[1]
        if target is not None:
            image = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
            image = QImage(target.data, target.shape[1], target.shape[0], target.shape[1] * target.shape[2],
                           QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.targetLabel.setPixmap(pixmap.scaled(self.targetLabel.width(), self.targetLabel.height()))


class mainWindow(QMainWindow):
    def __init__(self):

        # 初始化UI
        # 创建UI对象
        super().__init__()
        self.ui = Ui_PlayPage_customed()
        self.page = QWidget(self)

        # UI对象绑定到widget上
        self.ui.setupUi(self.page)

        # 显示窗口
        self.setFixedSize(1920, 1080)
        self.showFullScreen()

        # # 播放BGM
        self.threadingKiller = False
        self.bgmPlayer_thread = threading.Thread(target=self.play_bgm_thread_target)
        self.bgmPlayer_thread.start()

    # 槽函数

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
