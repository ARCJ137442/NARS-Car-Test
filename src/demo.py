from datetime import datetime
from os import path
from openpyxl import Workbook
import random
import sys
import time
from visdom import Visdom
import numpy as np
from typing import Container, Tuple, Any, Optional, List
from pygame.locals import *
import pandas as pd
from openpyxl import load_workbook
import pygame
import pygame_menu
from os import getcwd

from Interface import NARSImplementation

# 存放常量


class Constants:
    "存放常量的类"

    class path:
        "路径相关"

        ROOT_PATH = '../' if 'src' in getcwd() else './'
        "项目（包括src、assets等）的根路径。随VSCode调试路径的变化而变化"

        RESULT_PATH = ROOT_PATH + 'result/'
        "存放（结果）数据文件的路径（默认为`../result/`）"

        ASSETS_PATH = ROOT_PATH + 'assets/'
        "存放资源文件的路径（默认为`../assets/`）"

        EXECUTABLE_PATH = ROOT_PATH + 'executable/'
        "存放可执行文件（NARS实现）的路径（默认为`../executable/`）"

    class display:
        "显示相关"
        # 颜色
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)

        # 屏幕大小
        SCREEN_WIDTH = 550  # 教学内容空间（3、5、7、9）-->(150,100,50,0)
        SCREEN_HEIGHT = 400

        # 菜单显示大小
        MENU_WIDTH = 300
        MENU_HEIGHT = 250

        # 墙的大小
        WALL_WIDTH = 50
        WALL_HEIGHT = 50

        # 车的大小
        CAR_WIDTH = 50
        CAR_HEIGHT = 50

        # 小车移动的距离
        MOVE_DISTANCE = CAR_WIDTH  # 小车的一个身位

        # 左右两边空白距离
        LEFT_GAP_DISTANCE = 150
        RIGHT_GAP_DISTANCE = 150

        # 左右两边的临界距离坐标
        LEFT_CRITICAL_DISTANCE = WALL_WIDTH + \
            LEFT_GAP_DISTANCE  # 200
        RIGHT_CRITICAL_DISTANCE = SCREEN_WIDTH - \
            (WALL_WIDTH + CAR_WIDTH + RIGHT_GAP_DISTANCE)  # 300

    class stats:
        "统计相关"
        # 成功次数、失败次数、总次数
        SUCCESS_COUNT = 0
        FAILURE_COUNT = 0
        SUM_COUNT = 0
        SUCCESS_RATE = 0.00

        # 键盘操作的次数
        KEY_TIMES = 0
        NARS_OP_TIMES = 0

        # 小车成功率计算
        NARS_SUCCESS_RATE = 0.00
        NARS_SUCCESS_COUNT = 0
        NARS_FAILURE_COUNT = 0
        NARS_SUM_COUNT = 0
        NARS_ACTIVATION = 0.00

        NARS_LEFT_SUCCESS_COUNT = 0
        NARS_RIGHT_SUCCESS_COUNT = 0
        NARS_LEFT_FAILURE_COUNT = 0
        NARS_RIGHT_FAILURE_COUNT = 0
        NARS_PROCESS = []

        # 训练单独成功率计算
        TRAIN_SUCCESS_RATE = 0.00
        TRAIN_SUCCESS_COUNT = 0
        TRAIN_FAILURE_COUNT = 0
        TRAIN_SUM_COUNT = 0
        TRAIN_PROCESS = []

        # 结果字典
        RESULT_DICT = []
        # NARS过程数组
        NARS_LINE = []

        # ! 「结果保存位置」已迁移至path
        # 过程数据sheet及txt文件名称
        # name = ['3_1_1_1','3_1_1_2','3_1_1_3','3_1_1_4','3_1_1_5','3_1_1_6','3_1_1_7','3_1_1_8','3_1_1_9','3_1_1_10']
        _NOW = datetime.now()
        "获取当前时间，以便让数据结果唯一"

        # NAME = f'{_NOW.year}{str(_NOW.month).zfill(2)}{str(_NOW.day).zfill(2)}-{str(_NOW.hour).zfill(2)}_{str(_NOW.minute).zfill(2)}_{str(_NOW.second).zfill(2)}'
        NAME = '%.04d%.02d%.02d-%.02d%.02d%.02d' % (
            _NOW.year, _NOW.month, _NOW.day, _NOW.hour, _NOW.minute, _NOW.second)
        "使用当前时间生成的「唯一性名称」，使用「_NOW.minute」"  # * 样例：`20220725-11_11_11`

        SHEET_NAME = NAME
        "工作表名称"

        EXCEL_NAME = f'[{NAME}]datas.xlsx'
        "工作簿文件名"  # !【2023-11-10 01:37:28】目前暂时无法实现「相同文件中新增工作表」，只能不断新建

        TXT_NAME = f'[{NAME}]experiences.txt'
        "经验数据的文本文件路径"

        # 实验标题
        VISDOM_TITLE = '实验：修正传感器的影响'

    class game:
        "pygame相关"
        # 菜单初始化
        MAIN_MENU: Optional['pygame_menu.Menu'] = None

        # 发送目标事件
        SEND_GOAL_EVENT = pygame.USEREVENT + 2
        SEND_GOAL_EVENT_TIME = 1*1000

        # 暂停事件
        PAUSE_GAME_EVENT = pygame.USEREVENT + 4
        PAUSE_EVENT_TIME = 300*1000

        # babble事件
        RANDOM_BABBLE_EVENT = pygame.USEREVENT + 3
        BABBLE_DISPLAY_TIMES = 0
        BABBLE_TIMES = 12
        BABBLE_EVENT_TIME = 1.5*1000

        # 序列输入人为操作以便控制人为操作的内容和频率，所以自定义事件完成
        GIVEN_HUMAN_TRAIN_EVENT = pygame.USEREVENT + 5
        GIVEN_HUMAN_TRAIN_CONTENT = (
            (print('人为操作内容：全失败！'), [1, 1, 1, 1, 1, 1])[1]
            if random.random() > 0.5 else
            (print('人为操作内容：全成功！'), [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2])[1])
        '''人为操作内容
        - 数字⇒操作：left=1,right=2
        - 参考序列：
            - 全成功: [1, 2, 2, 1]
            - 全失败: [1, 1, 1]
            - 失败成功参半: [1, 1, 2]
        
        # !【2023-11-10 13:12:38】现在随机选择人为操作内容
        '''
        GIVEN_HUMAN_TRAIN_EVENT_TIME = 1.5*1000

    class temp:
        "临时变量"
        # 训练传入操作的信号
        TRAIN_SIGNAL = False

        # NARS传入操作的信号
        OP_SIGNAL = False

        # 是否允许NARS操作小车
        RUN_OP_FLAG = True
        '''是否运行小车自主操作
        若干预时，需要阻止小车自主运动的执行，则初始值为False，干预完之后将值设为True
        若不要这个操作，则初始值为True即可。
        '''


