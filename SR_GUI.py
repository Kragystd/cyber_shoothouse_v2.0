# -*- coding: utf-8 -*-
# @Time    : 2023/6/11 0:00
# @Author  : Kragy
# @File    : uitest.py
import gc
import json
import os

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
import math
import random
import threading
import time

import cv2
from queue import Queue
from ShootingRange import ShootingRange

# 常量
HOMEPAGE = 0
RECORDS = 1
SETTING = 2
CALIBRATE = 3
STARTMODE = 4
PLAYPAGE = 5

# 通信容器
HomePageDecode2Play = Queue()
CoreDecode2Play = Queue()


class HomeBGV_player:
    def __init__(self, target_ui):

        self.thread_on = False

        # 功能变量
        self.cap = cv2.VideoCapture("videos/HomeBG.mp4")
        self.ui = target_ui

    def decode_thread_target(self):
        while self.thread_on:
            time.sleep(0.01)
            # print('HomeBGV decoding...')
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 控制循环播放
                if ret:
                    HomePageDecode2Play.put(frame)  # 解码后的数据放到队列中
                del frame  # 释放资源
        # print('HomeBGV decoding stopped...')

    def show_thread_target(self):
        while self.thread_on:
            time.sleep(0.01)
            # print('HomeBGV showing...')
            if not HomePageDecode2Play.empty():
                frame = HomePageDecode2Play.get()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                qimg = QImage(frame.data, frame.shape[1], frame.shape[0],
                              QImage.Format_RGB888)  # 在这里可以对每帧图像进行处理，
                self.ui.setPixmap(QPixmap.fromImage(qimg))  # 图像在QLabel上展示
        # print('HomeBGV showing stopped...')

    def on(self):
        self.thread_on = True
        self.decode_thread = threading.Thread(target=self.decode_thread_target)
        self.decode_thread.start()

        self.show_thread = threading.Thread(target=self.show_thread_target)
        self.show_thread.start()

    def off(self):
        self.thread_on = False


class Core_player:
    def __init__(self, target_ui):

        self.thread_on = False

        # 功能变量
        self.ui = target_ui
        self.sound_num_dict = self.sound_num_dict_load()  # 随即声效数量字典
        self.soundBackPlayer = sound_player()

    def decode_thread_target(self):
        while self.thread_on:
            time.sleep(0.01)
            # print('Core decoding...')
            if hasattr(self.sr, 'cap') and self.sr.cap.isOpened():
                frameData = self.sr.getCurrentData()
                time.sleep(0.001)  # 控制读取录像的时间，连实时视频的时候改成time.sleep(0.001)，多线程的情况下最好加上，否则不同线程间容易抢占资源
                CoreDecode2Play.put(frameData)  # 解码后的数据放到队列中
                del frameData  # 释放资源
        # print('Core decoding stopped...')

    def show_thread_target(self):
        while self.thread_on:
            time.sleep(0.01)
            # print('Core showing...')
            if not CoreDecode2Play.empty():
                frameData = CoreDecode2Play.get()
                cam = frameData[0]
                target = frameData[1]
                hitpoint = str(frameData[2]) if frameData[2] is not None else '(*,*)'
                score = format(frameData[3], "0.2f") if frameData[2] is not None else None
                count = str(frameData[4])
                accuracy = format(frameData[5], "0.2f")
                avgscore = format(frameData[6], "0.2f")
                headshotRate = format(frameData[7], "0.2f")

                # 声音反馈
                if self.sound_config['mute'] is False and score is not None:
                    self.soundBack(score=frameData[3])

                cam = cv2.cvtColor(cam, cv2.COLOR_RGB2BGR)
                camImg = QImage(cam.data, cam.shape[1], cam.shape[0], QImage.Format_RGB888)
                self.ui.camLabel.setPixmap(QPixmap.fromImage(camImg))  # 图像在QLabel上展示
                if target is not None:
                    target = cv2.cvtColor(target, cv2.COLOR_RGB2BGR)
                    target = cv2.resize(target, (self.ui.targetLabel.width(), self.ui.targetLabel.height()))
                    targetImg = QImage(target.data, self.ui.targetLabel.width(), self.ui.targetLabel.height(),
                                       target.shape[1] * target.shape[2],
                                       QImage.Format_RGB888)
                    self.ui.targetLabel.setPixmap(QPixmap.fromImage(targetImg))  # 图像在QLabel上展示
                if score is not None:
                    self.ui.hitpointLabel.setText(f'命中点：{hitpoint}')
                    self.ui.scoreLabel.setText(f'分数：{score}')
                self.ui.countLabel.setText(f'计数：{count}')
                self.ui.accuracyLabel.setText(f'准确率：{accuracy}')
                self.ui.avgscoreLabel.setText(f'平均分：{avgscore}')
                self.ui.headshotRateLabel.setText(f'爆头率：{headshotRate}')

        # print('Core showing stopped...')

    def on(self, sr, sound_config):
        self.thread_on = True
        self.sr = sr
        self.sound_config = sound_config
        self.decode_thread = threading.Thread(target=self.decode_thread_target)
        self.decode_thread.start()

        self.show_thread = threading.Thread(target=self.show_thread_target)
        self.show_thread.start()

    def off(self):
        self.thread_on = False
        self.sr = None
        gc.collect()

    def sound_num_dict_load(self):
        sound_filename_list = os.listdir('src/sound')
        hit_real = len([i for i in sound_filename_list if i.startswith('hit_real')])
        shell_fall = len([i for i in sound_filename_list if i.startswith('shell_fall')])
        hit_feedback = len([i for i in sound_filename_list if i.startswith('hit_feedback')])
        return {'hit_real': hit_real,
                'shell_fall': shell_fall,
                'hit_feedback': hit_feedback
                }

    def soundBack(self, score):
        soundBack_thread = threading.Thread(target=self.soundBack_target, args=(score,))
        soundBack_thread.start()

    def soundBack_target(self, score):
        # 是否击中靶子
        if self.sound_config['fire_sound']:
            self.soundBackPlayer.on(
                sound_path=f'src/sound\hit_real{math.floor(self.sound_num_dict["hit_real"] * random.random())}.wav',
                channel=1)
        time.sleep(0.15)

        if self.sound_config['hit_sound'] and 0 < score:
            self.soundBackPlayer.on(
                sound_path=f'src/sound/hit_feedback{math.floor(self.sound_num_dict["hit_feedback"] * random.random())}.wav',
                channel=2)
        if self.sound_config['kill_sound'] and 6 <= score < 8:
            self.soundBackPlayer.on(sound_path=f'src/sound/kill0.wav', channel=2)
        elif self.sound_config['kill_sound'] and score >= 8:
            self.soundBackPlayer.on(sound_path=f'src/sound/headshot0.wav', channel=2)

        time.sleep(0.2)
        if self.sound_config['shell_sound']:
            self.soundBackPlayer.on(
                sound_path=f'src/sound\shell_fall{math.floor(self.sound_num_dict["shell_fall"] * random.random())}.wav',
                channel=3)
        return


