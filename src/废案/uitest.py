# -*- coding: utf-8 -*-
# @Time    : 2023/6/11 0:00
# @Author  : Kragy
# @File    : uitest.py


from ui.ui_w1 import Ui_f1
from ui.ui_w2 import Ui_f2
from ui.ui_Home import Ui_Home
from ui.ui_HomePage import Ui_HomePage
from ui.ui_Records import Ui_Records
from ui.ui_Setting import Ui_Setting


from PyQt5.QtCore import Qt,QUrl
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
import sys


class Ui_Home_customed(Ui_Home):
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.player.setVolume(0)
        self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(r'./videos/HomeBG.mp4')))  # 选取视频文件


class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1920, 1080)
        self.showFullScreen()
        self.ui = [Ui_HomePage(), Ui_Records(), Ui_Setting()]

        self.page = [QWidget(self) for i in range(len(self.ui))]
        for i in range(len(self.page)):
            self.ui[i].setupUi(self.page[i])
            self.page[i].setVisible(False)
        self.page[0].setVisible(True)

        # 播放背景视频
        self.ui[0].start.setAttribute(Qt.WA_TranslucentBackground)
        self.ui[0].player.setVideoOutput(self.ui[0].BGvideo)
        self.ui[0].player.play()


        # opEf = QGraphicsOpacityEffect()
        # opEf.setOpacity(0.5)
        # self.ui[0].options.setGraphicsEffect(opEf)
        # self.ui[0].options.setAttribute(Qt.WA_TranslucentBackground, True)

        # self.ui1.b1.clicked.connect(self.to2)
        # self.ui2.b2.clicked.connect(self.to1)

    def toHome(self):
        for i in self.page:
            i.setVisible(False)
        self.page[0].setVisible(True)

    def toRecords(self):
        for i in self.page:
            i.setVisible(False)
        self.page[1].setVisible(True)

    def toSetting(self):
        for i in self.page:
            i.setVisible(False)
        self.page[2].setVisible(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())
