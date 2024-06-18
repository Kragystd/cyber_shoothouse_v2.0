# -*- coding: utf-8 -*-
# @Time    : 2023/6/9 10:56
# @Author  : Kragy
# @File    : 1.py
import json
import math
import os
import random
import threading
import time
from datetime import datetime

import cv2
import numpy as np
import pygame

import gc


class ShootingRange:
    """
    核心功能，初始化需要摄像头id或网络摄像头地址，分数靶子路径。
    """

    def __init__(self, config):

        # 配置参数
        # "hitpoint_threshold": 命中点颜色容差系数
        # "tick": 设计判定间隔时间(单位：秒)
        # "ST_height":分数分布靶高度(倒数为平面识别精度)
        # "ST_width": 分数分布靶宽度
        # "mute": 全局静音
        # "sound_effect":  使用音效
        # "bgm": 使用bgm
        # "camera": 摄像头id
        # "vt_path": 虚拟靶路径
        # "st_path": 分数靶路径
        self.config = config

        # 静态资源
        self.color_range = {'red1': [(0, 43, 46), (10, 255, 255)],
                            'red2': [(156, 43, 46), (180, 255, 255)],
                            'green': [(35, 43, 46), (77, 255, 255)],
                            'blue': [(100, 43, 46), (124, 255, 255)],
                            'white': [(0, 0, 221), (180, 30, 255)]
                            }  # 颜色字典
        self.sound_num_dict = self.sound_num_dict_load()  # 随即声效数量字典
        self.score_target, self.virtual_target = self.score_target_load(self.config['st_path'])  # 分数分布靶
        self.cap = cv2.VideoCapture(self.config['camera'])  # 视频捕获流

        # 动态资源
        self.last_shoot_time = 0  # 上次射击时间
        self.hitpointScore_list = []  # 命中点列表
        self.hitmark = np.empty((self.config['ST_height'], self.config['ST_width'], 3)).astype(np.uint8)  # 命中标记图

        # 当前状态
        self.current_cam_marked = None
        self.current_real_target_marked = None
        self.current_hitpoint = None
        self.current_score = 0
        self.current_count = 0
        self.current_accuracy = 0
        self.current_avgscore = 0
        self.current_headshotRate = 0

    def getCurrentData(self):
        ret, frame = self.cap.read()
        if ret:
            self.process_frame(frame)
        return [self.current_cam_marked,
                self.current_real_target_marked,
                self.current_hitpoint,
                self.current_score,
                self.current_count,
                self.current_accuracy,
                self.current_avgscore,
                self.current_headshotRate]

    def process_frame(self, frame):
        real_target = self.real_target_locate(frame)
        if real_target is not None:
            # 显示定位点描边的摄像头捕获的画面
            if time.time() > self.last_shoot_time + self.config['tick']:
                # 检测命中点
                self.hitpoint_detect(real_target)

            self.real_target_display(real_target)

    def real_target_locate(self, src):
        """
        定位图像中的靶子
        :param src: 源图像
        """
        # 获取帧大小
        w = src.shape[0]
        h = src.shape[1]

        # 获取绿色部分的二值图像
        target_area_bin = self.get_area_by_color(src, 'green')

        centers, contours = self.area_locate(target_area_bin)

        cam_marked = np.copy(src)
        if contours is not None:
            for i in contours:
                cv2.drawContours(cam_marked, i, -1, (255, 0, 0), 3)
        self.current_cam_marked = cam_marked

        if len(centers) != 4:
            return None
        # 对找到的四个定位点进行排序
        centers_sorted = sorted(centers, key=lambda tup: tup[0])
        centers_sorted_l = sorted(centers_sorted[0:2], key=lambda tup: tup[1])
        centers_sorted_r = sorted(centers_sorted[2:], key=lambda tup: tup[1])
        centers_sorted_l.extend(centers_sorted_r)
        centers = centers_sorted_l

        # 获取透视变换矩阵M
        pos_src = np.array(centers, dtype="float32")
        pos_dst = np.array([[0, 0], [self.config['ST_height'], 0], [0, self.config['ST_width']],
                            [self.config['ST_height'], self.config['ST_width']]],
                           dtype="float32")
        M = cv2.getPerspectiveTransform(pos_src, pos_dst)

        real_target = cv2.warpPerspective(src, M, (self.config['ST_height'], self.config['ST_width']))
        RM = cv2.getRotationMatrix2D((self.config['ST_width'] // 2, self.config['ST_width'] // 2), -90, 1)
        real_target = cv2.warpAffine(real_target, RM, (self.config['ST_width'], self.config['ST_height']))
        real_target = cv2.flip(real_target, 1)
        return real_target

    def get_area_by_color(self, img, color, erode=1):
        """
        获取指定颜色的二值图像
        :param img:源图像
        :param color: 要提取的颜色
        :param erode:是否进行erode
        :return:所提取颜色的二值图像
        """
        # 依次对帧进行Gaussian_blur、BGR_2_HSV、get_green_area
        img_gs = cv2.GaussianBlur(img, (5, 5), 0)
        img_gs_hsv = cv2.cvtColor(img_gs, cv2.COLOR_BGR2HSV)
        img_gs_hsv_color = cv2.inRange(img_gs_hsv, self.color_range[color][0], self.color_range[color][1])
        if erode == 0:
            return img_gs_hsv_color
        img_gs_hsv_color_erode = cv2.erode(img_gs_hsv_color, None, iterations=3)
        return img_gs_hsv_color_erode

    def area_locate(self, area_bin):
        """
        :param area_bin: 某颜色的二值图像
        :return: 区域中心点坐标列表和边界点坐标列表
        """
        # 获取区域的轮廓
        image, contours, hierarchy = cv2.findContours(area_bin, cv2.RETR_TREE,
                                                      cv2.CHAIN_APPROX_SIMPLE)

        # 获取区域中心点列表
        centers = []
        for con in contours:
            M = cv2.moments(con)
            if M['m00'] != 0:
                center_x = int(M['m10'] / M['m00'])
                center_y = int(M['m01'] / M['m00'])
                centers.append((center_x, center_y))

        return centers, contours

    def hitpoint_detect(self, frame):
        """
        命中检测
        :param frame: 当前帧
        :return:
        """

        hitpoint = self.get_area_by_color(frame, 'red2', erode=0)
        images, hitpoint_contours, hierarchy = cv2.findContours(hitpoint, cv2.RETR_TREE,
                                                                cv2.CHAIN_APPROX_SIMPLE)

        for hp_contour in hitpoint_contours:
            if cv2.contourArea(hp_contour) > self.config['hitpoint_threshold']:
                M = cv2.moments(hp_contour)
                if M['m00'] != 0:
                    self.current_hitpoint = (int(M['m10'] / M['m00']),
                                             int(M['m01'] / M['m00']))

                    self.last_shoot_time = time.time()
                    self.hit_feedback(self.current_hitpoint)
                    return

    def hit_feedback(self, hitpoint: tuple):
        self.current_score = self.score_target[hitpoint[1], hitpoint[0]] * 10
        self.sound_back(self.current_score)
        self.hitpointScore_list.append((hitpoint, self.current_score))
        self.culculateGrade()

    def real_target_display(self, frame):
        if len(self.hitpointScore_list) != 0:
            cv2.putText(self.hitmark, 'x', (self.current_hitpoint[0] - 2, self.current_hitpoint[1] - 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(self.hitmark, format(self.current_score, "0.2f"),
                        (self.current_hitpoint[0] + 10, self.current_hitpoint[1] + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (1, 1, 1), 2, cv2.LINE_AA)
            hitmark_mask = np.array(self.hitmark, dtype=bool)
            frame = frame * ~hitmark_mask + self.hitmark * hitmark_mask

        self.current_real_target_marked = frame

    def score_target_load(self, st_path: str, vt_path: str = './imgs/st.png'):
        st_raw = cv2.imread(st_path)
        self.config['ST_width'] = int(self.config['ST_height'] * st_raw.shape[1] / st_raw.shape[0])
        st_raw = cv2.resize(st_raw, (self.config['ST_width'], self.config['ST_height']))
        vt_raw_hsv = cv2.cvtColor(st_raw, cv2.COLOR_BGR2HSV)
        tmp_score_target = []
        for i in vt_raw_hsv:
            vt_row = []
            for j in i:
                vt_row.append((j[2]) / 255)
            tmp_score_target.append(vt_row)

        virtual_target = cv2.imread(vt_path)
        virtual_target = cv2.resize(virtual_target, (self.config['ST_width'], self.config['ST_height']))
        return np.array(tmp_score_target), virtual_target

    def sound_num_dict_load(self):
        sound_filename_list = os.listdir('../sound')
        hit_real = len([i for i in sound_filename_list if i.startswith('hit_real')])
        shell_fall = len([i for i in sound_filename_list if i.startswith('shell_fall')])
        hit_feedback = len([i for i in sound_filename_list if i.startswith('hit_feedback')])
        return {'hit_real': hit_real,
                'shell_fall': shell_fall,
                'hit_feedback': hit_feedback
                }

    def culculateGrade(self):
        if len(self.hitpointScore_list) == 0:
            return
        self.current_count = len(self.hitpointScore_list)
        self.current_accuracy = (self.current_accuracy * (len(self.hitpointScore_list) - 1) +
                                 int(self.current_score != 0)) / len(self.hitpointScore_list)
        self.current_avgscore = (self.current_avgscore * (len(self.hitpointScore_list) - 1) + self.current_score) / len(
            self.hitpointScore_list)
        self.current_headshotRate = (self.current_headshotRate * (len(self.hitpointScore_list) - 1) +
                                     int(self.current_score > 8)) / len(self.hitpointScore_list)

    def play_hit_sound_thread_target(self, score):
        pygame.mixer.init()
        pygame.mixer.Channel(1).play(
            pygame.mixer.Sound(f'sound\hit_real{math.floor(self.sound_num_dict["hit_real"] * random.random())}.wav'))
        time.sleep(0.15)
        if score > 0 and score < 6:
            pygame.mixer.Channel(2).play(
                pygame.mixer.Sound(
                    f'sound/hit_feedback{math.floor(self.sound_num_dict["hit_feedback"] * random.random())}.wav'))
        elif score >= 6 and score < 8:
            pygame.mixer.Channel(2).play(
                pygame.mixer.Sound(f'../sound/kill0.wav'))
        elif score >= 8:
            pygame.mixer.Channel(2).play(
                pygame.mixer.Sound(f'../sound/headshot0.wav'))
        time.sleep(0.2)
        pygame.mixer.Channel(3).play(
            pygame.mixer.Sound(
                f'sound\shell_fall{math.floor(self.sound_num_dict["shell_fall"] * random.random())}.wav'))
        return

    def sound_back(self, score):
        play_sound_thread = threading.Thread(target=self.play_hit_sound_thread_target, args=(score,))
        play_sound_thread.start()

    def clear_data(self):
        self.hitpointScore_list = []
        self.hitmark = np.empty((self.config['ST_height'], self.config['ST_width'], 3)).astype(np.uint8)

        self.current_cam_marked = None
        self.current_real_target_marked = None
        self.current_hitpoint = None
        self.current_score = 0
        self.current_count = 0
        self.current_accuracy = 0
        self.current_avgscore = 0
        self.current_headshotRate = 0

    def save_data(self, mode=0, vt=None):
        if mode == 1:
            if self.current_real_target_marked is None:
                return False
            cv2.imwrite(f'./records/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S_real_target.png")}',
                        self.current_real_target_marked)
            return
        hitmark_mask = np.array(self.hitmark, dtype=bool)
        if mode == 2:
            img = self.virtual_target * ~hitmark_mask + self.hitmark * hitmark_mask
        if mode == 3 and vt != None:
            img = vt * ~hitmark_mask + self.hitmark * hitmark_mask

        cv2.imwrite(f'./records/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S_virtual_target.png")}', img)
        return True


if __name__ == '__main__':
    sr = ShootingRange('http://192.168.137.207:4747/video', 'imgs/st.png')
    while True:
        frameData = sr.getCurrentData()
        if frameData[0] is not None:
            cv2.imshow('cam', frameData[0])
            if frameData[1] is not None:
                cv2.imshow('target', frameData[1])
        cv2.waitKey(1)
        print(frameData[4], sr.hitpointScore_list)
