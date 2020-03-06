#!/usr/bin/env python
# encoding:utf-8
"""
author: liusili
@l@icense: (C) Copyright 2019, Union Big Data Co. Ltd. All rights reserved.
@contact: liusili@unionbigdata.com
@software:
@file: DifficultDataset
@time: 2019/12/16
@desc:
"""
import os
import shutil
import xml.etree.ElementTree as ET
from time import sleep


class DifficultDataset(object):
    def __init__(self, sample_root, img_format='.jpg'):
        """
        :param sample_root: 数据集根目录
        :param img_format: 数据图片格式，默认.JPG
        :rank: 数据集目录层级 默认2
        """
        self.sample_root = sample_root[:-1] if sample_root.endswith('\\') else sample_root
        self.name = self.sample_root.split('\\')[-1]
        self.img_format = img_format
        self.dataset = self.file_to_dict()

    def file_to_dict(self):
        Dataset = {}
        cnt = 0
        for code in os.listdir(self.sample_root):
            Dataset[code] = []
            code_path = os.path.join(self.sample_root, code)
            for _, _, img_lst in os.walk(code_path):
                if len(img_lst) > 0:
                    cnt += len(img_lst)
                    for img in img_lst:
                        img_name = os.path.splitext(img)[0]
                        if img_name not in Dataset[code]:
                            Dataset[code].append(img_name)
        print('The quantity of all valid images is {}'.format(cnt))
        return Dataset

    def move_difficult_data(self, target_path):
        """
        :info: 将困难样本文件夹中的图片，对应的目标文件夹中的图片以及标签信息移动到新的文件夹中
        """
        target_path = target_path[:-1] if target_path.endswith('\\') else target_path
        new_path = target_path + '_difficult'
        os.makedirs(new_path, exist_ok=True)
        for code in os.listdir(target_path):
            if code not in self.dataset: continue
            code_path = os.path.join(target_path, code)
            new_code_path = os.path.join(new_path, code)
            os.makedirs(new_code_path)
            for file in os.listdir(code_path):
                file_name = os.path.splitext(file)[0]
                file_path = os.path.join(code_path, file)
                new_file_path = os.path.join(new_code_path, file)
                if file_name in self.dataset[code]:
                    print('[MOVE] file {} to new directory.'.format(file))
                    shutil.move(file_path, new_file_path)
        print('[FINISH]')

    def move_file(self, target_path):
        target_path = target_path[:-1] if target_path.endswith('\\') else target_path
        new_path = target_path + '_new'
        os.makedirs(new_path, exist_ok=True)
        for code, file_name_lst in self.dataset.items():
            new_code_path = os.path.join(new_path, code)
            os.makedirs(new_code_path, exist_ok=True)
            for file_name in file_name_lst:
                xml_path = os.path.join(target_path, file_name + '.xml')
                img_path = os.path.join(target_path, file_name + self.img_format)
                new_xml_path = os.path.join(new_code_path, file_name + '.xml')
                new_img_path = os.path.join(new_code_path, file_name + self.img_format)
                if os.path.isfile(img_path) and os.path.isfile(xml_path):
                    shutil.move(img_path, new_img_path)
                    shutil.move(xml_path, new_xml_path)
        sleep(1)
        print('[FINISH]')



    @staticmethod
    def get_and_check(root, name, length):
        """
        :param root: Element-tree 根节点
        :param name: 需要返回的子节点名称
        :param length: 确认子节点长度
        """
        var_lst = root.findall(name)
        if len(var_lst) == 0:
            raise NotImplementedError('Can not find %s in %s.' % (name, root.tag))
        if (length > 0) and (len(var_lst) != length):
            raise NotImplementedError('The size of %s is supposed to be %d, but is %d.'
                                      % (name, length, len(var_lst)))
        if length == 1:
            var_lst = var_lst[0]
        return var_lst

    def correct_dataset(self):
        """
        :info: 将所有文件按照xml标签中的类别进行分类
        """
        new_path = self.sample_root + '_correct'
        os.makedirs(new_path, exist_ok=True)
        for code, name_lst in self.dataset.items():
            code_path = os.path.join(self.sample_root, code)
            for file_name in name_lst:
                xml_path = os.path.join(code_path, file_name + '.xml')
                img_path = os.path.join(code_path, file_name + self.img_format)

                tree = ET.parse(xml_path)
                root = tree.getroot()

                area = 0
                difficult = 0
                for obj in root.findall('object'):
                    diff = int(self.get_and_check(obj, 'difficult', 1).text)
                    if diff == 1: difficult = 1
                    bbox = self.get_and_check(obj, 'bndbox', 1)
                    xmin = int(self.get_and_check(bbox, 'xmin', 1).text)
                    ymin = int(self.get_and_check(bbox, 'ymin', 1).text)
                    xmax = int(self.get_and_check(bbox, 'xmax', 1).text)
                    ymax = int(self.get_and_check(bbox, 'ymax', 1).text)
                    bbox_area = (xmax - xmin + 1) * (ymax - ymin + 1)
                    if bbox_area > area:
                        area = bbox_area
                        category = self.get_and_check(obj, 'name', 1).text

                new_code_path = os.path.join(new_path, category)
                if difficult == 1:
                    new_code_path = os.path.join(new_path, 'difficult', category)
                os.makedirs(new_code_path, exist_ok=True)
                new_xml_path = os.path.join(new_code_path, file_name + '.xml')
                new_img_path = os.path.join(new_code_path, file_name + self.img_format)
                print('[COPY] file {0} xml and {1} to new directory.'.format(file_name, self.img_format[1:]))
                shutil.copy(xml_path, new_xml_path)
                shutil.copy(img_path, new_img_path)
        print('[FINISH]')

if __name__ == '__main__':
    sample_root = '/home/opzealot/Documents/working/Tianma/whtm/V2/difficult'
    playData = DifficultDataset(sample_root)