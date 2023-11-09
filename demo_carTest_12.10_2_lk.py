import random
import subprocess
import signal
import sys
import threading
import time
import socket
from visdom import Visdom
import numpy as np
from typing import Container, Tuple, Any, Optional, List
from pygame.locals import *
import pandas as pd
from openpyxl import load_workbook


import pygame
import pygame_menu


# 自定义定义事件
UPDATE_NARS_EVENT = pygame.USEREVENT + 2  # pygame事件
OPENNARS_BABBLE_EVENT = pygame.USEREVENT + 3
PAUSE_GAME_EVENT = pygame.USEREVENT + 4
CHANGE_DISTANCE_EVENT = pygame.USEREVENT + 5

# 存放常量的类
class Constants:
    # 颜色
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255,0,0)
    # 屏幕大小
    SCREEN_WIDTH = 550  #教学内容空间（3、5、7、9）-->(150,100,50,0)
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
    MOVE_DISTANCE = CAR_WIDTH # 小车的一个身位
    # 成功次数、失败次数、总次数
    SUCCESS_COUNT = 0
    FAILURE_COUNT = 0
    SUM_COUNT = 0
    SUCCESS_RATE = 0.00
    # babble和键盘操作的次数
    # BABBLE_TIMES = 30 # 11.9
    KEY_TIMES = 0  # 11.9
    NARS_OP_TIMES = 0
    #babble间隔时间
    # BABBLE_EVENT_TIME = 2000  
    # nars传入op操作的信号
    OP_SIGNAL = False # 11.9
    #左右两边空白距离
    LEFT_GAP_DISTANCE = 150
    RIGHT_GAP_DISTANCE = 150
    # 左右两边的临界距离坐标
    LEFT_CRITICAL_DISTANCE = WALL_WIDTH + LEFT_GAP_DISTANCE # 100
    RIGHT_CRITICAL_DISTANCE =SCREEN_WIDTH - (WALL_WIDTH + CAR_WIDTH + RIGHT_GAP_DISTANCE) #200
    #小车成功率计算
    NARS_SUCCESS_RATE = 0.00
    NARS_SUCCESS_COUNT = 0
    NARS_FAILURE_COUNT = 0
    NARS_SUM_COUNT = 0
    NARS_ACTIVATION = 0.00

    NARS_PROCESS = []
    #训练单独成功率计算
    TRAIN_SIGNAL = False
    TRAIN_SUCCESS_RATE = 0.00
    TRAIN_SUCCESS_COUNT = 0
    TRAIN_FAILURE_COUNT = 0
    TRAIN_SUM_COUNT = 0

    TRAIN_PROCESS = []

    textList = []

    #暂停时间
    PAUSE_EVENT_TIME = 600*1000

    main_menu: Optional['pygame_menu.Menu'] = None
    #测试文件位置
    SAVE_URL = "G:/pygame_car/test.xlsx"
    # SHEET_NAME = sys.argv[1] 
    #结果保存位置
    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/1_1_data.xlsx" 
    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/1_2_data.xlsx" 
    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/1_3_data.xlsx" 
    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/1_4_data.xlsx" 
    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/1_5_data.xlsx" 
    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/1_6_data.xlsx" 

    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/2_1_data.xlsx" 
    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/2_2_data.xlsx" 
    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/2_3_data.xlsx" 
    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/2_4_data.xlsx" 
    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/2_5_data.xlsx" 
    # SAVE_URL = "E:/渤海大学/小车/12.4小车实验数据_v2/2_6_data.xlsx"  

    #十次重复实验
    SHEET_NAME = 'No.1'
    # SHEET_NAME = 'No.2'
    # SHEET_NAME = 'No.3'
    # SHEET_NAME = 'No.4'
    # SHEET_NAME = 'No.5'
    # SHEET_NAME = 'No.6'
    # SHEET_NAME = 'No.7'
    # SHEET_NAME = 'No.8'
    # SHEET_NAME = 'No.9'
    # SHEET_NAME = 'No.10'
    
    #实验一变量
    BABBLE_DISPLAY_TIMES = 0
    #1
    BABBLE_TIMES = 10
    BABBLE_EVENT_TIME = 3000
    # #2
    # BABBLE_TIMES = 20
    # BABBLE_EVENT_TIME = 1500
    # #3
    # BABBLE_TIMES = 30
    # BABBLE_EVENT_TIME = 1000
    # #4
    # BABBLE_TIMES = 10
    # BABBLE_EVENT_TIME = 6000
    # #5
    # BABBLE_TIMES = 20
    # BABBLE_EVENT_TIME = 3000
    # #6
    # BABBLE_TIMES = 30
    # BABBLE_EVENT_TIME = 2000

