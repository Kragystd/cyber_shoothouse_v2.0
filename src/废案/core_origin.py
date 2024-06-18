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

score_target = None  # 虚拟靶子
ST_height = 1000
ST_width = 0

COLOR_RANGE = {
    'red1': [(0, 43, 46), (10, 255, 255)],
    'red2': [(156, 43, 46), (180, 255, 255)],
    'green': [(35, 43, 46), (77, 255, 255)],
    'blue': [(100, 43, 46), (124, 255, 255)],
    'white': [(0, 0, 221), (180, 30, 255)]
}  # 颜色字典

HP_THRESHODE = 40  # 命中点阈值

last_shoot_time = 0  # 上次射击时间
tick = 0.2  # 设计判定间隔

# 不同音效数量
SOUND_NUM_HIT_FEEDBACK = 1
SOUND_NUM_HIT_REAL = 6
SOUND_NUM_SHELL_FALL = 3

hitpoint_list = []  # 命中点列表


def set_windows():
    cv2.namedWindow("frame", cv2.WINDOW_KEEPRATIO)
    cv2.moveWindow('frame', 0, 0)


def play_bgm_thread_target():
    pygame.mixer.init()
    while True:
        pygame.mixer.Channel(3).play(pygame.mixer.Sound(f'../sound/bgm.wav'))
        time.sleep(150)


def play_hit_sound_thread_target(score):
    pygame.mixer.init()
    pygame.mixer.Channel(0).play(
        pygame.mixer.Sound(f'src/sound\hit_real{math.floor(SOUND_NUM_HIT_REAL * random.random())}.wav'))
    time.sleep(0.15)
    if score > 0 and score < 6:
        pygame.mixer.Channel(1).play(
            pygame.mixer.Sound(f'src/sound/hit_feedback{math.floor(SOUND_NUM_HIT_FEEDBACK * random.random())}.wav'))
    elif score >= 6 and score < 8:
        pygame.mixer.Channel(1).play(
            pygame.mixer.Sound(f'../sound/kill0.wav'))
    elif score >= 8:
        pygame.mixer.Channel(1).play(
            pygame.mixer.Sound(f'../sound/headshot0.wav'))
    time.sleep(0.2)
    pygame.mixer.Channel(2).play(
        pygame.mixer.Sound(f'src/sound\shell_fall{math.floor(SOUND_NUM_SHELL_FALL * random.random())}.wav'))


def sound_back(score):
    play_sound_thread = threading.Thread(target=play_hit_sound_thread_target, args=(score,))
    play_sound_thread.start()


def get_area_by_color(img, color, no_erode=0):
    """

    :param img:源图像
    :param color: 要提取的颜色
    :param no_erode:是否关闭erode
    :return:所提取颜色的二值图像
    """
    # 依次对帧进行Gaussian_blur、BGR_2_HSV、get_green_area
    img_gs = cv2.GaussianBlur(img, (5, 5), 0)
    img_gs_hsv = cv2.cvtColor(img_gs, cv2.COLOR_BGR2HSV)
    img_gs_hsv_color = cv2.inRange(img_gs_hsv, COLOR_RANGE[color][0], COLOR_RANGE[color][1])
    img_gs_hsv_color_erode = cv2.erode(img_gs_hsv_color, None, iterations=3)
    # kernel = np.ones((5, 5), np.uint8)
    # img_gs_hsv_color_erode_open = cv2.morphologyEx(img_gs_hsv_color_erode, cv2.MORPH_OPEN, kernel, iterations=3)
    if no_erode == 1:
        return img_gs_hsv_color
    cv2.imshow("1", img_gs_hsv_color_erode)
    return img_gs_hsv_color_erode


def area_locate(area_bin):
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


def virtual_target_load(vt_path: str):
    global score_target, ST_width

    vt_raw = cv2.imread(vt_path)
    ST_width = int(ST_height * vt_raw.shape[1] / vt_raw.shape[0])
    vt_raw = cv2.resize(vt_raw, (ST_width, ST_height))
    vt_raw_hsv = cv2.cvtColor(vt_raw, cv2.COLOR_BGR2HSV)
    score_target = []
    for i in vt_raw_hsv:
        vt_row = []
        for j in i:
            vt_row.append((j[2]) / 255)
        score_target.append(vt_row)
    score_target = np.array(score_target)


def real_target_locate(src):
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
    target_area_bin = get_area_by_color(src, 'green')

    centers, contours = area_locate(target_area_bin)

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
    pos_dst = np.array([[0, 0], [ST_height, 0], [0, ST_width], [ST_height, ST_width]], dtype="float32")
    M = cv2.getPerspectiveTransform(pos_src, pos_dst)

    real_target = cv2.warpPerspective(src, M, (ST_height, ST_width))
    RM = cv2.getRotationMatrix2D((ST_width // 2, ST_width // 2), -90, 1)
    real_target = cv2.warpAffine(real_target, RM, (ST_width, ST_height))
    real_target = cv2.flip(real_target, 1)
    return cam, real_target


def real_target_display(frame):
    global hitpoint
    for pos in hitpoint_list:
        # cv2.circle(frame, pos, 7, (0, 0, 0), -1)
        cv2.putText(frame, 'x', (pos[0][0] - 2, pos[0][1] - 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                    cv2.LINE_AA)
        cv2.putText(frame, f'{format(pos[1], "0.2f")}', (pos[0][0] + 5, pos[0][1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 0), 2,
                    cv2.LINE_AA)
    if frame is not None:
        cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord(' '):
        hitpoint_list.clear()


def hitpoint_detect(frame):
    """
    命中检测
    :param frame: 当前帧
    :return:
    """
    global last_shoot_time, hitpoint_list
    hitpoint = get_area_by_color(frame, 'red2', no_erode=1)
    images, hitpoint_contours, hierarchy = cv2.findContours(hitpoint, cv2.RETR_TREE,
                                                            cv2.CHAIN_APPROX_SIMPLE)

    for hp_contour in hitpoint_contours:
        if cv2.contourArea(hp_contour) > HP_THRESHODE:
            M = cv2.moments(hp_contour)
            if M['m00'] != 0:
                center_x = int(M['m10'] / M['m00'])
                center_y = int(M['m01'] / M['m00'])

                last_shoot_time = time.time()
                hit_feedback((center_x, center_y))
                break


def hit_feedback(hitpoint: tuple):
    score = score_target[hitpoint[1], hitpoint[0]] * 10
    sound_back(score)
    hitpoint_list.append((hitpoint, score))
    print(f'hitpoint: {hitpoint}')
    print(f'score: {score}')


def process_frame(frame):
    cam_marked, real_target = real_target_locate(frame)
    if real_target is not None:
        # 显示定位点描边的摄像头捕获的画面
        cv2.imshow('cam', cam_marked)
        if time.time() > last_shoot_time + tick:
            # 检测命中点
            hitpoint_detect(real_target)

    real_target_display(real_target)


def main():
    virtual_target_load('../imgs/st.png')
    set_windows()
    net_cam = 'http://192.168.137.207:4747/videos'
    usb_cam = 0

    cap = cv2.VideoCapture(net_cam)

    play_sound_thread = threading.Thread(target=play_bgm_thread_target)
    play_sound_thread.start()
    while (True):
        is_frame_capture, frame = cap.read()

        # lab
        # is_frame_capture = True
        # frame = cv2.imread('imgs/virtual_cam.png')
        # cv2.imshow('frame', frame)

        if is_frame_capture:
            if frame is not None:
                cv2.imshow('cam', frame)
                process_frame(frame)
        time.sleep(0.01)

    # 当一切结束后，释放VideoCapture对象
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
