# -*- coding: utf-8 -*-
# @Time    : 2023/6/9 10:56
# @Author  : Kragy
# @File    : 1.py
"""
核心功能模块
针对激光教学枪械，编写了基于opencv图像识别的打靶程序。通过标靶上的定位点检测摄像头捕获画面中的标靶，并通过颜色识别打到标靶上的激光，定位其位置来获取分数。
"""
import json
import time
from datetime import datetime
import cv2
import numpy as np


class ShootingRange:
    """
    核心功能，通过opencv调用摄像头，识别标靶并进行射击判定
    """

    def __init__(self, config):
        """
        ShootingRange构造函数，初始化各项参数
        :param config: 配置参数
        """
        # 配置参数
        # "hitpoint_threshold": 命中点颜色容差系数
        # "tick": 设计判定间隔时间(单位：秒)
        # "ST_height":分数分布靶高度(倒数为平面识别精度)
        # "ST_width": 分数分布靶宽度
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
        self.score_target, self.virtual_target = self.st_and_vt_load(self.config['st_path'],
                                                                     self.config['vt_path'])  # 分数分布靶 虚拟靶标
        self.cap = cv2.VideoCapture(self.config['camera'])  # 视频捕获流

        # 动态资源
        self.last_shoot_time = 0  # 上次射击时间
        self.hitpointScore_list = []  # 命中点列表
        self.hitmark = np.empty((self.config['ST_height'], self.config['ST_width'], 3)).astype(np.uint8)  # 命中标记图

        # 当前状态
        self.current_cam_marked = None  # 当前标注了可能的定位点轮廓的摄像头捕获的画面(下称标记后的摄像头画面)
        self.current_real_target_marked = None  # 当前标注了所有命中点的实际标靶画面(下称标记后的实际标靶画面)
        self.current_hitpoint = None  # 当前命中点
        self.current_score = None  # 当前分数
        self.current_count = 0  # 当前技术
        self.current_accuracy = 0  # 当前准确率
        self.current_avgscore = 0  # 当前平均分
        self.current_headshotRate = 0  # 当前爆头率

    def getCurrentData(self):
        """
        捕获并处理一帧，返回当前状态数据
        :return:当前状态数据
        """
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
        """
        处理帧，首先定位实际标靶,如果定位成功则按照tick进行命中点检测,最后对检测到的标靶图像进行标记
        :param frame: 待处理的帧
        """
        self.current_hitpoint = None  # 更新当前命中点
        self.current_score = None  # 更新当前分数

        real_target = self.real_target_locate(frame)  # 定位实际标靶
        if real_target is not None:
            # 显示定位点描边的摄像头捕获的画面
            if time.time() > self.last_shoot_time + self.config['tick']:
                self.hitpoint_detect(real_target)  # 检测命中点

            self.mark_real_target(real_target)  # 标记标靶图像

    def real_target_locate(self, src):
        """
        定位图像中的标靶，通过标靶上的定位点进行检测,经过图像变换得到实际标靶图像：检测到四个定位点，以其为基准进行基本变换和透视变换，返回变换后的实际标靶图像
        :param src: 源图像
        :return real_target: 变换后的实际标靶图像
        """
        # 获取帧大小
        w = src.shape[0]
        h = src.shape[1]

        target_area_bin = self.get_area_by_color(src, 'green')  # 获取绿色部分的二值图像
        centers, contours = self.area_locate(target_area_bin)  # 获取连续的绿色区域的边界和中心点

        cam_marked = np.copy(src)  # 创建标记后的摄像头图像

        # 对摄像头图像进行标记,画出可能的定位点轮廓,以便用户进行机位和靶位调整
        if contours is not None:
            for i in contours:
                cv2.drawContours(cam_marked, i, -1, (255, 0, 0), 3)  # 画出可能的定位点轮廓
        self.current_cam_marked = cam_marked  # 更新当前标记后的摄像头画面

        # 尝试根据4个定位点进行实际标靶定位
        if len(centers) != 4:
            return None
        # #对找到的4个定位点进行排序,以定位实际标靶
        centers_sorted = sorted(centers, key=lambda tup: tup[0])
        centers_sorted_l = sorted(centers_sorted[0:2], key=lambda tup: tup[1])
        centers_sorted_r = sorted(centers_sorted[2:], key=lambda tup: tup[1])
        centers_sorted_l.extend(centers_sorted_r)
        centers = centers_sorted_l
        # #对实际标靶图像透视变换
        # ##获取透视变换矩阵M
        pos_src = np.array(centers, dtype="float32")
        pos_dst = np.array([[0, 0], [self.config['ST_height'], 0], [0, self.config['ST_width']],
                            [self.config['ST_height'], self.config['ST_width']]],
                           dtype="float32")
        # ##进行基本变换,使其图像与分数标靶尺寸相同,以便得分映射
        M = cv2.getPerspectiveTransform(pos_src, pos_dst)
        real_target = cv2.warpPerspective(src, M, (self.config['ST_height'], self.config['ST_width']))
        RM = cv2.getRotationMatrix2D((self.config['ST_width'] // 2, self.config['ST_width'] // 2), -90, 1)

        # ##进行透视变换,校正其透视偏差
        real_target = cv2.warpAffine(real_target, RM, (self.config['ST_width'], self.config['ST_height']))
        real_target = cv2.flip(real_target, 1)

        return real_target

    def get_area_by_color(self, img, color, erode=1):
        """
        获取指定颜色的遮罩图像
        :param img:源图像
        :param color: 要提取的颜色
        :param erode:是否进行erode
        :return:所提取颜色的二值图像
        """
        img_gs = cv2.GaussianBlur(img, (5, 5), 0)  # 高斯模糊
        img_gs_hsv = cv2.cvtColor(img_gs, cv2.COLOR_BGR2HSV)  # 更改颜色模式为HSV模式

        img_gs_hsv_color = cv2.inRange(img_gs_hsv, self.color_range[color][0],
                                       self.color_range[color][1])  # 选定指定范围内的图像遮罩
        # 进行图像腐蚀，减少噪点
        if erode == 0:
            return img_gs_hsv_color
        img_gs_hsv_color_erode = cv2.erode(img_gs_hsv_color, None, iterations=3)
        return img_gs_hsv_color_erode

    def area_locate(self, area_mask):
        """
        根据这招图像求连续区域中心点坐标列表和边界点坐标列表
        :param area_mask: 某颜色的遮罩图像
        :return: 区域中心点坐标列表和边界点坐标列表
        """
        # 获取区域的轮廓contours
        image, contours, hierarchy = cv2.findContours(area_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # 获取区域中心点列表centers
        centers = []
        for con in contours:
            M = cv2.moments(con)  # 连续区域的矩
            if M['m00'] != 0:
                # 计算区域中心坐标
                center_x = int(M['m10'] / M['m00'])
                center_y = int(M['m01'] / M['m00'])
                centers.append((center_x, center_y))

        return centers, contours

    def hitpoint_detect(self, frame):
        """
        命中点检测
        :param frame: 当前帧
        """
        # 这里将area_locate函数展开重写，以便高效地进行命中反馈
        hitpoint = self.get_area_by_color(frame, 'red2', erode=0)  # 获取红色区域
        images, hitpoint_contours, hierarchy = cv2.findContours(hitpoint, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for hp_contour in hitpoint_contours:
            if cv2.contourArea(hp_contour) > self.config['hitpoint_threshold']:
                M = cv2.moments(hp_contour)
                if M['m00'] != 0:
                    self.current_hitpoint = (int(M['m10'] / M['m00']),
                                             int(M['m01'] / M['m00']))  # 更新当前命中点

                    self.last_shoot_time = time.time()  # 记录本次命中时间
                    self.hit_feedback(self.current_hitpoint)  # 进行命中反馈
                    return

    def hit_feedback(self, hitpoint: tuple):
        """
        根据命中点进行反馈
        :param hitpoint:
        """
        self.current_score = self.score_target[hitpoint[1], hitpoint[0]] * 10  # 通过st_target进行映射并更新当前分数
        self.hitpointScore_list.append((hitpoint, self.current_score))  # 将命中点和分数存入列表
        self.culculateGrade()  # 计算当前成绩数据

    def mark_real_target(self, frame):
        """
        将命中点标记到实际标靶画面。
        :param frame:待处理画面
        """

        # 将命中点分数列表最后一个元素添加到命中标记图
        if len(self.hitpointScore_list) != 0:
            cv2.putText(self.hitmark, 'x',
                        (self.hitpointScore_list[-1][0][0] - 2, self.hitpointScore_list[-1][0][1] - 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(self.hitmark, format(self.hitpointScore_list[-1][1], "0.2f"),
                        (self.hitpointScore_list[-1][0][0] + 10, self.hitpointScore_list[-1][0][1] + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (1, 1, 1), 2, cv2.LINE_AA)

            # 图像覆盖运算
            hitmark_mask = np.array(self.hitmark, dtype=bool)  # 命中标记图的遮罩
            frame = frame * ~hitmark_mask + self.hitmark * hitmark_mask

        self.current_real_target_marked = frame

    def st_and_vt_load(self, st_path, vt_path):
        """
        加载分数分布靶和虚拟靶标
        :param st_path: 分数分布靶路径
        :param vt_path: 虚拟靶标路径
        :return: 分数分布靶和虚拟靶标（ndarray）
        """
        # 加载分数分布靶
        st_raw = cv2.imread(st_path)
        self.config['ST_width'] = int(self.config['ST_height'] * st_raw.shape[1] / st_raw.shape[0])  # 计算虚拟靶标宽度并应用到对象
        st_raw = cv2.resize(st_raw, (self.config['ST_width'], self.config['ST_height']))  # 重设分数靶标大小
        vt_raw_hsv = cv2.cvtColor(st_raw, cv2.COLOR_BGR2HSV)  # 转换颜色模式为HSV

        # 将灰度值转换为分数
        tmp_score_target = []
        for i in vt_raw_hsv:
            vt_row = []
            for j in i:
                vt_row.append((j[2]) / 255)
            tmp_score_target.append(vt_row)

        # 加载虚拟靶标
        virtual_target = cv2.imread(vt_path)
        virtual_target = cv2.resize(virtual_target, (self.config['ST_width'], self.config['ST_height']))  # 重设分数靶标大小
        return np.array(tmp_score_target), virtual_target

    def culculateGrade(self):
        """
        计算并更新成绩数据。优化后无需遍历命中点分数列表。
        """
        if len(self.hitpointScore_list) == 0:
            return
        self.current_count = len(self.hitpointScore_list)
        self.current_accuracy = (self.current_accuracy * (len(self.hitpointScore_list) - 1) +
                                 int(self.current_score != 0)) / len(self.hitpointScore_list)
        self.current_avgscore = (self.current_avgscore * (len(self.hitpointScore_list) - 1) + self.current_score) / len(
            self.hitpointScore_list)
        self.current_headshotRate = (self.current_headshotRate * (len(self.hitpointScore_list) - 1) +
                                     int(self.current_score > 8)) / len(self.hitpointScore_list)

    def clear_data(self):
        """
        清空当前数据
        """
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

    def save_data(self, mode=1, customed_img=None):
        """
        保存当前数据
        :param mode: 保存模式：
                            1.保存实际标靶画面
                            2.保存标记后的虚拟标靶
                            3.保存标记后的自定义图片
        :param customed_img:自定义图片
        :return:是否保存成功
        """
        if mode == 1:
            if self.current_real_target_marked is None:
                return False
            cv2.imwrite(f'./records/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S_real_target.png")}',
                        self.current_real_target_marked)
            return False
        hitmark_mask = np.array(self.hitmark, dtype=bool)
        if mode == 2:
            img = self.virtual_target * ~hitmark_mask + self.hitmark * hitmark_mask
        if mode == 3 and customed_img != None:
            customed_img = cv2.resize(customed_img, (self.config['ST_width'], self.config['ST_height']))
            img = customed_img * ~hitmark_mask + self.hitmark * hitmark_mask

        cv2.imwrite(f'./records/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S_virtual_target.png")}', img)
        return True

if __name__ == '__main__':
    with open('src/config/config.json', encoding='utf-8') as json_file:
        config = json.load(json_file)['shootRange_config']
    sr = ShootingRange(config)
    while True:
        frameData = sr.getCurrentData()
        if frameData[0] is not None:
            cv2.imshow('cam', frameData[0])
            if frameData[1] is not None:
                cv2.imshow('target', frameData[1])
        cv2.waitKey(1)

