# -*- coding: utf-8 -*-
# @Time    : 2023/6/9 10:56
# @Author  : Kragy
# @File    : 1.py

import math
import random
import threading
import time

import cv2
import numpy as np
import pygame


class ShootingRange:
    """
    核心功能，初始化需要摄像头id或网络摄像头地址，分数靶子路径。
    """

    def __init__(self, cam, score_target_path):
        self.color_range = {
            'red1': [(0, 43, 46), (10, 255, 255)],
            'red2': [(156, 43, 46), (180, 255, 255)],
            'green': [(35, 43, 46), (77, 255, 255)],
            'blue': [(100, 43, 46), (124, 255, 255)],
            'white': [(0, 0, 221), (180, 30, 255)]
        }  # 颜色字典

        self.hitpoint_threshode = 20  # 命中点阈值
        self.last_shoot_time = 0  # 上次射击时间
        self.tick = 0.2  # 设计判定间隔
        self.hitpointScore_list = []  # 命中点列表

        self.ST_width = 0  # 分数分布靶宽度
        self.ST_height = 1000  # 分数分布靶高度
        self.score_target = self.score_target_load(score_target_path)  # 分数分布靶
        self.no_img = cv2.cvtColor(cv2.imread('../imgs/no_img.jpg'), cv2.COLOR_BGR2RGB)
        self.dataFrame = [None, None, None, None, None]
        self.cap = cv2.VideoCapture(cam)  # 视频捕获流

    def getCurrentData(self):
        ret, frame = self.cap.read()
        result = [self.no_img, self.no_img, 'None', 'None']
        if ret:
            result = self.process_frame(frame)
            if result[0] == 'cam_marked_is_None':
                result[0] = frame
        time.sleep(0.01)
        return result

    def process_frame(self, frame):
        cam_marked, real_target = self.real_target_locate(frame)
        hitpoint = 'None'
        score = 'None'
        if real_target is not None:
            # 显示定位点描边的摄像头捕获的画面
            if time.time() > self.last_shoot_time + self.tick:
                # 检测命中点
                hitpoint, score = self.hitpoint_detect(real_target)

        real_target_display = self.real_target_display(real_target)
        accuracy, avgscore, headshotRate = self.getGrade()
        return ['cam_marked_is_None' if cam_marked is None else cam_marked,
                real_target_display,
                hitpoint,
                score,
                accuracy,
                avgscore,
                headshotRate]

    def real_target_locate(self, src):
        """
        定位图像中的靶子
        :param src: 源图像
        :return: cam:定位点描边的源图像
        :return: real_target:真实靶子的图像
        """
        # 获取帧大小
        w = src.shape[0]
        h = src.shape[1]

        # 获取绿色部分的二值图像
        target_area_bin = self.get_area_by_color(src, 'green')

        centers, contours = self.area_locate(target_area_bin)

        cam = np.copy(src)
        if contours is not None:
            for i in contours:
                cv2.drawContours(cam, i, -1, (255, 0, 0), 3)

        if len(centers) != 4:
            return None, None
        # 对找到的四个定位点进行排序
        centers_sorted = sorted(centers, key=lambda tup: tup[0])
        centers_sorted_l = sorted(centers_sorted[0:2], key=lambda tup: tup[1])
        centers_sorted_r = sorted(centers_sorted[2:], key=lambda tup: tup[1])
        centers_sorted_l.extend(centers_sorted_r)
        centers = centers_sorted_l

        # 获取透视变换矩阵M
        pos_src = np.array(centers, dtype="float32")
        pos_dst = np.array([[0, 0], [self.ST_height, 0], [0, self.ST_width], [self.ST_height, self.ST_width]],
                           dtype="float32")
        M = cv2.getPerspectiveTransform(pos_src, pos_dst)

        real_target = cv2.warpPerspective(src, M, (self.ST_height, self.ST_width))
        RM = cv2.getRotationMatrix2D((self.ST_width // 2, self.ST_width // 2), -90, 1)
        real_target = cv2.warpAffine(real_target, RM, (self.ST_width, self.ST_height))
        real_target = cv2.flip(real_target, 1)
        return cam, real_target

    def get_area_by_color(self, img, color, no_erode=0):
        """
        获取指定颜色的二值图像
        :param img:源图像
        :param color: 要提取的颜色
        :param no_erode:是否关闭erode
        :return:所提取颜色的二值图像
        """
        # 依次对帧进行Gaussian_blur、BGR_2_HSV、get_green_area
        img_gs = cv2.GaussianBlur(img, (5, 5), 0)
        img_gs_hsv = cv2.cvtColor(img_gs, cv2.COLOR_BGR2HSV)
        img_gs_hsv_color = cv2.inRange(img_gs_hsv, self.color_range[color][0], self.color_range[color][1])
        img_gs_hsv_color_erode = cv2.erode(img_gs_hsv_color, None, iterations=3)
        # kernel = np.ones((5, 5), np.uint8)
        # img_gs_hsv_color_erode_open = cv2.morphologyEx(img_gs_hsv_color_erode, cv2.MORPH_OPEN, kernel, iterations=3)
        if no_erode == 1:
            return img_gs_hsv_color
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

        hitpoint = self.get_area_by_color(frame, 'red2', no_erode=1)
        images, hitpoint_contours, hierarchy = cv2.findContours(hitpoint, cv2.RETR_TREE,
                                                                cv2.CHAIN_APPROX_SIMPLE)

        for hp_contour in hitpoint_contours:
            if cv2.contourArea(hp_contour) > self.hitpoint_threshode:
                M = cv2.moments(hp_contour)
                if M['m00'] != 0:
                    center_x = int(M['m10'] / M['m00'])
                    center_y = int(M['m01'] / M['m00'])

                    self.last_shoot_time = time.time()
                    return self.hit_feedback((center_x, center_y))
        return 'None', 'None'

    def hit_feedback(self, hitpoint: tuple):
        score = self.score_target[hitpoint[1], hitpoint[0]] * 10
        # sound_back(score)
        self.hitpointScore_list.append((hitpoint, score))
        return hitpoint, score

    def real_target_display(self, frame):
        for pos in self.hitpointScore_list:
            # cv2.circle(frame, pos, 7, (0, 0, 0), -1)
            cv2.putText(frame, 'x', (pos[0][0] - 2, pos[0][1] - 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                        cv2.LINE_AA)
            cv2.putText(frame, f'{format(pos[1], "0.2f")}', (pos[0][0] + 5, pos[0][1] + 5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 0), 2,
                        cv2.LINE_AA)
        return frame if frame is not None else self.no_img

    def score_target_load(self, vt_path: str):
        vt_raw = cv2.imread(vt_path)
        self.ST_width = int(self.ST_height * vt_raw.shape[1] / vt_raw.shape[0])
        vt_raw = cv2.resize(vt_raw, (self.ST_width, self.ST_height))
        vt_raw_hsv = cv2.cvtColor(vt_raw, cv2.COLOR_BGR2HSV)
        tmp_score_target = []
        for i in vt_raw_hsv:
            vt_row = []
            for j in i:
                vt_row.append((j[2]) / 255)
            tmp_score_target.append(vt_row)
        return np.array(tmp_score_target)

    def getGrade(self):
        if len(self.hitpointScore_list) == 0:
            return 'None', 'None', 'None'
        accuracy = 0
        avgscore = 0
        headshotRate = 0
        for i in self.hitpointScore_list:
            if i[1] != 0:
                accuracy += 1
                avgscore += i[1]
                if i[1] > 8:
                    headshotRate += 1

        accuracy /= len(self.hitpointScore_list)
        avgscore /= len(self.hitpointScore_list)
        headshotRate /= len(self.hitpointScore_list)
        return accuracy, avgscore, headshotRate


if __name__ == '__main__':
    sr = ShootingRange(0, '../imgs/st.png')
    while True:
        frameData = sr.getCurrentData()
        print(frameData)
        cv2.imshow('cam', frameData[0])
        cv2.imshow('target', frameData[1])
        cv2.waitKey(10)