# 墙体类，依据位置分成不同的类
class Wall(pygame.sprite.Sprite):
    "墙的基类，位置固定，不能移动"

    def __init__(self, left):
        "初始化：这里的`left`指的是墙体的左边距离屏幕的距离"
        super().__init__()
        self.image = pygame.image.load(
            Constants.path.ASSETS_PATH + "wall_50px.png")
        self.rect = self.image.get_rect(
            top=Constants.display.SCREEN_HEIGHT-Constants.display.WALL_HEIGHT,
            left=left)

    def move(self):
        "不能移动"
        pass


class Wall_L(Wall):
    "左边的墙"

    def __init__(self):
        super().__init__(Constants.display.LEFT_GAP_DISTANCE)


class Wall_R(Wall):
    "右边的墙"

    def __init__(self):
        super().__init__(Constants.display.SCREEN_WIDTH -
                         Constants.display.WALL_WIDTH-Constants.display.RIGHT_GAP_DISTANCE)


class Car(pygame.sprite.Sprite):
    "小车类，确定小车起始位置，小车移动的操作一并写入了Game类中"

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(
            Constants.path.ASSETS_PATH + "car_50px.png")
        x = Constants.display.SCREEN_WIDTH / 2
        self.rect = self.image.get_rect(
            center=(x, Constants.display.SCREEN_HEIGHT-Constants.display.CAR_HEIGHT*0.5))

    def move(self):
        pass