# 墙体类，主要作用确定他们的位置
class Wall_1(pygame.sprite.Sprite):# 使Player继承pygame.sprite.Sprite类
    def __init__(self):# 定义属性
        super().__init__()
        self.image = pygame.image.load("wall_50px.png")
        self.rect = self.image.get_rect(top=Constants.SCREEN_HEIGHT-Constants.WALL_HEIGHT,left=Constants.LEFT_GAP_DISTANCE)

    def move(self):# 定义行为
        pass

class Wall_2(pygame.sprite.Sprite):# 使Player继承pygame.sprite.Sprite类
    def __init__(self):# 定义属性
        super().__init__()
        self.image = pygame.image.load("wall_50px.png")
        self.rect = self.image.get_rect(top=Constants.SCREEN_HEIGHT-Constants.WALL_HEIGHT,left=Constants.SCREEN_WIDTH-Constants.WALL_WIDTH-Constants.RIGHT_GAP_DISTANCE)

    def move(self):# 定义行为
        pass
# 小车类，确定小车起始位置，小车移动的操作一并写入了Game类中
class Car(pygame.sprite.Sprite):#使Player继承pygame.sprite.Sprite类
    def __init__(self):# 定义属性
        super().__init__()
        self.image = pygame.image.load("car_50px.png")
        x = Constants.SCREEN_WIDTH / 2
        self.rect = self.image.get_rect(center=(x,Constants.SCREEN_HEIGHT-Constants.CAR_HEIGHT*0.5))

    def move(self):
        pass


