#!/usr/bin/env python
# encoding:utf-8
"""
author: liusili
@l@icense: (C) Copyright 2019, Union Big Data Co. Ltd. All rights reserved.
@contact: liusili@unionbigdata.com
@software:
@file: PlayResult.py
@time: 2020/2/19
@desc: 
"""
import os
import shutil
from tqdm import tqdm
from time import sleep


class PlayResult(object):
    def __init__(self, sample_root, img_format='.jpg'):
        """
        :param sample_root: 结果目录
        :param img_format: 结果图片格式，默认.jpg
        """
        self.sample_root = sample_root
        self.img_format = img_format
        self.dataset = self.__file_to_dict()

    def __file_to_dict(self):
        dataset = {}
        cnt = 0
        for root, _, file_lst in os.walk(self.sample_root):
            if len(file_lst) > 0:
                category = root.split(self.sample_root + '\\')[-1]
                dataset[category] = []
                for file in file_lst:
                    file_name = os.path.splitext(file)[0]
                    image_path = os.path.join(root, file_name + self.img_format)
                    if file_name not in dataset[category] \
                            and os.path.isfile(image_path):
                        dataset[category].append(file_name)
                        cnt += 1
        for category, file_lst in list(dataset.items()):
            if len(file_lst) == 0: 
                del dataset[category]
                
        print('The quantity of all valid images is {}'.format(cnt))
        return dataset

    def filter_correct(self):
        """
        :info: 过滤掉预测正确的图片
        :return: 返回字典
        """
        cnt = 0
        for category, file_list in list(self.dataset.items()):
            if category.split('\\')[-1] == category.split('\\')[-2]:
                del self.dataset[category]
            else:
                cnt += len(file_list)
        print('The quantity of incorrect prediction is {}'.format(cnt))

    def merge_incorrect_data(self):
        self.filter_correct()
        new_path = self.sample_root + '_incorrect'
        print('---Start merging incorrect data---')
        sleep(0.5)
        pbar = tqdm(self.dataset.items())
        for category, file_list in pbar:
            predict_cat = category.split('\\')[-1]
            ori_cat = category.split('\\')[-2]
            new_category_path = os.path.join(new_path, ori_cat, predict_cat)
            os.makedirs(new_category_path, exist_ok=True)
            for file_name in file_list:
                img_path = os.path.join(self.sample_root, category, file_name + self.img_format)
                new_img_path = os.path.join(new_category_path, file_name + self.img_format)
                shutil.copy(img_path, new_img_path)
            pbar.set_description('Processing category:{}'.format(category))
        sleep(0.5)
        print('---End merging incorrect data---')

    def reconstruct_result(self):
        correct_path = self.sample_root + '_correct'
        incorrect_path = self.sample_root + '_incorrect'
        print('---Start reconstructing results---')
        sleep(0.5)
        pbar = tqdm(self.dataset.items())
        for category, file_list in pbar:
            predict_cat = category.split('\\')[-1]
            ori_cat = category.split('\\')[-2]
            if predict_cat == ori_cat:
                new_category_path = os.path.join(correct_path, predict_cat)
            else:
                new_category_path = os.path.join(incorrect_path, ori_cat, predict_cat)
            os.makedirs(new_category_path, exist_ok=True)
            for file_name in file_list:
                img_path = os.path.join(self.sample_root, category, file_name + self.img_format)
                new_img_path = os.path.join(new_category_path, file_name + self.img_format)
                shutil.copy(img_path, new_img_path)
            pbar.set_description('Processing category:{}'.format(category))
        sleep(0.5)
        print('---End reconstructing results---')