class sound_player:
    def __init__(self, sound_path=None, channel=None, auto_play=False, loop=False):
        self.thread_on = False
        self.sound_path = sound_path
        self.channel = channel
        self.loop = loop
        if auto_play:
            self.on()

    def play_thread_target(self):
        pygame.mixer.init()
        if self.loop:
            pygame.mixer.Channel(self.channel).play(pygame.mixer.Sound(self.sound_path), -1)
        else:
            pygame.mixer.Channel(self.channel).play(pygame.mixer.Sound(self.sound_path))
            return
        while self.thread_on:
            time.sleep(0.01)
        return

    def on(self, sound_path=None, channel=None, auto_play=False, loop=False):

        if sound_path is not None and channel is not None:
            self.thread_on = True

            self.sound_path = sound_path
            self.channel = channel
            self.loop = loop
        self.decode_HomeBGV_thread = threading.Thread(target=self.play_thread_target)
        self.decode_HomeBGV_thread.start()

    def off(self):
        self.thread_on = False


class SR_GUI(QMainWindow):
    def __init__(self):

        # 功能变量
        with open('src/config/config.json', encoding='utf-8') as json_file:
            self.config = json.load(json_file)
        self.camera_valid = False

        # 初始化UI
        # 创建UI对象
        super().__init__()
        self.ui = [
            Ui_HomePage(),
            Ui_Records(),
            Ui_Setting(),
            Ui_Calibrate(),
            Ui_StartMode(),
            Ui_PlayPage()
        ]

        # UI对象绑定到widget上
        self.page = [QWidget(self) for i in range(len(self.ui))]
        for i in range(len(self.page)):
            self.ui[i].setupUi(self.page[i])
            self.page[i].setVisible(False)
        self.page[0].setVisible(True)
        self.current_page = 0

        # 自定义窗口设置
        self.customizeUI()

        # 显示窗口
        self.setFixedSize(1920, 1080)
        self.showFullScreen()

        # 播放BGM
        self.bgm_player = sound_player(sound_path='src/sound/bgm.wav', channel=0, auto_play=True, loop=True)

    def customizeUI(self):

        # homePage
        self.ui[HOMEPAGE].bt_start.clicked.connect(self.homePage_click_start)
        self.ui[HOMEPAGE].bt_records.clicked.connect(self.homePage_click_Records)
        self.ui[HOMEPAGE].bt_setting.clicked.connect(self.homePage_click_Setting)
        self.ui[HOMEPAGE].bt_quit.clicked.connect(self.homePage_click_quit)

        self.homeBGV_player = HomeBGV_player(target_ui=self.ui[HOMEPAGE].videoLable)
        self.homeBGV_player.on()

        # Records
        self.ui[RECORDS].bt_back.clicked.connect(self.Records_click_bt_back)

        # Setting
        self.ui[SETTING].bt_back.clicked.connect(self.Setting_click_bt_back)
        self.ui[SETTING].bt_apply.clicked.connect(self.Setting_click_bt_apply)

        self.ui[SETTING].cam_input.setAlignment(Qt.AlignCenter)
        self.ui[SETTING].tick_input.setAlignment(Qt.AlignCenter)
        self.ui[SETTING].threshold_input.setAlignment(Qt.AlignCenter)
        self.ui[SETTING].score_precision_input.setAlignment(Qt.AlignCenter)

        # Calibrate
        self.ui[CALIBRATE].bt_back.clicked.connect(self.Calibrate_click_bt_back)

        # StartMode
        self.ui[STARTMODE].bt_back.clicked.connect(self.StartMode_click_bt_back)
        self.ui[STARTMODE].bt_Mode1.clicked.connect(self.StartMode_click_bt_Model1)
        self.ui[STARTMODE].bt_Mode2.clicked.connect(self.StartMode_click_bt_Model2)
        self.ui[STARTMODE].bt_Mode3.clicked.connect(self.StartMode_click_bt_Model3)

        # PlayPage
        self.ui[PLAYPAGE].bt_back.clicked.connect(self.PlayPage_click_bt_back)
        self.core_player = Core_player(target_ui=self.ui[PLAYPAGE])
        self.ui[PLAYPAGE].bt_reset.clicked.connect(self.PlayPage_click_bt_reset)
        self.ui[PLAYPAGE].bt_save.clicked.connect(self.PlayPage_click_bt_save)

        return

    def setUItext(self, ui, content):
        setUItext_thread = threading.Thread(target=self.setUItext_target, args=(ui, content))
        setUItext_thread.start()

    # 槽函数
    def toPage(self, page_id):
        self.page[self.current_page].setVisible(False)
        self.page[page_id].setVisible(True)
        self.current_page = page_id

    # homePage
    def homePage_click_start(self):
        sound_player('src/sound/clicked.wav', channel=5, auto_play=True)
        self.toPage(STARTMODE)
        self.homeBGV_player.off()

    def homePage_click_Records(self):
        sound_player('src/sound/enter_records.wav', channel=5, auto_play=True)
        # self.toPage(RECORDS)
        # self.homeBGV_player.off()
        os.system('explorer .\\records')

    def homePage_click_Setting(self):
        sound_player('src/sound/clicked.wav', channel=5, auto_play=True)

        self.ui[SETTING].fire_sound.setChecked(self.config['sound_config']['fire_sound'])
        self.ui[SETTING].shell_sound.setChecked(self.config['sound_config']['shell_sound'])
        self.ui[SETTING].hit_sound.setChecked(self.config['sound_config']['hit_sound'])
        self.ui[SETTING].kill_sound.setChecked(self.config['sound_config']['kill_sound'])

        self.ui[SETTING].cam_input.setText(str(self.config['shootRange_config']['camera']))
        self.ui[SETTING].tick_input.setText(str(self.config['shootRange_config']['tick']))
        self.ui[SETTING].threshold_input.setText(str(self.config['shootRange_config']['hitpoint_threshold']))
        self.ui[SETTING].score_precision_input.setText(str(1 / self.config['shootRange_config']['ST_height']))

        self.toPage(SETTING)
        self.homeBGV_player.off()

    def homePage_click_quit(self):
        sound_player('src/sound/clicked.wav', channel=5, auto_play=True)
        time.sleep(0.2)
        self.quitAll()

    # Records
    def Records_click_bt_back(self):
        sound_player('src/sound/clicked.wav', channel=5, auto_play=True)
        self.homeBGV_player.on()
        self.toPage(HOMEPAGE)

    # Setting
    def Setting_click_bt_back(self):
        sound_player('src/sound/clicked.wav', channel=5, auto_play=True)
        self.homeBGV_player.on()
        self.toPage(HOMEPAGE)

    def Setting_click_bt_apply(self):
        sound_player('src/sound/clicked.wav', channel=5, auto_play=True)

        self.config['sound_config']['fire_sound'] = self.ui[SETTING].fire_sound.isChecked()
        self.config['sound_config']['shell_sound'] = self.ui[SETTING].shell_sound.isChecked()
        self.config['sound_config']['hit_sound'] = self.ui[SETTING].hit_sound.isChecked()
        self.config['sound_config']['kill_sound'] = self.ui[SETTING].kill_sound.isChecked()

        self.config['shootRange_config']['tick'] = float(self.ui[SETTING].tick_input.text())
        self.config['shootRange_config']['hitpoint_threshold'] = int(self.ui[SETTING].threshold_input.text())
        self.config['shootRange_config']['ST_height'] = int(
            1 / float(self.ui[SETTING].score_precision_input.text()))
        cam_input = self.ui[SETTING].cam_input.text() if self.ui[
                                                             SETTING].cam_input.text() != '0' else 0

        if self.config['shootRange_config']['camera'] != cam_input or self.camera_valid is False:
            cap = cv2.VideoCapture(cam_input)
            self.camera_valid, frame = cap.read()
            if self.camera_valid:
                self.config['shootRange_config']['camera'] = cam_input
            cap.release()
        self.setUItext(self.ui[SETTING].bt_apply, '应用完成' if self.camera_valid else '摄像头无效')

        with open('src/config/config.json', 'w') as json_file:
            json.dump(self.config, json_file)

    # Calibrate
    def Calibrate_click_bt_back(self):
        sound_player('src/sound/clicked.wav', channel=5, auto_play=True)
        self.homeBGV_player.on()
        self.toPage(HOMEPAGE)

    # StartMode
    def StartMode_click_bt_back(self):
        sound_player('src/sound/clicked.wav', channel=5, auto_play=True)
        self.toPage(HOMEPAGE)
        self.homeBGV_player.on()

    def StartMode_click_bt_Model1(self):
        if self.camera_valid:
            sound_player('src/sound/clicked.wav', channel=5, auto_play=True)
            self.toPage(PLAYPAGE)
            self.core_player.on(sr=ShootingRange(config=self.config['shootRange_config']),
                                sound_config=self.config['sound_config'])
        else:
            QMessageBox.information(self, '摄像头无效', '请到[设置]界面设置摄像头', QMessageBox.Yes)

    def StartMode_click_bt_Model2(self):
        if self.camera_valid:
            sound_player('src/sound/hover.wav', channel=5, auto_play=True)
        else:
            QMessageBox.information(self, '摄像头无效', '请到[设置]界面设置摄像头', QMessageBox.Yes)

    def StartMode_click_bt_Model3(self):
        if self.camera_valid:
            sound_player('src/sound/hover.wav', channel=5, auto_play=True)
        else:
            QMessageBox.information(self, '摄像头无效', '请到[设置]界面设置摄像头', QMessageBox.Yes)

    # PlayPage
    def PlayPage_click_bt_back(self):
        sound_player('src/sound/clicked.wav', channel=5, auto_play=True)
        self.homeBGV_player.on()
        self.toPage(HOMEPAGE)
        self.core_player.off()

    def PlayPage_click_bt_reset(self):
        sound_player('src/sound/clear.wav', channel=5, auto_play=True)
        self.core_player.sr.clear_data()
        self.setUItext(self.ui[PLAYPAGE].bt_reset, '已重置')

    def PlayPage_click_bt_save(self):
        sound_player('src/sound/save.wav', channel=5, auto_play=True)
        ret = self.core_player.sr.save_data(mode=1)
        self.setUItext(self.ui[PLAYPAGE].bt_save, '保存成功')
    def play_bgm_thread_target(self):
        pygame.mixer.init()
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(f'src/sound\\bgm.wav'), -1)
        while True:
            time.sleep(0.05)
            if self.kill_BGM:
                pygame.mixer.Channel(0).stop()
                return

    def setUItext_target(self, ui: QPushButton, text):
        oriText = ui.text()
        ui.setText(text)
        time.sleep(0.5)
        ui.setText('')
        time.sleep(0.07)
        ui.setText(text)
        time.sleep(0.07)
        ui.setText('')
        time.sleep(0.07)

        ui.setText(str(oriText))

    def quitAll(self):
        QCoreApplication.instance().quit()
        self.bgm_player.off()
        self.homeBGV_player.off()
        self.core_player.off()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = SR_GUI()
    window.show()
    sys.exit(app.exec_())
