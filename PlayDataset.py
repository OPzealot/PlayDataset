#!/usr/bin/env python
# encoding:utf-8
"""
author: liusili
@l@icense: (C) Copyright 2019, Union Big Data Co. Ltd. All rights reserved.
@contact: liusili@unionbigdata.com
@software:
@file: PlayDataset
@time: 2019/12/16
@desc:
"""
import os
import shutil
from tqdm import tqdm
from time import sleep
import random
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import xml.etree.ElementTree as ET
from openpyxl import Workbook


def convert_img_format(sample_root, img_format=None, tar_format='.jpg'):
    if img_format is None:
        img_format = ['.jpg', '.JPG']
    for root, _, files in os.walk(sample_root):
        for file in files:
            ori_format = os.path.splitext(file)[1]
            if ori_format in img_format:
                file_path = os.path.join(root, file)
                new_file_path = file_path.replace(ori_format, tar_format)
                shutil.move(file_path, new_file_path)
    print('[FINISH] Convert the format of images.')


class PlayDataset(object):
    def __init__(self, sample_root, img_format='.jpg', img_only=False):
        """
        :param sample_root: 数据集根目录
        :param img_format: 数据图片格式，默认.jpg
        :param img_only: 数据只包含图片 默认False
        """
        self.sample_root = sample_root.rstrip("\\")
        self.name = self.sample_root.split('\\')[-1]
        self.img_format = img_format
        self.img_only = img_only
        self.dataset = self.__file_to_dict()

    def __file_to_dict(self):
        Dataset = {}
        cnt = 0
        for root, _, file_lst in os.walk(self.sample_root):
            if len(file_lst) > 0:
                category = root.split(self.sample_root + '\\')[-1]
                Dataset[category] = []
                for file in file_lst:
                    file_name = os.path.splitext(file)[0]
                    image_path = os.path.join(root, file_name + self.img_format)
                    xml_path = os.path.join(root, file_name + '.xml')
                    if file_name not in Dataset[category] and \
                            (os.path.isfile(xml_path) or self.img_only)\
                            and os.path.isfile(image_path):
                        Dataset[category].append(file_name)
                        cnt += 1
        print('The quantity of all valid images is {}'.format(cnt))
        return Dataset

    def count_category(self):
        """
        :info: 统计每类数量，如果是多级文件则统计所有子类数量，并且输出xlsx表格文件
        """
        output_dir = '.\\output'
        table_path = os.path.join(output_dir, self.name+'_category_quantity.xlsx')
        wb = Workbook()
        sheet = wb.active
        sheet.title = 'Category Quantity'
        for category, name_lst in self.dataset.items():
            quantity = len(name_lst)
            print('Quantity of category [{}]: {}'.format(category, quantity))
            row = category.split('\\') + [quantity]
            sheet.append(row)
        wb.save(table_path)
        wb.close()
        print("[FINISH] The result has been saved at path: {}".format(table_path))

    def gather_data(self):
        """
        :info: 将所有子文件的数据放到同一个目录下
        """
        new_path = os.path.join(self.sample_root+'_gather', 'all')
        os.makedirs(new_path, exist_ok=False)
        pbar = tqdm(self.dataset.items())
        for category, file_lst in pbar:
            category_path = os.path.join(self.sample_root, category)
            for file_name in file_lst:
                image_path = os.path.join(category_path, file_name + self.img_format)
                new_image = os.path.join(new_path, file_name + self.img_format)
                shutil.copyfile(image_path, new_image)
                if not self.img_only:
                    xml_path = os.path.join(category_path, file_name + '.xml')
                    new_xml = os.path.join(new_path, file_name + '.xml')
                    shutil.copyfile(xml_path, new_xml)
            pbar.set_description('Processing category:{}'.format(category))
        sleep(0.5)
        print('[FINISH] Gathering the data is done.')

    def sample_data(self,
                    num_of_samples,
                    dir_name='sample',
                    **sample_dict):
        """
        :info: 对数据集进行随机采样，生成新的数据集
        :param dir_name: 采样文件夹的名称后缀
        :param num_of_samples:采样数量
        :param sample_dict: 这里可以添加特殊category的采样数量，比如类似 A2WBD=800
        """
        new_path = self.sample_root + '_' + dir_name
        others_path = new_path + '_others'
        os.makedirs(new_path, exist_ok=False)
        os.makedirs(others_path, exist_ok=False)

        for category, sample_lst in self.dataset.items():
            category_path = os.path.join(self.sample_root, category)
            sample_category_path = os.path.join(new_path, category)
            sample_others_category_path = os.path.join(others_path, category)
            os.makedirs(sample_category_path, exist_ok=True)
            os.makedirs(sample_others_category_path, exist_ok=True)

            if category in sample_dict:
                num_of_samples = sample_dict[category]

            random.shuffle(sample_lst)
            sample_others_lst = None
            if len(sample_lst) > num_of_samples:
                # 截取未抽样到的图片到others
                sample_others_lst = sample_lst[num_of_samples:]
                sample_lst = sample_lst[:num_of_samples]

            print("---Start sampling dataset---")
            pbar = tqdm(sample_lst)
            for file_name in pbar:
                image_path = os.path.join(category_path, file_name + self.img_format)
                new_image = os.path.join(sample_category_path, file_name + self.img_format)
                shutil.copyfile(image_path, new_image)
                if not self.img_only:
                    xml_path = os.path.join(category_path, file_name + '.xml')
                    new_xml = os.path.join(sample_category_path, file_name + '.xml')
                    shutil.copyfile(xml_path, new_xml)

                pbar.set_description('Processing category:{}'.format(category))

            if not sample_others_lst:
                continue

            print("---Start saving other data---")
            pbar = tqdm(sample_others_lst)
            for file_name in pbar:
                image_path = os.path.join(category_path, file_name + self.img_format)
                new_image = os.path.join(sample_others_category_path, file_name + self.img_format)
                shutil.copyfile(image_path, new_image)
                if not self.img_only:
                    xml_path = os.path.join(category_path, file_name + '.xml')
                    new_xml = os.path.join(sample_others_category_path, file_name + '.xml')
                    shutil.copyfile(xml_path, new_xml)

                pbar.set_description('Processing category:{}'.format(category))
        sleep(0.5)
        print('[FINISH] Data sampling has been finished.')

    def merge_category(self, **merge_dict):
        """
        :info: 对指定的category进行合并，生成新的dataset
        :param merge_dict: 合并category字典，key值是合并后的名称，value是需要合并的category的list
        """
        for merge_category, category_lst in merge_dict.items():
            if merge_category not in self.dataset:
                self.dataset[merge_category] = []
            for category in category_lst:
                if category in self.dataset and category != merge_category:
                    self.dataset[merge_category] += self.dataset.pop(category)
                else:
                    print('Skip merging category {}.'.format(category))

    def plot_dist_of_dataset(self, control_line):
        """
        :info: 绘制缺陷数量分布图
        :param control_line: 数量控制线
        """
        labels = []
        count = []
        for category in sorted(self.dataset.keys()):
            labels.append(category)
            count.append(len(self.dataset[category]))

        x = np.arange(len(labels))

        fig, ax = plt.subplots()
        fig.set_facecolor('papayawhip')
        # 等价于 fig = plt.figure() 和 ax = fig.add_subplot(1,1,1)
        rects = ax.bar(x, count, width=0.5, color='SkyBlue',
                       label='categoryNum')
        line_x = (-1, len(labels))
        line_y = (control_line, control_line)
        if control_line > 0:
            ax.add_line(Line2D(line_x, line_y, linewidth=1, color='IndianRed'))
            ax.annotate('control line', xy=(0, control_line), xytext=(0, 0),
                        textcoords="offset points", color='IndianRed',
                        ha='left', va='bottom')

        ax.set_ylabel('Count')
        ax.set_title('<{}> Image Count for Each category'.format(self.name))
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, rotation_mode='anchor',
                           ha='right', size='x-small')
        #         ax.legend()

        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha='center', va='bottom')

        fig.tight_layout()
        output_dir = '.\\output'
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, self.name + '_categoryCount.png')
        plt.savefig(save_path, facecolor='papayawhip', bbox_inches='tight', dpi=300)
        plt.show()

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

    def info_img_and_category(self):
        """
        :info: 打印图片以及类别的基本特征，大小以及bbox的坐标分布范围
        """
        assert not self.img_only, "This method needs xml files."
        width_min = height_min = bbox_xmin = bbox_ymin = 100000
        width_max = height_max = bbox_xmax = bbox_ymax = 0
        bbox_center_x_dict = {}
        bbox_center_y_dict = {}

        area_lst = []
        for category, name_lst in self.dataset.items():
            category_path = os.path.join(self.sample_root, category)
            bbox_center_x_dict[category] = []
            bbox_center_y_dict[category] = []
            for file_name in name_lst:
                xml_path = os.path.join(category_path, file_name + '.xml')

                tree = ET.parse(xml_path)
                root = tree.getroot()
                size = self.get_and_check(root, 'size', 1)
                width = int(self.get_and_check(size, 'width', 1).text)
                height = int(self.get_and_check(size, 'height', 1).text)

                width_min = min(width, width_min)
                width_max = max(width, width_max)
                height_min = min(height, height_min)
                height_max = max(height, height_max)

                for obj in root.findall('object'):
                    bbox = self.get_and_check(obj, 'bndbox', 1)
                    xmin = int(self.get_and_check(bbox, 'xmin', 1).text)
                    ymin = int(self.get_and_check(bbox, 'ymin', 1).text)
                    xmax = int(self.get_and_check(bbox, 'xmax', 1).text)
                    ymax = int(self.get_and_check(bbox, 'ymax', 1).text)

                    area = (xmax - xmin + 1) * (ymax - ymin + 1)
                    area_lst.append(area)

                    center_x = (xmin + xmax) // 2
                    center_y = (ymin + ymax) // 2

                    bbox_center_x_dict[category].append(center_x)
                    bbox_center_y_dict[category].append(center_y)

                    bbox_xmin = min(xmin, bbox_xmin)
                    bbox_ymin = min(ymin, bbox_ymin)
                    bbox_xmax = max(xmax, bbox_xmax)
                    bbox_ymax = max(ymax, bbox_ymax)

        # 绘制bbox中心散点图
        fig, ax = plt.subplots()
        fig.set_facecolor('papayawhip')
        ax.set_xlim(left=0, right=width_max)
        ax.set_ylim(bottom=height_max, top=0)
        ax.xaxis.tick_top()  # 将x坐标轴移到上方
        ax.set_title('<{}> Distribution of BundingBox Center'.format(self.name))
        plt.grid(alpha=0.75, linestyle='--')
        for category in sorted(bbox_center_x_dict.keys()):
            ax.scatter(bbox_center_x_dict[category], bbox_center_y_dict[category],
                       marker='.', label=category)
        plt.legend(bbox_to_anchor=(1.05, 0), loc=3, borderaxespad=0)

        output_dir = '.\\output'
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, self.name + '_CodeDistribution.png')
        plt.savefig(save_path, facecolor='papayawhip', bbox_inches='tight', dpi=300)
        plt.show()

        # 绘制缺陷面积分布直方图
        fig, ax = plt.subplots()
        fig.set_facecolor('papayawhip')
        n, bins, patches = ax.hist(x=area_lst, bins=15, color='SkyBlue', edgecolor='k')
        plt.grid(axis='y', alpha=0.75)
        for index, num in enumerate(n):
            num = int(num)
            ax.annotate('{}'.format(num), xy=((bins[index] + bins[index + 1]) / 2, num),
                        xytext=(0, 0), textcoords="offset points",
                        ha='center', va='bottom')
        ax.set_xticks(bins)
        ax = plt.gca()
        for label in ax.xaxis.get_ticklabels():
            label.set_rotation(45)
        ax.set_xlabel('CodeArea')
        ax.set_ylabel('Frequency')
        ax.set_title('<{}> Code Area Frequency'.format(self.name))
        save_path = os.path.join(output_dir, self.name + '_CodeAreaFrequency.png')
        plt.savefig(save_path, facecolor='papayawhip', bbox_inches='tight', dpi=300)
        plt.show()

        if width_min == width_max and height_min == height_max:
            print('图片的大小恒定为：width={}像素，height={}像素'.format(width_min, height_min))
        else:
            print('图片大小不恒定：width_max={}，width_min={}; height_max={}, height_min={}'
                  .format(width_max, width_min, height_max, height_min))

        print('BundingBox的取值范围：bbox_xmin={}, bbox_ymin={}, bbox_xmax={}, bbox_ymax={}'
              .format(bbox_xmin, bbox_ymin, bbox_xmax, bbox_ymax))

    def delete_no_BBox_XML(self):
        """
        :info: 删除没有bbox信息的XML文件
        """
        assert not self.img_only, "This method needs xml files."
        cnt = 0
        for category, name_lst in self.dataset.items():
            category_path = os.path.join(self.sample_root, category)
            for file_name in name_lst:
                xml_path = os.path.join(category_path, file_name + '.xml')

                tree = ET.parse(xml_path)
                root = tree.getroot()
                if len(root.findall('object')) == 0:
                    os.remove(xml_path)
                    self.dataset[category].remove(file_name)
                    cnt += 1
                    print('[DELETE] file {:>3d}:{}'.format(cnt, xml_path))
        if cnt == 0:
            print('Nothing has been deleted.')
        print('[FINISH] Delete XML file without bunding box.')

    def move_file_lack_info(self):
        """
        :info: 移动没有标签的图片或者没有对应图片的标签到新的文件夹下
        """
        assert not self.img_only, "This method needs xml files."
        new_path = self.sample_root + '_lack_info'
        os.makedirs(new_path, exist_ok=True)
        for category in os.listdir(self.sample_root):
            category_path = os.path.join(self.sample_root, category)
            new_category_path = os.path.join(new_path, category)
            os.makedirs(new_category_path, exist_ok=True)
            for file in os.listdir(category_path):
                file_name = os.path.splitext(file)[0]
                if file_name not in self.dataset[category]:
                    print('[MOVE] file {} to new directory.'.format(file))
                    file_path = os.path.join(category_path, file)
                    new_file_path = os.path.join(new_category_path, file)
                    shutil.move(file_path, new_file_path)
        print('[FINISH] Move file without complete information.')

    def move_multi_defect_data(self):
        """
        :info: 移动一张图中有多缺陷的图片以及标签到新的文件夹中
        """
        assert not self.img_only, "This method needs xml files."
        new_path = self.sample_root + '_multiDefect'
        os.makedirs(new_path, exist_ok=True)
        print("---Start moving multi-defects images---")
        for category, name_lst in self.dataset.items():
            category_path = os.path.join(self.sample_root, category)
            pbar = tqdm(name_lst)
            for file_name in pbar:
                xml_path = os.path.join(category_path, file_name + '.xml')
                img_path = os.path.join(category_path, file_name + self.img_format)

                tree = ET.parse(xml_path)
                root = tree.getroot()
                for obj in root.findall('object'):
                    name = self.get_and_check(obj, 'name', 1).text
                    if name != category:
                        new_category_path = os.path.join(new_path, category)
                        os.makedirs(new_category_path, exist_ok=True)
                        new_xml_path = os.path.join(new_category_path, file_name + '.xml')
                        new_img_path = os.path.join(new_category_path, file_name + self.img_format)
                        shutil.move(xml_path, new_xml_path)
                        shutil.move(img_path, new_img_path)
                        self.dataset[category].remove(file_name)
                        break
                    pbar.set_description('Processing category:{}'.format(category))
        sleep(1)
        print('---End moving multi-defects files---')

    def correct_wrong_tag(self, category, correct_category):
        """
        :info: 将打标拼写错误的标签纠正
        """
        assert not self.img_only, "This method needs xml files."
        assert category in self.dataset, 'category:{} does not exist.'.format(category)
        category_path = os.path.join(self.sample_root, category)
        for file_name in self.dataset[category]:
            xml_path = os.path.join(category_path, file_name + '.xml')
            tree = ET.parse(xml_path)
            root = tree.getroot()
            size = self.get_and_check(root, 'size', 1)
            width = self.get_and_check(size, 'width', 1).text
            height = self.get_and_check(size, 'height', 1).text
            for obj in root.findall('object'):
                name = self.get_and_check(obj, 'name', 1).text
                if name == category:
                    self.get_and_check(obj, 'name', 1).text = correct_category
            print('[Correct] Correct category name of {}.xml file.'.format(file_name))
            tree.write(xml_path)
        print('[FINISH] Correct category of XML file.')

    def correct_dataset(self):
        """
        :info: 将所有文件按照xml标签中的类别进行分类,如果标记有difficult则放入困难样本
        """
        assert not self.img_only, "This method needs xml files."
        new_path = self.sample_root + '_correct'
        os.makedirs(new_path, exist_ok=True)
        print("---Start correcting dataset---")
        sleep(1)
        for category, name_lst in self.dataset.items():
            category_path = os.path.join(self.sample_root, category)
            pbar = tqdm(name_lst)
            for file_name in pbar:
                xml_path = os.path.join(category_path, file_name + '.xml')
                img_path = os.path.join(category_path, file_name + self.img_format)

                tree = ET.parse(xml_path)
                root = tree.getroot()

                area = 0
                difficult = 0
                for obj in root.findall('object'):
                    diff = int(self.get_and_check(obj, 'difficult', 1).text)
                    if diff == 1:
                        difficult = 1
                    bbox = self.get_and_check(obj, 'bndbox', 1)
                    xmin = int(self.get_and_check(bbox, 'xmin', 1).text)
                    ymin = int(self.get_and_check(bbox, 'ymin', 1).text)
                    xmax = int(self.get_and_check(bbox, 'xmax', 1).text)
                    ymax = int(self.get_and_check(bbox, 'ymax', 1).text)
                    bbox_area = (xmax - xmin + 1) * (ymax - ymin + 1)
                    if bbox_area > area:
                        area = bbox_area
                        new_category = self.get_and_check(obj, 'name', 1).text

                new_category_path = os.path.join(new_path, new_category)
                if difficult == 1:
                    new_category_path = os.path.join(new_path, 'difficult', new_category)
                os.makedirs(new_category_path, exist_ok=True)
                new_xml_path = os.path.join(new_category_path, file_name + '.xml')
                new_img_path = os.path.join(new_category_path, file_name + self.img_format)
                shutil.copy(xml_path, new_xml_path)
                shutil.copy(img_path, new_img_path)
                pbar.set_description('Processing raw category:{}'.format(category))
        sleep(1)
        print('---End copying file with correct tag---')

    def modify_xml(self, category):
        """
        :info: 对于一些特殊的category，修改bbox信息至全图范围
        """
        assert not self.img_only, "This method needs xml files."
        assert category in self.dataset, 'category:{} does not exist.'.format(category)
        category_path = os.path.join(self.sample_root, category)
        for file_name in self.dataset[category]:
            xml_path = os.path.join(category_path, file_name + '.xml')
            tree = ET.parse(xml_path)
            root = tree.getroot()
            size = self.get_and_check(root, 'size', 1)
            width = self.get_and_check(size, 'width', 1).text
            height = self.get_and_check(size, 'height', 1).text
            obj = self.get_and_check(root, 'object', 1)
            bbox = self.get_and_check(obj, 'bndbox', 1)
            # 修改bbox坐标
            self.get_and_check(bbox, 'xmin', 1).text = '1'
            self.get_and_check(bbox, 'ymin', 1).text = '1'
            self.get_and_check(bbox, 'xmax', 1).text = width
            self.get_and_check(bbox, 'ymax', 1).text = height
            print('[MODIFY] Modify bunding box of {}.xml file.'.format(file_name))
            tree.write(xml_path)
        print('[FINISH] Modify bunding box of XML file.')
        
    def reset_difficult(self):
        """
        :info: 重置标签xml中difficult信息
        """
        assert not self.img_only, "This method needs xml files."
        print("---Start resetting difficult dataset---")
        total_resetting = 0
        for category, name_lst in self.dataset.items():
            category_path = os.path.join(self.sample_root, category)
            cnt = 0
            for file_name in name_lst:
                xml_path = os.path.join(category_path, file_name + '.xml')
                tree = ET.parse(xml_path)
                root = tree.getroot()

                for obj in root.findall('object'):
                    diff = int(self.get_and_check(obj, 'difficult', 1).text)
                    if diff == 1:
                        self.get_and_check(obj, 'difficult', 1).text = '0'
                        cnt += 1
                        tree.write(xml_path)
            print('The number of reset category [{}]: {}'.format(category, cnt))
            total_resetting += cnt
        print('[FINISH] Total number of reset data: {}'.format(total_resetting))


if __name__ == '__main__':
    sample_root = r'D:\Working\阿里天池项目\数据重庆\Data\CQCampain'
    playData = PlayDataset(sample_root)
    playData.correct_dataset()