class Game:
    "游戏类"  # TODO: 或许需要再把「游戏」和「主体」分离，把「小车」单独作一个类

    def __init__(self):
        "游戏的初始化方法，主要负责游戏前的准备工作"

        # 总初始化
        pygame.init()
        size = width, height = (Constants.display.SCREEN_WIDTH,
                                Constants.display.SCREEN_HEIGHT)

        pygame.display.set_caption("机器教育有效性实验")
        self.screen = pygame.display.set_mode(size)

        # 元素

        self.car = Car()
        self.wall_1 = Wall_L()
        self.wall_2 = Wall_R()
        self.inference_rate = 10

        self.enemies = pygame.sprite.Group()
        self.enemies.add(self.wall_1)
        self.enemies.add(self.wall_2)

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.car)
        self.all_sprites.add(self.wall_1)
        self.all_sprites.add(self.wall_2)

        # 时钟

        self.clock = pygame.time.Clock()

        # 字体

        # display text like scores, times, etc.
        self.font = pygame.font.Font(
            Constants.path.ASSETS_PATH + "SimSun.ttf", 14)

        # 数据显示

        self.viz = Visdom(env='carTest')

        self.opts1 = {
            "title": Constants.stats.VISDOM_TITLE,
            "xlabel": '时间(s)',
            "ylabel": '小车避障成功率(%)',
            "width": 600,
            "height": 500,
            "legend": ['总成绩', '训练成绩', '学习成绩', 'NARS活跃度']
        }
        self.x = []
        self.Yn = []
        self.datas = []  # 用于结果存入excel
        self.train_process_str = ''

    def on_NARS_output(self, line):
        "在NARS有输出时触发"
        # 加入历史，打印
        Constants.stats.NARS_LINE.append(line)
        print(line)

    def on_NARS_operation(self, operator):
        "在NARS有输出时触发"
        print(operator)
        if Constants.temp.RUN_OP_FLAG == True:
            # 操作：左移
            if operator == '^left':
                Constants.temp.OP_SIGNAL = True
                self.condition_judge('left')
                self.move_left()
                Constants.stats.NARS_OP_TIMES += 1
                Constants.temp.OP_SIGNAL = False
            # 操作：右移
            if operator == '^right':
                Constants.temp.OP_SIGNAL = True
                self.condition_judge('right')
                self.move_right()
                Constants.stats.NARS_OP_TIMES += 1
                Constants.temp.OP_SIGNAL = False

    def getSense(self):
        '''小车获取当前位置--获取感知信息
        原文参考：
        接口模块负责持续监听传感器产生的距离信息，将其装配成合法纳思语后单向送入OpenNARS，例如：“< {lsensor} → [50] >.”
        
        # !【2023-11-10 14:21:26】目前的「感知」仍然保留在`Game`模块中，因为其数据仍然需要从`Game`模块中获取。
        '''  # TODO: 或许这个也要和论文所说一样，纳入「接口」模块中
        # print('l_sensor:' + str(self.car.rect.x - self.wall_1.rect.x + Constants.WALL_WIDTH))
        # print('r_sensor:' + str(self.wall_2.rect.x - self.car.rect.x - Constants.CAR_WIDTH))
        # print('#########################')
        # print('l_sensor_n:' + str(self.car.rect.x - Constants.WALL_WIDTH - Constants.LEFT_GAP_DISTANCE))
        # print('r_sensor_n:' + str(Constants.SCREEN_WIDTH - self.car.rect.x - Constants.CAR_WIDTH - Constants.WALL_WIDTH - Constants.RIGHT_GAP_DISTANCE))
        self.NARS.add_sense('l_sensor',  # 告知NARS现在左侧的位置
                            str(self.car.rect.x - Constants.display.WALL_WIDTH -
                                Constants.display.LEFT_GAP_DISTANCE))
        self.NARS.add_sense('r_sensor',  # 告知NARS现在右侧的位置
                            str(Constants.display.SCREEN_WIDTH - self.car.rect.x - Constants.display.CAR_WIDTH -
                                Constants.display.WALL_WIDTH - Constants.display.RIGHT_GAP_DISTANCE))

    def move_left(self):
        "左移运动"
        # 精神运动
        self.getSense()
        self.NARS.add_operation_experience('left', self.NARS.SELF)
        # 这里也许有推理时间
        if self.car.rect.x - Constants.display.MOVE_DISTANCE < (Constants.display.WALL_WIDTH+Constants.display.LEFT_GAP_DISTANCE):
            # 物理运动
            self.car.rect.x = Constants.display.WALL_WIDTH + \
                Constants.display.LEFT_GAP_DISTANCE
            # 感知变化
            self.getSense()
            # 结果
            self.NARS.add_self_status('safe', True)  # 负反馈
        else:
            # 物理运动
            self.car.rect.x -= Constants.display.MOVE_DISTANCE
            # 感知变化
            self.getSense()
            # 结果
            self.NARS.add_self_status('safe', False)  # 正反馈
        # 数据显示
        self.visdom_data()

    def move_right(self):
        "右移运动"
        # 运动发生
        self.getSense()
        self.NARS.add_operation_experience('right', self.NARS.SELF)
        if self.car.rect.x + Constants.display.MOVE_DISTANCE > Constants.display.SCREEN_WIDTH-Constants.display.WALL_WIDTH-Constants.display.CAR_WIDTH-Constants.display.LEFT_GAP_DISTANCE:
            # 物理运动
            self.car.rect.x = Constants.display.SCREEN_WIDTH-Constants.display.WALL_WIDTH - \
                Constants.display.CAR_WIDTH-Constants.display.LEFT_GAP_DISTANCE
            # 感知变化
            self.getSense()
            # 运动发生引发感知变化的结果
            self.NARS.add_self_status('safe', True)  # 负反馈
        else:
            self.car.rect.x += Constants.display.MOVE_DISTANCE
            # 感知变化
            self.getSense()
            # 引发结果
            self.NARS.add_self_status('safe', False)  # 正反馈
        # 数据显示
        self.visdom_data()

    def condition_judge(self, key_value):
        '''移动条件判断
        判断位于临界位置时操作发生的后果——成功/失败
        亦用于对小车行动的统计
        '''
        print("------------------------")
        print(key_value)
        print(self.car.rect.x)
        if self.car.rect.x == Constants.display.LEFT_CRITICAL_DISTANCE and key_value == 'left':
            Constants.stats.FAILURE_COUNT += 1
        if self.car.rect.x == Constants.display.LEFT_CRITICAL_DISTANCE and key_value == 'right':
            Constants.stats.SUCCESS_COUNT += 1
        if self.car.rect.x == Constants.display.RIGHT_CRITICAL_DISTANCE and key_value == 'left':
            Constants.stats.SUCCESS_COUNT += 1
        if self.car.rect.x == Constants.display.RIGHT_CRITICAL_DISTANCE and key_value == 'right':
            Constants.stats.FAILURE_COUNT += 1
        if self.car.rect.x == Constants.display.LEFT_CRITICAL_DISTANCE or self.car.rect.x == Constants.display.RIGHT_CRITICAL_DISTANCE:
            Constants.stats.SUM_COUNT += 1
        if Constants.stats.SUM_COUNT > 0:
            Constants.stats.SUCCESS_RATE = round(
                Constants.stats.SUCCESS_COUNT/Constants.stats.SUM_COUNT, 2)
        # 添加NARS独自操作的成功率
        if Constants.temp.OP_SIGNAL == True:
            if self.car.rect.x == Constants.display.LEFT_CRITICAL_DISTANCE and key_value == 'left':
                print("左侧NARS失败！")
                Constants.stats.NARS_FAILURE_COUNT += 1
                Constants.stats.NARS_PROCESS.append('L_F')
            if self.car.rect.x == Constants.display.LEFT_CRITICAL_DISTANCE and key_value == 'right':
                print("左侧NARS成功！")
                Constants.stats.NARS_SUCCESS_COUNT += 1
                Constants.stats.NARS_PROCESS.append('L_S')
            if self.car.rect.x == Constants.display.RIGHT_CRITICAL_DISTANCE and key_value == 'left':
                print("右侧NARS成功")
                Constants.stats.NARS_SUCCESS_COUNT += 1
                Constants.stats.NARS_PROCESS.append('R_S')
                Constants.stats.NARS_RIGHT_SUCCESS_COUNT += 1
                if Constants.stats.NARS_RIGHT_SUCCESS_COUNT == 10:
                    Constants.stats.RESULT_DICT.append(
                        {'Repeat_time:': int(self.speeding_delta_time_s)})
            if self.car.rect.x == Constants.display.RIGHT_CRITICAL_DISTANCE and key_value == 'right':
                print("右侧NARS失败")
                Constants.stats.NARS_FAILURE_COUNT += 1
                Constants.stats.NARS_PROCESS.append('R_F')
            if self.car.rect.x == Constants.display.LEFT_CRITICAL_DISTANCE or self.car.rect.x == Constants.display.RIGHT_CRITICAL_DISTANCE:
                Constants.stats.NARS_SUM_COUNT += 1
            if Constants.stats.NARS_SUM_COUNT > 0:
                Constants.stats.NARS_SUCCESS_RATE = round(
                    Constants.stats.NARS_SUCCESS_COUNT/Constants.stats.NARS_SUM_COUNT, 2)
            # 判断连续时间
            for n in range(len(Constants.stats.NARS_PROCESS)):
                if Constants.stats.NARS_PROCESS[n] == 'L_S':
                    Constants.stats.NARS_LEFT_SUCCESS_COUNT += 1
                    if Constants.stats.NARS_LEFT_SUCCESS_COUNT == 10:
                        Constants.stats.RESULT_DICT.append(
                            {'Repeat_time:': int(self.speeding_delta_time_s)})
                elif Constants.stats.NARS_PROCESS[n] == 'L_F':
                    Constants.stats.NARS_LEFT_SUCCESS_COUNT = 0
                elif Constants.stats.NARS_PROCESS[n] == 'R_S':
                    Constants.stats.NARS_LEFT_SUCCESS_COUNT = 0
                elif Constants.stats.NARS_PROCESS[n] == 'R_F':
                    Constants.stats.NARS_LEFT_SUCCESS_COUNT = 0

                if Constants.stats.NARS_PROCESS[n] == 'R_S':
                    Constants.stats.NARS_RIGHT_SUCCESS_COUNT += 1
                    if Constants.stats.NARS_RIGHT_SUCCESS_COUNT == 10:
                        Constants.stats.RESULT_DICT.append(
                            {'Repeat_time:': int(self.speeding_delta_time_s)})
                elif Constants.stats.NARS_PROCESS[n] == 'R_F':
                    Constants.stats.NARS_RIGHT_SUCCESS_COUNT = 0
                elif Constants.stats.NARS_PROCESS[n] == 'L_S':
                    Constants.stats.NARS_RIGHT_SUCCESS_COUNT = 0
                elif Constants.stats.NARS_PROCESS[n] == 'L_F':
                    Constants.stats.NARS_RIGHT_SUCCESS_COUNT = 0

        # 计算训练单独成功率
        if Constants.temp.TRAIN_SIGNAL == True:
            if self.car.rect.x == Constants.display.LEFT_CRITICAL_DISTANCE and key_value == 'left':
                print("左侧训练失败！")
                Constants.stats.TRAIN_FAILURE_COUNT += 1
                Constants.stats.TRAIN_PROCESS.append('L_F')
            if self.car.rect.x == Constants.display.LEFT_CRITICAL_DISTANCE and key_value == 'right':
                print("左侧训练成功！")
                Constants.stats.TRAIN_SUCCESS_COUNT += 1
                Constants.stats.TRAIN_PROCESS.append('L_S')
            if self.car.rect.x == Constants.display.RIGHT_CRITICAL_DISTANCE and key_value == 'left':
                print("右侧训练成功")
                Constants.stats.TRAIN_SUCCESS_COUNT += 1
                Constants.stats.TRAIN_PROCESS.append('R_S')
            if self.car.rect.x == Constants.display.RIGHT_CRITICAL_DISTANCE and key_value == 'right':
                print("右侧训练失败")
                Constants.stats.TRAIN_FAILURE_COUNT += 1
                Constants.stats.TRAIN_PROCESS.append('R_F')
            if self.car.rect.x == Constants.display.LEFT_CRITICAL_DISTANCE or self.car.rect.x == Constants.display.RIGHT_CRITICAL_DISTANCE:
                Constants.stats.TRAIN_SUM_COUNT += 1
            if Constants.stats.TRAIN_SUM_COUNT > 0:
                Constants.stats.TRAIN_SUCCESS_RATE = round(
                    Constants.stats.TRAIN_SUCCESS_COUNT/Constants.stats.TRAIN_SUM_COUNT, 2)
        print("------------------------")

    #
    def __set_timer(self):
        "事件的设置，主要用于事件的触发"
        timer_update_NARS = int(
            Constants.game.SEND_GOAL_EVENT_TIME / self.game_speed)
        timer_babble = int(Constants.game.BABBLE_EVENT_TIME / self.game_speed)
        timer_pause = int(Constants.game.PAUSE_EVENT_TIME / self.game_speed)
        timer_given_human = int(
            Constants.game.GIVEN_HUMAN_TRAIN_EVENT_TIME / self.game_speed)
        pygame.time.set_timer(
            Constants.game.SEND_GOAL_EVENT, timer_update_NARS)
        pygame.time.set_timer(Constants.game.RANDOM_BABBLE_EVENT, timer_babble)
        pygame.time.set_timer(Constants.game.PAUSE_GAME_EVENT, timer_pause)
        pygame.time.set_timer(
            Constants.game.GIVEN_HUMAN_TRAIN_EVENT, timer_given_human)

    def print_process(self, process, init_width, init_height):
        "页面经验显示功能"
        x = len(process)//10 + 1
        if x % 4 == 1:
            height = init_height
            start = 10*(x-1)
            if start+10 > len(process):
                end = len(process)
            elif start+10 <= len(process):
                end = start + 10
            for j in range(start, end):
                self.train_process_str = self.train_process_str + \
                    '->' + process[j]
                j += 1
            train_process = self.font.render(
                self.train_process_str, True, Constants.display.BLACK)
            self.screen.blit(train_process, [init_width, height])
            self.train_process_str = ''
        if x % 4 == 2:
            start = 10*(x-2)
            if start+10 > len(process):
                end = len(process)
            elif start+10 <= len(process):
                end = start + 10
            for i in range(0, 2):
                height = init_height
                self.train_process_str = ''
                for j in range(start, end):
                    self.train_process_str = self.train_process_str + \
                        '->' + process[j]
                    j += 1
                train_process = self.font.render(
                    self.train_process_str, True, Constants.display.BLACK)
                height = height + 15*i
                self.screen.blit(train_process, [init_width, height])
                i += 1
                start = end
                if start+10 > len(process):
                    end = len(process)
                if start+10 <= len(process):
                    end = start + 10
        if x % 4 == 3:
            start = 10*(x-3)
            if start+10 > len(process):
                end = len(process)
            elif start+10 <= len(process):
                end = start + 10
            for i in range(0, 3):
                height = init_height
                self.train_process_str = ''
                for j in range(start, end):
                    self.train_process_str = self.train_process_str + \
                        '->' + process[j]
                    j += 1
                train_process = self.font.render(
                    self.train_process_str, True, Constants.display.BLACK)
                height = height + 15*i
                self.screen.blit(train_process, [init_width, height])
                i += 1
                start = end
                if start+10 > len(process):
                    end = len(process)
                if start+10 <= len(process):
                    end = start + 10
        if x % 4 == 0:
            start = 10*(x-4)
            if start+10 > len(process):
                end = len(process)
            elif start+10 <= len(process):
                end = start + 10
            for i in range(0, 4):
                height = init_height
                self.train_process_str = ''
                for j in range(start, end):
                    self.train_process_str = self.train_process_str + \
                        '->' + process[j]
                    j += 1
                train_process = self.font.render(
                    self.train_process_str, True, Constants.display.BLACK)
                height = height + 15*i
                self.screen.blit(train_process, [init_width, height])
                i += 1
                start = end
                if start+10 > len(process):
                    end = len(process)
                if start+10 <= len(process):
                    end = start + 10

    def __display_text_babble(self):
        "随机babble中的文字显示"
        current_time = pygame.time.get_ticks()
        delta_time_s = (current_time - self.start_time) / 1000
        self.speeding_delta_time_s = delta_time_s * self.game_speed

        time = self.font.render(
            '时间: %d' % self.speeding_delta_time_s, True, Constants.display.BLACK)

        babbling = self.font.render(
            '随机训练次数: %d' % Constants.game.BABBLE_DISPLAY_TIMES, True, Constants.display.BLACK)
        train_success_count = self.font.render(
            '训练成功次数：%d' % Constants.stats.TRAIN_SUCCESS_COUNT, True, Constants.display.BLACK)
        train_failure_count = self.font.render(
            '训练失败次数：%d' % Constants.stats.TRAIN_FAILURE_COUNT, True, Constants.display.BLACK)
        train_sum_count = self.font.render(
            '训练总次数：%d' % Constants.stats.TRAIN_SUM_COUNT, True, Constants.display.BLACK)
        train_success_rate = self.font.render(
            '训练成功率：%.2f' % Constants.stats.TRAIN_SUCCESS_RATE, True, Constants.display.BLACK)

        self.print_process(Constants.stats.TRAIN_PROCESS, 70, 100)

        NARS_op = self.font.render(
            'NARS次数: %d' % Constants.stats.NARS_OP_TIMES, True, Constants.display.BLACK)
        if Constants.stats.NARS_OP_TIMES == 1:
            Constants.stats.RESULT_DICT.append(
                {'NARS_start_time:': int(self.speeding_delta_time_s)})
        if Constants.stats.NARS_OP_TIMES > 0:
            Constants.stats.NARS_ACTIVATION = round(
                Constants.stats.NARS_OP_TIMES/self.speeding_delta_time_s, 2)
        NARS_activation = self.font.render(
            'NARS活跃度: %.2f' % Constants.stats.NARS_ACTIVATION, True, Constants.display.BLACK)
        if Constants.stats.NARS_ACTIVATION == 0.50:
            Constants.stats.RESULT_DICT.append(
                {'Active>0.50_time:': int(self.speeding_delta_time_s)})
        NARS_activation = self.font.render(
            'NARS活跃度: %.2f' % Constants.stats.NARS_ACTIVATION, True, Constants.display.BLACK)
        NARS_success_count = self.font.render(
            'NARS成功次数：%d' % Constants.stats.NARS_SUCCESS_COUNT, True, Constants.display.BLACK)
        NARS_failure_count = self.font.render(
            'NARS失败次数：%d' % Constants.stats.NARS_FAILURE_COUNT, True, Constants.display.BLACK)
        NARS_sum_count = self.font.render(
            'NARS总次数：%d' % Constants.stats.NARS_SUM_COUNT, True, Constants.display.BLACK)
        NARS_success_rate = self.font.render(
            'NARS成功率：%.2f' % Constants.stats.NARS_SUCCESS_RATE, True, Constants.display.BLACK)

        self.print_process(Constants.stats.NARS_PROCESS, 70, 230)

        success_count = self.font.render(
            '成功次数：%d' % Constants.stats.SUCCESS_COUNT, True, Constants.display.BLACK)
        failure_count = self.font.render(
            '失败次数：%d' % Constants.stats.FAILURE_COUNT, True, Constants.display.BLACK)
        sum_count = self.font.render(
            '总次数：%d' % Constants.stats.SUM_COUNT, True, Constants.display.BLACK)
        success_rate = self.font.render(
            '成功率：%.2f' % Constants.stats.SUCCESS_RATE, True, Constants.display.BLACK)

        self.screen.blit(time, [70, 10])

        self.screen.blit(babbling, [70, 40])
        self.screen.blit(train_success_count, [320, 40])
        self.screen.blit(train_failure_count, [70, 60])
        self.screen.blit(train_sum_count, [320, 60])
        self.screen.blit(train_success_rate, [70, 80])

        self.screen.blit(NARS_op, [70, 170])
        self.screen.blit(NARS_activation, [320, 170])
        self.screen.blit(NARS_success_count, [70, 190])
        self.screen.blit(NARS_failure_count, [320, 190])
        self.screen.blit(NARS_sum_count, [70, 210])
        self.screen.blit(NARS_success_rate, [320, 210])

        self.screen.blit(success_count, [70, 300])
        self.screen.blit(failure_count, [320, 300])
        self.screen.blit(sum_count, [70, 320])
        self.screen.blit(success_rate, [320, 320])

    def __display_text_human(self):
        "人为训练中的文字显示"
        current_time = pygame.time.get_ticks()
        delta_time_s = (current_time - self.start_time) / 1000
        self.speeding_delta_time_s = delta_time_s * self.game_speed

        time = self.font.render(
            '时间: %d' % self.speeding_delta_time_s, True, Constants.display.BLACK)

        babbling = self.font.render('键盘训练次数: %d' %
                                    Constants.stats.KEY_TIMES, True, Constants.display.BLACK)
        train_success_count = self.font.render(
            '训练成功次数：%d' % Constants.stats.TRAIN_SUCCESS_COUNT, True, Constants.display.BLACK)
        train_failure_count = self.font.render(
            '训练失败次数：%d' % Constants.stats.TRAIN_FAILURE_COUNT, True, Constants.display.BLACK)
        train_sum_count = self.font.render(
            '训练总次数：%d' % Constants.stats.TRAIN_SUM_COUNT, True, Constants.display.BLACK)
        train_success_rate = self.font.render(
            '训练成功率：%.2f' % Constants.stats.TRAIN_SUCCESS_RATE, True, Constants.display.BLACK)

        self.print_process(Constants.stats.TRAIN_PROCESS, 70, 100)

        NARS_op = self.font.render(
            'NARS次数: %d' % Constants.stats.NARS_OP_TIMES, True, Constants.display.BLACK)
        if Constants.stats.NARS_OP_TIMES == 1:
            Constants.stats.RESULT_DICT.append(
                {'NARS_start_time:': int(self.speeding_delta_time_s)})
        if Constants.stats.NARS_OP_TIMES > 0:
            Constants.stats.NARS_ACTIVATION = round(
                Constants.stats.NARS_OP_TIMES/self.speeding_delta_time_s, 2)
        NARS_activation = self.font.render(
            'NARS活跃度: %.2f' % Constants.stats.NARS_ACTIVATION, True, Constants.display.BLACK)
        if Constants.stats.NARS_ACTIVATION == 0.50:
            Constants.stats.RESULT_DICT.append(
                {'Active>0.50_time:': int(self.speeding_delta_time_s)})
        NARS_success_count = self.font.render(
            'NARS成功次数：%d' % Constants.stats.NARS_SUCCESS_COUNT, True, Constants.display.BLACK)
        NARS_failure_count = self.font.render(
            'NARS失败次数：%d' % Constants.stats.NARS_FAILURE_COUNT, True, Constants.display.BLACK)
        NARS_sum_count = self.font.render(
            'NARS总次数：%d' % Constants.stats.NARS_SUM_COUNT, True, Constants.display.BLACK)
        NARS_success_rate = self.font.render(
            'NARS成功率：%.2f' % Constants.stats.NARS_SUCCESS_RATE, True, Constants.display.BLACK)

        self.print_process(Constants.stats.NARS_PROCESS, 70, 230)

        success_count = self.font.render(
            '成功次数：%d' % Constants.stats.SUCCESS_COUNT, True, Constants.display.BLACK)
        failure_count = self.font.render(
            '失败次数：%d' % Constants.stats.FAILURE_COUNT, True, Constants.display.BLACK)
        sum_count = self.font.render(
            '总次数：%d' % Constants.stats.SUM_COUNT, True, Constants.display.BLACK)
        success_rate = self.font.render(
            '成功率：%.2f' % Constants.stats.SUCCESS_RATE, True, Constants.display.BLACK)

        self.screen.blit(time, [70, 10])

        self.screen.blit(babbling, [70, 40])
        self.screen.blit(train_success_count, [320, 40])
        self.screen.blit(train_failure_count, [70, 60])
        self.screen.blit(train_sum_count, [320, 60])
        self.screen.blit(train_success_rate, [70, 80])

        self.screen.blit(NARS_op, [70, 170])
        self.screen.blit(NARS_activation, [320, 170])
        self.screen.blit(NARS_success_count, [70, 190])
        self.screen.blit(NARS_failure_count, [320, 190])
        self.screen.blit(NARS_sum_count, [70, 210])
        self.screen.blit(NARS_success_rate, [320, 210])

        self.screen.blit(success_count, [70, 300])
        self.screen.blit(failure_count, [320, 300])
        self.screen.blit(sum_count, [70, 320])
        self.screen.blit(success_rate, [320, 320])

    def pause(self):
        "暂停游戏画面"
        self.is_pause = True

        while self.is_pause == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # ! 暂停时退出，也要保存
                    self.save_and_quit()
                if event.type == Constants.game.PAUSE_GAME_EVENT:
                    self.is_pause = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_pause = False
                    elif event.key == pygame.K_q:
                        # ! 暂停时退出，也要保存
                        self.save_and_quit()
        pygame.display.update()
        self.clock.tick(5)

    def write_data(self):
        "将数据写入表格和txt文件"
        print("write_data: 开始保存数据")
        self.write_excel()
        print("write_data: 数据EXCEL写入完毕！")
        self.write_process_txt()
        print("write_data: 经验txt保存完毕！")

    def write_excel(self):
        "将数据写入表格"
        # 数据⇒数据框
        data_frame = pd.DataFrame(
            self.datas,
            columns=["时间", "总成绩", "训练成绩", "学习成绩", 'NARS活跃度'])
        # 打开工作簿
        writer = pd.ExcelWriter(
            Constants.path.RESULT_PATH + Constants.stats.EXCEL_NAME, engine='openpyxl')
        book = None
        # 确定工作簿（尝试读取旧文件）
        try:
            '''#!跳过报错：zipfile.BadZipFile: File is not a zip file'''
            if path.exists(Constants.path.RESULT_PATH + Constants.stats.EXCEL_NAME):
                book = load_workbook(
                    Constants.path.RESULT_PATH + Constants.stats.EXCEL_NAME)
        except BaseException as e:
            print('write_excel: 工作簿读取异常：', e.with_traceback(None) if e else e)
            book = writer.book
            '''
            根据新的错误信息,可以看到是在为ExcelWriter的book属性赋值时报错了,提示该属性不可设置。
            根据Openpyxl文档,ExcelWriter初始化时会新建一个Workbook,之后不能再修改该属性。
            所以可以这样修复原代码:
            '''
        # 数据框⇒Excel表格（指定工作表）
        data_frame.to_excel(
            writer,
            sheet_name=Constants.stats.SHEET_NAME,
            index=False)
        # 保存，关闭
        book.save(filename=Constants.path.RESULT_PATH +
                  Constants.stats.EXCEL_NAME)  # 是工作簿保存，不是写入者保存
        # writer.save()
        writer.close()  # 关闭写入流

    def write_process_txt(self):
        "将经验数据写入txt文件"
        with open(Constants.path.RESULT_PATH + Constants.stats.TXT_NAME, 'w') as f:
            # 记录「操作-成败」
            T_LS_count = 0
            T_RS_count = 0
            N_LS_count = 0
            N_RS_count = 0
            T_LF_count = 0
            T_RF_count = 0
            N_LF_count = 0
            N_RF_count = 0
            f.write('TRAIN_PROCESS:'+'\n')
            for i in range(1, len(Constants.stats.TRAIN_PROCESS)+1):
                f.write(Constants.stats.TRAIN_PROCESS[i-1])
                if Constants.stats.TRAIN_PROCESS[i-1] == 'L_S':
                    T_LS_count += 1
                elif Constants.stats.TRAIN_PROCESS[i-1] == 'R_S':
                    T_RS_count += 1
                if Constants.stats.TRAIN_PROCESS[i-1] == 'L_F':
                    T_LF_count += 1
                elif Constants.stats.TRAIN_PROCESS[i-1] == 'R_F':
                    T_RF_count += 1
                if i % 10 == 0:
                    f.write('\n')
                else:
                    f.write(',')
                i += 1
            f.write('\n' + 'T_L_S_COUNT: %d' % T_LS_count +
                    ';  T_R_S_COUNT: %d' % T_RS_count + ' .\n')
            f.write('\n' + 'T_L_F_COUNT: %d' % T_LF_count +
                    ';  T_R_F_COUNT: %d' % T_RF_count + ' .\n')
            f.write('\n')
            # 记录「NARS操作」
            f.write('NARS_PROCESS:'+'\n')
            for i in range(1, len(Constants.stats.NARS_PROCESS)+1):
                f.write(Constants.stats.NARS_PROCESS[i-1])
                if Constants.stats.NARS_PROCESS[i-1] == 'L_S':
                    N_LS_count += 1
                elif Constants.stats.NARS_PROCESS[i-1] == 'R_S':
                    N_RS_count += 1
                if Constants.stats.NARS_PROCESS[i-1] == 'L_F':
                    N_LF_count += 1
                elif Constants.stats.NARS_PROCESS[i-1] == 'R_F':
                    N_RF_count += 1
                if i % 10 == 0:
                    f.write('\n')
                else:
                    f.write(',')
                i += 1
            f.write('\n' + 'N_L_S_COUNT: %d' % N_LS_count +
                    ';  N_R_S_COUNT: %d' % N_RS_count + ' .\n')
            f.write('\n' + 'N_L_F_COUNT: %d' % N_LF_count +
                    ';  N_R_F_COUNT: %d' % N_RF_count + ' .\n')
            n1 = 0
            n2 = 0
            n3 = 0
            n4 = 0
            for r in range(0, len(Constants.stats.RESULT_DICT)):
                if Constants.stats.RESULT_DICT[r].get('NARS_start_time:') != None and n1 == 0:
                    f.write('\n'+str(Constants.stats.RESULT_DICT[r]) + ' .\n')
                    n1 += 1
                if Constants.stats.RESULT_DICT[r].get('Active>0.50_time:') != None and n2 == 0:
                    f.write('\n'+str(Constants.stats.RESULT_DICT[r]) + ' .\n')
                    n2 += 1
                if Constants.stats.RESULT_DICT[r].get('Train_during_time:') != None and n3 == 0:
                    f.write('\n'+str(Constants.stats.RESULT_DICT[r]) + ' .\n')
                    n3 += 1
                if Constants.stats.RESULT_DICT[r].get('Repeat_time:') != None and n4 == 0:
                    f.write('\n'+str(Constants.stats.RESULT_DICT[r]) + ' .\n')
                    n4 += 1
            # f.write('\n')
            # f.write('\n')
            # for l in range(0,len(Constants.stats.NARS_LINE)):
            #     f.write(str(Constants.stats.NARS_LINE[l]))

    def visdom_data(self):
        "将数据实时传入visdom进行曲线绘制"
        self.x.append(self.speeding_delta_time_s)
        self.Yn.append([Constants.stats.SUCCESS_RATE, Constants.stats.TRAIN_SUCCESS_RATE,
                       Constants.stats.NARS_SUCCESS_RATE, Constants.stats.NARS_ACTIVATION])
        self.datas.append([int(self.speeding_delta_time_s), Constants.stats.SUCCESS_RATE,
                           Constants.stats.TRAIN_SUCCESS_RATE, Constants.stats.NARS_SUCCESS_RATE, Constants.stats.NARS_ACTIVATION])
        self.viz.line(X=self.x, Y=self.Yn, win='window', opts=self.opts1)

    def babble(self):
        "随机babble"
        print("babble")
        Constants.temp.TRAIN_SIGNAL = True
        rand_int = random.randint(1, 2)
        if rand_int == 1:
            self.condition_judge('left')
            self.move_left()
        if rand_int == 2:
            self.condition_judge('right')
            self.move_right()
        Constants.temp.TRAIN_SIGNAL = False

    def given_human_train(self):
        "根据给出的序列进行人为操作"
        print("given_human_train")
        # if Constants.NARS_OP_TIMES == 0 :
        Constants.temp.TRAIN_SIGNAL = True
        if Constants.game.GIVEN_HUMAN_TRAIN_CONTENT[Constants.stats.KEY_TIMES] == 1:
            self.condition_judge('left')
            self.move_left()
        if Constants.game.GIVEN_HUMAN_TRAIN_CONTENT[Constants.stats.KEY_TIMES] == 2:
            self.condition_judge('right')
            self.move_right()
        Constants.temp.TRAIN_SIGNAL = False

    def random_babble(self):
        "负责babble的主要控制"
        print("random_babble")

        # 启动NARS并输入常识
        self.init_NARS()
        time.sleep(3)

        # pygame环境初始化
        self.init_pygame()

        # 随机babble的循环
        while True:
            self.screen.fill(Constants.display.WHITE)
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
            # 进入事件判断
            for event in pygame.event.get():
                # 共用逻辑
                self.on_common_event(event)
                # 随机babble⇒NARS Babble
                if event.type == Constants.game.RANDOM_BABBLE_EVENT:
                    if Constants.game.BABBLE_TIMES <= 0:
                        pygame.event.set_blocked(
                            Constants.game.RANDOM_BABBLE_EVENT)
                    else:
                        Constants.game.BABBLE_TIMES -= 1
                        Constants.game.BABBLE_DISPLAY_TIMES += 1
                        self.babble()
            # 更新，递进
            self.__display_text_babble()
            pygame.display.update()
            self.clock.tick(self.fps)

    def human_train(self):
        "负责人为键盘的主要控制"
        print("human_train")

        # 启动NARS并输入常识
        self.init_NARS()
        time.sleep(3)

        # pygame环境初始化
        self.init_pygame()

        # 人为操作的循环
        while True:
            self.screen.fill(Constants.display.WHITE)

            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
            for event in pygame.event.get():
                # 共用逻辑
                self.on_common_event(event)
                # 按照写入的序列进行操作
                if event.type == Constants.game.GIVEN_HUMAN_TRAIN_EVENT:
                    if Constants.stats.KEY_TIMES >= len(Constants.game.GIVEN_HUMAN_TRAIN_CONTENT):
                        pygame.event.set_blocked(
                            Constants.game.GIVEN_HUMAN_TRAIN_EVENT)
                        Constants.stats.RESULT_DICT.append(
                            {'Train_during_time:': int(self.speeding_delta_time_s)})
                        # 用于阻止人为训练时小车自主运动信号的执行
                        Constants.temp.RUN_OP_FLAG = True
                    if Constants.stats.NARS_OP_TIMES > 0:
                        pygame.event.set_blocked(
                            Constants.game.GIVEN_HUMAN_TRAIN_EVENT)
                    elif Constants.stats.KEY_TIMES >= 0 and Constants.stats.KEY_TIMES < len(Constants.game.GIVEN_HUMAN_TRAIN_CONTENT):
                        self.given_human_train()
                        Constants.stats.KEY_TIMES += 1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        Constants.stats.RESULT_DICT.append(
                            {'Train_during_time:': int(self.speeding_delta_time_s)})
                    # 左右键盘控制小车
                    if event.key == pygame.K_LEFT:
                        Constants.temp.TRAIN_SIGNAL = True
                        Constants.stats.KEY_TIMES += 1
                        self.condition_judge('left')
                        self.move_left()
                        Constants.temp.TRAIN_SIGNAL = False
                    if event.key == pygame.K_RIGHT:
                        Constants.temp.TRAIN_SIGNAL = True
                        Constants.stats.KEY_TIMES += 1
                        self.condition_judge('right')
                        self.move_right()
                        Constants.temp.TRAIN_SIGNAL = False

            self.__display_text_human()
            pygame.display.update()
            self.clock.tick(self.fps)

    def init_NARS(self):
        '''初始化NARS，启动NARS并输入常识
        - 初始化其目标
        - 初始化其传感器
        '''
        self.NARS = NARSImplementation(
            output_hook=self.on_NARS_output,  # 输出钩子
            operation_hook=self.on_NARS_operation,  # 操作钩子
        )
        self.NARS.launch(
            nars_type="opennars",
            executables_path=Constants.path.EXECUTABLE_PATH
        )
        self.NARS.add_self_status_goal('safe')  # 告知「目标是安全」
        '''原文参考
        系统输入的原初目标为“< SELF —> [safe] >.”，目的是保持自身的安全状态。
        '''
        self.NARS.add_self_sensor_existence(
            'l_sensor', 'r_sensor')  # 告知「自己有左、右传感器」
        '''原文参考
        感觉信息由小车左、右两个传感器{lsensor}与{rsensor}产生，
        并与SELF建立联结：“<SELF —> {lsensor}>.” “< SELF —> {rsensor}>.”，
        这能让OpenNARS在主观上知晓自身有两个感觉“器官”。
        
        # ! 代码相对原论文的不同点：
        # ! 在实际纳思语的表达中，
        # !     一是其顺序相反——但在逻辑上不影响：即有`<{A} --> {B}>`⇔`<{B} --> {A}>`
        # !     二是两句「自身有感官」可以被合并，即
        # ! 「传感器名称」在「l/r」和「sensor」之间添加了下划线，以便阅者区分
        '''

    def init_pygame(self):
        '''pygame环境初始化'''
        self.screen.fill(Constants.display.WHITE)
        self.game_speed = 1
        self.fps = 60 * self.game_speed
        self.clock = pygame.time.Clock()
        self.__set_timer()
        self.start_time = pygame.time.get_ticks()
        
    def init_menu(self):
        '''构建主菜单'''
        self.screen.fill(Constants.display.WHITE)

        self.menu = pygame_menu.Menu('Choose Module', Constants.display.MENU_WIDTH, Constants.display.MENU_HEIGHT,
                                     theme=pygame_menu.themes.THEME_DARK)
        self.b_b = self.menu.add.button('Random Babble', self.random_babble)
        self.menu.add.button('Human Train', self.human_train)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)

    def on_common_event(self, event):
        '''pygame中「随机Babble」「人为训练」共用的事件处理
        - 退出
        - 暂停游戏
        - 发送目标
        - 键盘按下C⇒移动墙壁
        - 键盘按下空格⇒暂停
        '''
        # QUIT事件⇒写入数据 & 退出
        if event.type == pygame.QUIT:
            self.save_and_quit()
        # 发送目标事件
        if event.type == Constants.game.SEND_GOAL_EVENT:
            self.NARS.add_self_status_goal('safe')
        # 暂停游戏事件
        if event.type == Constants.game.PAUSE_GAME_EVENT:
            pygame.mixer.Sound(
                Constants.path.ASSETS_PATH + "ding.wav").play()
            self.pause()
        if event.type == pygame.KEYDOWN:
            # C⇒移动墙壁
            if event.key == pygame.K_c:
                Constants.display.LEFT_GAP_DISTANCE -= 50
                Constants.display.RIGHT_GAP_DISTANCE -= 50
                Constants.display.LEFT_CRITICAL_DISTANCE = Constants.display.WALL_WIDTH + \
                    Constants.display.LEFT_GAP_DISTANCE  # 200
                Constants.display.RIGHT_CRITICAL_DISTANCE = Constants.display.SCREEN_WIDTH - \
                    (Constants.display.WALL_WIDTH + Constants.display.CAR_WIDTH +
                     Constants.display.RIGHT_GAP_DISTANCE)  # 300
                self.wall_1.__init__()
                self.wall_2.__init__()
            # 空格⇒暂停
            if event.key == pygame.K_SPACE:
                pygame.mixer.Sound(
                    Constants.path.ASSETS_PATH + "ding.wav").play()
                self.pause()

    def save_and_quit(self):
        '''当程序退出时
        - 一般是在 pygame.QUIT 事件中调用
        '''
        print("写入数据_quit")
        self.write_data()
        pygame.quit()
        sys.exit()

    def run(self):
        "负责游戏的运行--主控制"
        # 构建主菜单
        self.init_menu()
        # 游戏大循环
        while True:
            events = pygame.event.get()
            # 检测退出事件
            for event in events:
                if event.type == pygame.QUIT:
                    exit()  # 直接退出
            # 根据事件更新
            if self.menu.is_enabled():
                self.menu.update(events)
                self.menu.draw(self.screen)
            pygame.display.update()


def main():
    "主方法"
    game = Game()
    game.run()  # 运行游戏


# 当作为主程序运行时
if __name__ == '__main__':
    main()