# 游戏类
class Game:
    # 游戏的初始化方法，主要负责游戏前的准备工作
    def __init__(self):
        pygame.init()
        size = width, height = (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT)

        pygame.display.set_caption("小车测试")
        self.screen = pygame.display.set_mode(size)

        self.car = Car()
        self.wall_1 = Wall_1()
        self.wall_2 = Wall_2()
        self.inference_rate = 10

        self.enemies = pygame.sprite.Group()
        self.enemies.add(self.wall_1)  
        self.enemies.add(self.wall_2)

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.car)
        self.all_sprites.add(self.wall_1)
        self.all_sprites.add(self.wall_2)

        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font("SimSun.ttf", 14)  # display text like scores, times, etc.

        self.viz = Visdom(env='carTest')
        self.opts1 = {
            "title": '实验二：训练方式',
            "xlabel":'时间(s)',
            "ylabel":'小车避障成功率(%)',
            "width":600,
            "height":500,
            "legend":['总成绩','训练成绩','学习成绩','NARS活跃度']
        }
        self.x = []
        self.Yn = []
        self.A = [] #用于结果存入excel
        self.train_process_str = ''
        self.str_name = ['str1','str2','str3','str4','str5','str6']

    # 开一个并行线程，负责读取nars的输出
    def launch_thread(self):
        self.read_line_thread = threading.Thread(target=self.read_operation,
                                                 args=(self.process.stdout,))
        self.read_line_thread.daemon = True  # thread dies with the exit of the program
        self.read_line_thread.start()

    # 连接nars
    def launch_nars(self, nars_type):
        self.process = subprocess.Popen(["cmd"], bufsize=1,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        universal_newlines=True,  
                                        shell=False)
        if nars_type == "opennars":
            self.send_to_nars('java -cp "*" org.opennars.main.Shell')
        elif nars_type == 'ONA':
            self.send_to_nars('NAR shell')
        elif nars_type == "xiangnars":
            self.send_to_nars('java -cp "*" nars.main_nogui.Shell')
        self.send_to_nars('*volume=0')
        self.launch_thread()

    def process_kill(self):
        self.process.send_signal(signal.CTRL_C_EVENT)
        self.process.terminate()

    # 给nars传入信息
    def send_to_nars(self, str):
        self.process.stdin.write(str + '\n')
        self.process.stdin.flush()

    def read_operation(self,out):
        for line in iter(out.readline, b'\n'):  # get operations
            # 抑制实验
            current_time = pygame.time.get_ticks()
            Timer = (current_time - Constants.Start_time) / 1000
            #print("Timer = " + str(Timer))
            if Timer > 0.0 and Timer < 3.0:
                print("主动经验屏蔽：" + line + str(Timer))
                continue
            if line[0:3] == 'EXE':
                subline = line.split(' ',2)[2]
                operation = subline.split('(',1)[0]
                print(operation)
                if operation == '^left':
                    Constants.OP_SIGNAL = True
                    self.condition_judge('left')
                    self.move_left()
                    Constants.NARS_OP_TIMES += 1
                    Constants.OP_SIGNAL = False
                if operation == '^right':
                    Constants.OP_SIGNAL = True
                    self.condition_judge('right')
                    self.move_right()
                    Constants.NARS_OP_TIMES += 1
                    Constants.OP_SIGNAL = False
                
        out.close()

    #随机babble
    def babble(self):
        print("babble")
        Constants.TRAIN_SIGNAL = True
        rand_int = random.randint(1,2)
        if rand_int == 1:
            self.condition_judge('left')
            self.move_left()
            #在发生操作前就判断这次操作的后果是撞车、不撞车或安全，因为位移发生后判断出随之发生错误
        if rand_int == 2:
            self.condition_judge('right')
            self.move_right()
        Constants.TRAIN_SIGNAL = False
            
            

    # 如果接收到移动的指令，先向nars传入移动的信息，之后判断撞车与否，并更新此时的感知信息。
    def move_left(self):
        # 精神运动
        self.getSensor()
        self.send_to_nars("<(*, {SELF}) --> ^left>. :|:")#应该在给nars传入应小车移动造成的感知信息变化前告知nars发生了运动操作。
        #self.getSensor()
        # 这里也许有推理时间
        if self.car.rect.x - Constants.MOVE_DISTANCE  < (Constants.WALL_WIDTH+Constants.LEFT_GAP_DISTANCE): 
            # 物理运动
            self.car.rect.x = Constants.WALL_WIDTH + Constants.LEFT_GAP_DISTANCE
            # 感知变化
            self.getSensor()
            # 结果
            self.send_to_nars("<{SELF} --> [safe]>. :|: %0% ")
        else:
            # 物理运动
            self.car.rect.x -= Constants.MOVE_DISTANCE
            # 感知变化
            self.getSensor()
            # 结果
            self.send_to_nars("<{SELF} --> [safe]>. :|:")
        self.visdom_data()
        
    
    def move_right(self):
        # 运动发生
        self.getSensor()
        self.send_to_nars("<(*, {SELF}) --> ^right>. :|:")

        if self.car.rect.x + Constants.MOVE_DISTANCE > Constants.SCREEN_WIDTH-Constants.WALL_WIDTH-Constants.CAR_WIDTH-Constants.LEFT_GAP_DISTANCE:
            # 物理运动
            self.car.rect.x = Constants.SCREEN_WIDTH-Constants.WALL_WIDTH-Constants.CAR_WIDTH-Constants.LEFT_GAP_DISTANCE
            # 感知变化
            self.getSensor()
            # 运动发生引发感知变化的结果
            self.send_to_nars("<{SELF} --> [safe]>. :|: %0% ")
        else:
            self.car.rect.x += Constants.MOVE_DISTANCE
            # 感知变化
            self.getSensor()
            # 引发结果
            self.send_to_nars("<{SELF} --> [safe]>. :|: ")
        self.visdom_data()

    def getSensor(self):
        print("L-sensor --> [" + str(self.car.rect.x - self.wall_1.rect.x + Constants.WALL_WIDTH) + "]")
        print("R-sensor --> [" + str(self.wall_2.rect.x - (self.car.rect.x + Constants.CAR_WIDTH)) + "]")
        self.send_to_nars("<{lsensor} --> [" + str(self.car.rect.x - self.wall_1.rect.x + Constants.WALL_WIDTH) + "]>. :|:")  # 告知NARS现在左侧的位置
        self.send_to_nars("<{rsensor} --> [" + str(self.wall_2.rect.x - (self.car.rect.x + Constants.CAR_WIDTH)) + "]>. :|:")  # 告知NARS现在右侧的位置

    #11.9--用于判断位于临界位置时操作发生的后果时成功或失败
    def condition_judge(self,key_value):
        print("------------------------")
        print("Enter in condition judge")
        print(key_value)
        print(self.car.rect.x)

        if self.car.rect.x == Constants.LEFT_CRITICAL_DISTANCE and key_value == 'left':
            print("失败！")
            Constants.FAILURE_COUNT += 1
        if self.car.rect.x == Constants.LEFT_CRITICAL_DISTANCE and key_value == 'right':
            print("成功！")
            Constants.SUCCESS_COUNT += 1
        if self.car.rect.x == Constants.RIGHT_CRITICAL_DISTANCE and key_value =='left':
            print("成功")
            Constants.SUCCESS_COUNT += 1
        if self.car.rect.x == Constants.RIGHT_CRITICAL_DISTANCE and key_value == 'right':
            print("失败")
            Constants.FAILURE_COUNT += 1
        if self.car.rect.x == Constants.LEFT_CRITICAL_DISTANCE or self.car.rect.x == Constants.RIGHT_CRITICAL_DISTANCE:
            Constants.SUM_COUNT += 1
        if Constants.SUM_COUNT > 0:
                Constants.SUCCESS_RATE = round(Constants.SUCCESS_COUNT/Constants.SUM_COUNT,2)
        #添加nars独自操作的成功率
        if Constants.OP_SIGNAL == True:
            if self.car.rect.x == Constants.LEFT_CRITICAL_DISTANCE and key_value == 'left':
                print("左侧NARS失败！")
                Constants.NARS_FAILURE_COUNT +=1
                Constants.NARS_PROCESS.append('L_F')
            if self.car.rect.x == Constants.LEFT_CRITICAL_DISTANCE and key_value == 'right':
                print("左侧NARS成功！")
                Constants.NARS_SUCCESS_COUNT +=1
                Constants.NARS_PROCESS.append('L_S')
            if self.car.rect.x == Constants.RIGHT_CRITICAL_DISTANCE and key_value =='left':
                print("右侧NARS成功")
                Constants.NARS_SUCCESS_COUNT +=1
                Constants.NARS_PROCESS.append('R_S')
            if self.car.rect.x == Constants.RIGHT_CRITICAL_DISTANCE and key_value == 'right':
                print("右侧NARS失败")
                Constants.NARS_FAILURE_COUNT += 1
                Constants.NARS_PROCESS.append('R_F')
            if self.car.rect.x == Constants.LEFT_CRITICAL_DISTANCE or self.car.rect.x == Constants.RIGHT_CRITICAL_DISTANCE:
                Constants.NARS_SUM_COUNT += 1
            if Constants.NARS_SUM_COUNT > 0:
                Constants.NARS_SUCCESS_RATE = round(Constants.NARS_SUCCESS_COUNT/Constants.NARS_SUM_COUNT,2)
        #计算训练单独成功率
        if Constants.TRAIN_SIGNAL == True:
            if self.car.rect.x == Constants.LEFT_CRITICAL_DISTANCE and key_value == 'left':
                print("左侧训练失败！")
                Constants.TRAIN_FAILURE_COUNT +=1
                Constants.TRAIN_PROCESS.append('L_F')
            if self.car.rect.x == Constants.LEFT_CRITICAL_DISTANCE and key_value == 'right':
                print("左侧训练成功！")
                Constants.TRAIN_SUCCESS_COUNT +=1
                Constants.TRAIN_PROCESS.append('L_S')
            if self.car.rect.x == Constants.RIGHT_CRITICAL_DISTANCE and key_value =='left':
                print("右侧训练成功")
                Constants.TRAIN_SUCCESS_COUNT +=1
                Constants.TRAIN_PROCESS.append('R_S')
            if self.car.rect.x == Constants.RIGHT_CRITICAL_DISTANCE and key_value == 'right':
                print("右侧训练失败")
                Constants.TRAIN_FAILURE_COUNT += 1
                Constants.TRAIN_PROCESS.append('R_F')
            if self.car.rect.x == Constants.LEFT_CRITICAL_DISTANCE or self.car.rect.x == Constants.RIGHT_CRITICAL_DISTANCE:
                Constants.TRAIN_SUM_COUNT += 1
            if Constants.TRAIN_SUM_COUNT > 0:
                Constants.TRAIN_SUCCESS_RATE = round(Constants.TRAIN_SUCCESS_COUNT/Constants.TRAIN_SUM_COUNT,2)
            # print(Constants.TRAIN_PROCESS)
        print("------------------------")
        #这个判断方式直接适用于键盘操作训练中，对于babble和nars的判断分别加在baale()和read_operation()方法中
    #事件的设置，主要用于两个自定义事件的触发
    def __set_timer(self):
        UPDATE_NARS_EVENT_TIMER = 1000 
        OPENNARS_BABBLE_EVENT_TIMER = Constants.BABBLE_EVENT_TIME
        PAUSE_GAME_EVENT_TIMER = Constants.PAUSE_EVENT_TIME
        timer_update_NARS = int(UPDATE_NARS_EVENT_TIMER / self.game_speed) #
        timer_babble = int(OPENNARS_BABBLE_EVENT_TIMER / self.game_speed)
        timer_pause = int(PAUSE_GAME_EVENT_TIMER / self.game_speed)
        pygame.time.set_timer(UPDATE_NARS_EVENT, timer_update_NARS)  # the activity of NARS
        pygame.time.set_timer(OPENNARS_BABBLE_EVENT, timer_babble)
        pygame.time.set_timer(PAUSE_GAME_EVENT, timer_pause)

    def print_process(self,process,init_width,init_height,type):
        height = init_height
        x = len(process)//10 + 1
        if x == 1:
            self.train_process_str = '' 
            for m in range(0,len(process)):
                self.train_process_str = self.train_process_str + '->' + process[m]
            train_process = self.font.render(self.train_process_str,True, Constants.BLACK)
            self.screen.blit(train_process,[init_width,init_height])
        elif x >= 2  and x <= 4:
            start = 0
            end = 10
            for i in range(0,x):
                self.train_process_str = '' 
                for j in range(start,end):
                    self.train_process_str = self.train_process_str +'->' + process[j]
                    j += 1
                i += 1
                if 10*i < len(process):
                    start = 10*i
                if 10*(i+1) > len(process):
                    end = len(process)
                else:
                    end = 10*(i+1)  
                train_process = self.font.render(self.train_process_str,True, Constants.BLACK)
                self.screen.blit(train_process,[init_width,height])
                height = height + 15
                self.train_process_str = '' 
        elif x > 4:
            start = 10*(x-1)
            if start+10 > len(process):
                end = len(process)
            elif start+10 <= len(process):
                end = start + 10
            for i in range(0,4):
                self.train_process_str = '' 
                for j in range(start,end):
                    self.train_process_str = self.train_process_str +'->' + process[j]
                    j += 1
                i += 1
                if 10*i < len(process):
                    start = 10*i
                if 10*(i+1) > len(process):
                    end = len(process)
                else:
                    end = 10*(i+1)  
                train_process = self.font.render(self.train_process_str,True, Constants.BLACK)
                self.screen.blit(train_process,[init_width,height])
                height = height + 15
                self.train_process_str = '' 

    #随机babble中的文字显示
    def __display_text_babble(self):
        current_time = pygame.time.get_ticks()
        delta_time_s = (current_time - self.start_time) / 1000
        self.speeding_delta_time_s = delta_time_s * self.game_speed

        time = self.font.render('时间: %d' % self.speeding_delta_time_s, True, Constants.BLACK)

        babbling = self.font.render('随机训练次数: %d' % Constants.BABBLE_DISPLAY_TIMES, True, Constants.BLACK)
        train_success_count = self.font.render('训练成功次数：%d' % Constants.TRAIN_SUCCESS_COUNT, True, Constants.BLACK)
        train_failure_count = self.font.render('训练失败次数：%d' % Constants.TRAIN_FAILURE_COUNT, True, Constants.BLACK)
        train_sum_count = self.font.render('训练总次数：%d' % Constants.TRAIN_SUM_COUNT, True, Constants.BLACK)
        train_success_rate = self.font.render('训练成功率：%.2f' % Constants.TRAIN_SUCCESS_RATE,True, Constants.BLACK)
        
        self.print_process(Constants.TRAIN_PROCESS,70,100,'train')

        nars_op = self.font.render('NARS次数: %d' % Constants.NARS_OP_TIMES, True, Constants.BLACK)
        if Constants.NARS_OP_TIMES > 0:
            Constants.NARS_ACTIVATION = round(Constants.NARS_OP_TIMES/self.speeding_delta_time_s,2)
        nars_activation = self.font.render('NARS活跃度: %.2f' % Constants.NARS_ACTIVATION, True, Constants.BLACK)
        nars_success_count = self.font.render('NARS成功次数：%d' % Constants.NARS_SUCCESS_COUNT, True, Constants.BLACK)
        nars_failure_count = self.font.render('NARS失败次数：%d' % Constants.NARS_FAILURE_COUNT, True, Constants.BLACK)
        nars_sum_count = self.font.render('NARS总次数：%d' % Constants.NARS_SUM_COUNT, True, Constants.BLACK)
        nars_success_rate = self.font.render('NARS成功率：%.2f' % Constants.NARS_SUCCESS_RATE,True, Constants.BLACK)

        self.print_process(Constants.NARS_PROCESS,70,220,'nars')

        success_count = self.font.render('成功次数：%d' % Constants.SUCCESS_COUNT, True, Constants.BLACK)
        failure_count = self.font.render('失败次数：%d' % Constants.FAILURE_COUNT, True, Constants.BLACK)
        sum_count = self.font.render('总次数：%d' % Constants.SUM_COUNT, True, Constants.BLACK)
        success_rate = self.font.render('成功率：%.2f' % Constants.SUCCESS_RATE,True, Constants.BLACK)
        
        self.screen.blit(time, [70, 10])

        self.screen.blit(babbling, [70, 40])
        self.screen.blit(train_success_count,[320,40])
        self.screen.blit(train_failure_count,[70,60]) 
        self.screen.blit(train_sum_count,[320,60])
        self.screen.blit(train_success_rate,[70,80])

        self.screen.blit(nars_op,[70,160])
        self.screen.blit(nars_activation,[320,160])
        self.screen.blit(nars_success_count,[70,180])
        self.screen.blit(nars_failure_count,[320,180]) 
        self.screen.blit(nars_sum_count,[70,200])
        self.screen.blit(nars_success_rate,[320,200])

        self.screen.blit(success_count, [70, 300])
        self.screen.blit(failure_count, [320, 300])
        self.screen.blit(sum_count, [70, 320])
        self.screen.blit(success_rate, [320,320])
           

           
    #人为训练中的文字显示
    def __display_text_human(self):
        current_time = pygame.time.get_ticks()
        delta_time_s = (current_time - self.start_time) / 1000
        self.speeding_delta_time_s = delta_time_s * self.game_speed

        time = self.font.render('时间: %d' % self.speeding_delta_time_s, True, Constants.BLACK)

        babbling = self.font.render('键盘训练次数: %d' % Constants.KEY_TIMES, True, Constants.BLACK)
        train_success_count = self.font.render('训练成功次数：%d' % Constants.TRAIN_SUCCESS_COUNT, True, Constants.BLACK)
        train_failure_count = self.font.render('训练失败次数：%d' % Constants.TRAIN_FAILURE_COUNT, True, Constants.BLACK)
        train_sum_count = self.font.render('训练总次数：%d' % Constants.TRAIN_SUM_COUNT, True, Constants.BLACK)
        train_success_rate = self.font.render('训练成功率：%.2f' % Constants.TRAIN_SUCCESS_RATE,True, Constants.BLACK)

        self.print_process(Constants.TRAIN_PROCESS,70,100,'train')

        nars_op = self.font.render('NARS次数: %d' % Constants.NARS_OP_TIMES, True, Constants.BLACK)
        if Constants.NARS_OP_TIMES > 0:
            Constants.NARS_ACTIVATION = round(Constants.NARS_OP_TIMES/self.speeding_delta_time_s,2)
        nars_activation = self.font.render('NARS活跃度: %.2f' % Constants.NARS_ACTIVATION, True, Constants.BLACK)
        nars_success_count = self.font.render('NARS成功次数：%d' % Constants.NARS_SUCCESS_COUNT, True, Constants.BLACK)
        nars_failure_count = self.font.render('NARS失败次数：%d' % Constants.NARS_FAILURE_COUNT, True, Constants.BLACK)
        nars_sum_count = self.font.render('NARS总次数：%d' % Constants.NARS_SUM_COUNT, True, Constants.BLACK)
        nars_success_rate = self.font.render('NARS成功率：%.2f' % Constants.NARS_SUCCESS_RATE,True, Constants.BLACK)

        self.print_process(Constants.NARS_PROCESS,70,220,'nars')

        success_count = self.font.render('成功次数：%d' % Constants.SUCCESS_COUNT, True, Constants.BLACK)
        failure_count = self.font.render('失败次数：%d' % Constants.FAILURE_COUNT, True, Constants.BLACK)
        sum_count = self.font.render('总次数：%d' % Constants.SUM_COUNT, True, Constants.BLACK)
        success_rate = self.font.render('成功率：%.2f' % Constants.SUCCESS_RATE,True, Constants.BLACK)
        
        self.screen.blit(time, [70, 10])

        self.screen.blit(babbling, [70, 40])
        self.screen.blit(train_success_count,[320,40])
        self.screen.blit(train_failure_count,[70,60]) 
        self.screen.blit(train_sum_count,[320,60])
        self.screen.blit(train_success_rate,[70,80])

        self.screen.blit(nars_op,[70,160])
        self.screen.blit(nars_activation,[320,160])
        self.screen.blit(nars_success_count,[70,180])
        self.screen.blit(nars_failure_count,[320,180]) 
        self.screen.blit(nars_sum_count,[70,200])
        self.screen.blit(nars_success_rate,[320,200])

        self.screen.blit(success_count, [70, 300])
        self.screen.blit(failure_count, [320, 300])
        self.screen.blit(sum_count, [70, 320])
        self.screen.blit(success_rate, [320,320])

    #暂停游戏画面
    def pause(self):
        self.is_pause = True
        
        while self.is_pause == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == PAUSE_GAME_EVENT:
                    self.is_pause = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_pause = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()
        pygame.display.update()
        self.clock.tick(5)
    
    def write_data(self):
        print("enter in write_data")
        header = ["时间", "总成绩", "训练成绩", "学习成绩",'NARS活跃度']
        writer = pd.ExcelWriter(Constants.SAVE_URL,engine='openpyxl')
        book = load_workbook(Constants.SAVE_URL)
        writer.book = book
        data = pd.DataFrame(self.A, columns=header)
        data.to_excel(writer, sheet_name= Constants.SHEET_NAME,index=False)
        writer.save()
        print("数据写入完毕！")
    
    def visdom_data(self):
        self.x.append(self.speeding_delta_time_s)
        self.Yn.append([Constants.SUCCESS_RATE,Constants.TRAIN_SUCCESS_RATE,Constants.NARS_SUCCESS_RATE,Constants.NARS_ACTIVATION])
        self.A.append([int(self.speeding_delta_time_s),Constants.SUCCESS_RATE,Constants.TRAIN_SUCCESS_RATE,Constants.NARS_SUCCESS_RATE,Constants.NARS_ACTIVATION])
        self.viz.line(X=self.x, Y=self.Yn, win='window', opts=self.opts1)

    #负责babble的主要控制
    def random_babble(self):
        # Do the job here !
        print("random_babble")
        #画面绘制
        self.screen.fill(Constants.WHITE)
        self.game_speed = 1  # don't set too large, self.game_speed = 1.0 is the default speed.
        self.fps = 60 * self.game_speed
        self.clock = pygame.time.Clock()  # create a game clock
        self.__set_timer()
        self.start_time = pygame.time.get_ticks()
        #随机babble的循环
        while True:
            self.screen.fill(Constants.WHITE)
            #绘制游戏中所有角色
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
            #进入事件判断
            for event in pygame.event.get():
                if event.type == pygame.QUIT:#关闭游戏
                    print("写入数据_quit")
                    self.write_data()
                    pygame.quit()
                    sys.exit()
                if event.type == PAUSE_GAME_EVENT:
                    pygame.mixer.Sound("ding.wav").play()
                    self.pause()
                    # time.sleep(10)
                    # print("写入数据_pause")
                    # self.write_data()
                    # pygame.quit()
                    # sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        Constants.LEFT_GAP_DISTANCE -= 50
                        Constants.RIGHT_GAP_DISTANCE -= 50
                        Constants.LEFT_CRITICAL_DISTANCE = Constants.WALL_WIDTH + Constants.LEFT_GAP_DISTANCE
                        Constants.RIGHT_CRITICAL_DISTANCE = Constants.SCREEN_WIDTH - (Constants.WALL_WIDTH + Constants.CAR_WIDTH + Constants.RIGHT_GAP_DISTANCE)
                        self.wall_1.__init__()
                        self.wall_2.__init__()
                    if event.key == pygame.K_SPACE:
                        pygame.mixer.Sound("ding.wav").play()
                        self.pause()
                if event.type == UPDATE_NARS_EVENT:
                    self.send_to_nars('<{SELF} --> [safe]>! :|:')
                if event.type == OPENNARS_BABBLE_EVENT: #babble事件
                    if Constants.BABBLE_TIMES <= 0:
                        pygame.event.set_blocked(OPENNARS_BABBLE_EVENT)
                    else:
                        Constants.BABBLE_TIMES -= 1
                        Constants.BABBLE_DISPLAY_TIMES += 1
                        self.babble()
            self.__display_text_babble()
            pygame.display.update()
            self.clock.tick(self.fps)
        
    #负责人为键盘的主要控制
    def human_train(self):
        # Do the job here !
        print("human_train")

        self.screen.fill(Constants.WHITE)

        self.game_speed = 1  # don't set too large, self.game_speed = 1.0 is the default speed.
        self.fps = 60 * self.game_speed
        self.clock = pygame.time.Clock()  # create a game clock
        self.__set_timer()
        self.start_time = pygame.time.get_ticks()
        #人为操作的循环
        
        while True:
            self.screen.fill(Constants.WHITE)
            
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:#关闭游戏
                    print("写入数据")
                    self.write_data()
                    pygame.quit()               
                    sys.exit()
                if event.type == UPDATE_NARS_EVENT:
                    self.send_to_nars('<{SELF} --> [safe]>! :|:')
                    #传送信息
                    self.visdom_data()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        Constants.LEFT_GAP_DISTANCE -= 50
                        Constants.RIGHT_GAP_DISTANCE -= 50
                        Constants.LEFT_CRITICAL_DISTANCE = Constants.WALL_WIDTH + Constants.LEFT_GAP_DISTANCE
                        Constants.RIGHT_CRITICAL_DISTANCE = Constants.SCREEN_WIDTH - (Constants.WALL_WIDTH + Constants.CAR_WIDTH + Constants.RIGHT_GAP_DISTANCE)
                        self.wall_1.__init__()
                        self.wall_2.__init__()
                    if event.key == pygame.K_LEFT:
                        Constants.TRAIN_SIGNAL = True
                        Constants.KEY_TIMES += 1
                        self.condition_judge('left')
                        self.move_left()#先判断再发生位移
                        Constants.TRAIN_SIGNAL = False
                    if event.key == pygame.K_RIGHT:
                        Constants.TRAIN_SIGNAL = True
                        Constants.KEY_TIMES += 1
                        self.condition_judge('right')
                        self.move_right() 
                        Constants.TRAIN_SIGNAL = False
                    if event.key == pygame.K_SPACE:
                        pygame.mixer.Sound("ding.wav").play()
                        self.pause()
            self.__display_text_human()
            pygame.display.update()
            self.clock.tick(self.fps)
    #负责游戏的运行--主控制
    def run(self):
        self.screen.fill(Constants.WHITE)
        #创建菜单
        self.menu = pygame_menu.Menu('Choose Module', Constants.MENU_WIDTH, Constants.MENU_HEIGHT,
                                     theme=pygame_menu.themes.THEME_DARK)
        self.b_b = self.menu.add.button('Random Babble', self.random_babble)#根据按钮不同，进入不同方法中
        self.menu.add.button('Human Train', self.human_train)
        self.menu.add.button('Quit', pygame_menu.events.EXIT) 
        #游戏大循环
        while True:
            #接收信息：若退出则关闭页面
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()
            #若菜单可用，按照菜单内容进入不同方法中
            if self.menu.is_enabled():
                self.menu.update(events)
                self.menu.draw(self.screen)
            pygame.display.update()

        

#主方法
if __name__ =='__main__':

    game = Game()#初始化
    game.launch_nars("opennars")
    #常识输入
    game.send_to_nars('<{SELF} --> [safe] >! :|:')
    game.send_to_nars('<{lsensor, rsensor} --> {SELF} >. :|:')
    game.run()#运行游戏