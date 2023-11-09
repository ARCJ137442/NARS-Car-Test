import random
import sys
import threading
import socket
from typing import Tuple, Any, Optional, List
from pygame.locals import *

import pygame
import pygame_menu

# 自定义定义事件
UPDATE_NARS_EVENT = pygame.USEREVENT + 2  # pygame事件
OPENNARS_BABBLE_EVENT = pygame.USEREVENT + 3

# 存放常量的类
class Constants:
    # 颜色
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    # 屏幕大小
    SCREEN_WIDTH = 320  #教学内容空间（3、5、7、9），最初的预实验选择3格：也就是64*3+64*2=320
    SCREEN_HEIGHT = 350
    # 菜单显示大小
    MENU_WIDTH = 300
    MENU_HEIGHT = 250
    # 墙的大小
    WALL_WIDTH = 64
    WALL_HEIGHT = 64
    # 车的大小
    CAR_WIDTH = 64
    CAR_HEIGHT = 64
    # 小车移动的距离
    MOVE_DISTANCE = CAR_WIDTH # 小车的一个身位
    # 成功次数、失败次数、总次数
    SUCCESS_COUNT = 0
    FAILURE_COUNT = 0
    SUM_COUNT = 0
    # babble和键盘操作的次数
    BABBLE_TIMES = 0 # 11.9
    KEY_TIMES = 0  # 11.9
    # nars传入op操作的信号
    OP_SIGNAL = False # 11.9
    # 左右两边的临界距离坐标
    LEFT_CRITICAL_DISTANCE = WALL_WIDTH # 64
    RIGHT_CRITICAL_DISTANCE =SCREEN_WIDTH-WALL_WIDTH-CAR_WIDTH # 320-64-64=192


    main_menu: Optional['pygame_menu.Menu'] = None

# 墙体类，主要作用确定他们的位置
class Wall_1(pygame.sprite.Sprite):# 使Player继承pygame.sprite.Sprite类
    def __init__(self):# 定义属性
        super().__init__()
        self.image = pygame.image.load("wall.png")
        self.rect = self.image.get_rect(top=Constants.SCREEN_HEIGHT-Constants.WALL_HEIGHT,left=0)

    def move(self):# 定义行为
        pass

class Wall_2(pygame.sprite.Sprite):# 使Player继承pygame.sprite.Sprite类
    def __init__(self):# 定义属性
        super().__init__()
        self.image = pygame.image.load("wall.png")
        self.rect = self.image.get_rect(top=Constants.SCREEN_HEIGHT-Constants.WALL_HEIGHT,left=Constants.SCREEN_WIDTH-Constants.WALL_WIDTH)

    def move(self):# 定义行为
        pass
# 小车类，确定小车起始位置，小车移动的操作一并写入了Game类中
class Car(pygame.sprite.Sprite):#使Player继承pygame.sprite.Sprite类
    def __init__(self):# 定义属性
        super().__init__()
        self.image = pygame.image.load("car.png")
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
         
    # 开一个并行线程，负责读取nars的输出
    def launch_thread(self):
        self.read_line_thread = threading.Thread(target=self.read_operation)
        self.read_line_thread.daemon = True  # thread dies with the exit of the program
        self.read_line_thread.start()
    # 连接nars
    def connect_nars(self, host, port):
        self.conn = socket.socket()
        self.conn.connect((host, port))
        self.nars = self.conn.makefile('rwb')
        self.launch_thread()
        # 输入实验所需的常识
        #self.send_to_nars('<{SELF} --> [good]>. %0.5%') # 初始状态：NARS并不GOOD
        #self.send_to_nars('<{SELF} --> [good]>!') #  初始状态：NARS目标是让自己GOOD
        #self.send_to_nars('<[dangerous] --> [good]>. %0%') #  初始知识：危险信号会降低GOOD
        #self.send_to_nars('<[safe] --> [good]>.') #  初始状态：安全信号会提升GOOD
        self.send_to_nars('< <{lsensor} --> [dangerous]> =/> <(*, {SELF}) --> ^right> >. :|:')
        self.send_to_nars('< <{rsensor} --> [dangerous]> =/> <(*, {SELF}) --> ^left> >. :|:')
        #self.send_to_nars("<(&,^left,{lsensor}) --> [good]>?") # 认真地教育
        #self.send_to_nars("<(&,^right,{rsensor}) --> [good]>?") # 认真地教育
        #self.send_to_nars('<{SELF} --> ^right>.  %0.5%') #  初始状态：运动有利GOOD
        #self.send_to_nars('<{SELF} --> ^left>. %0.5%') #  初始状态：运动有利GOOD
    
# 如果同时开事件传送和操作后传送，给nars传入的消息太多，但是信息多并不是与其效果成正比。这段代码负责间隔0.2s持续向nars输入感知信息
    # def update_sensors_continuous(self):
    #     if self.car.rect.left < 64:
    #         self.send_to_nars('<{lsensor} --> [dangerous]>. :|:')
    #         self.send_to_nars('<{rsensor} --> [safe]>. :|:')
    #         self.send_to_nars('<{SELF} --> [good]>. :|: %0%')
    #     elif self.car.rect.right > 192:
    #         self.send_to_nars('<{lsensor} --> [safe]>. :|:')
    #         self.send_to_nars('<{rsensor} --> [dangerous]>. :|:')
    #         self.send_to_nars('<{SELF} --> [good]>. :|: %0%')
    #     else:
    #         self.send_to_nars('<{lsensor} --> [safe]>. :|:')
    #         self.send_to_nars('<{rsensor} --> [safe]>. :|:')
    #         self.send_to_nars('<{SELF} --> [good]>. :|:')
    
    # 1是左边撞；2是右边撞；3是没有撞。这段方法是根据是否撞车对nars传入不同的信息。
    def update_sensors(self,judge_num):
        print(judge_num)
        if judge_num == 1:
            self.send_to_nars('<{lsensor} --> [dangerous]>. :|:')
            self.conn.send('1\n'.encode())
            self.send_to_nars('<{rsensor} --> [safe]>. :|:')
            self.conn.send('1\n'.encode())
            self.send_to_nars('<{SELF} --> [good]>. :|: %0%')
            #self.send_to_nars('< <{lsensor} --> [dangerous]> =/> <(*, {SELF}) --> ^right> >. :|:')   # 不知道NARS自己能否生成新目标
        elif judge_num == 2:
            self.send_to_nars('<{lsensor} --> [safe]>. :|:')
            self.conn.send('1\n'.encode())
            self.send_to_nars('<{rsensor} --> [dangerous]>. :|:')
            self.conn.send('1\n'.encode())
            self.send_to_nars('<{SELF} --> [good]>. :|: %0%')
            #self.send_to_nars('< <{rsensor} --> [dangerous]> =/> <(*, {SELF}) --> ^left> >. :|:')   # 不知道NARS自己能否生成新目标
        elif judge_num == 0:
            self.send_to_nars('<{lsensor} --> [safe]>. :|:')
            self.send_to_nars('<{rsensor} --> [safe]>. :|:')
            self.send_to_nars('<{SELF} --> [good]>. :|:')
        self.conn.send('10\n'.encode())
        # self.add_inference_cycles()
        # self.send_to_nars('<{SELF} --> [good]>! :|:')

    # 给nars传入信息
    def send_to_nars(self, info):
        self.conn.send(f'{info}\n'.encode())

    def add_inference_cycles(self, num = 10):
        self.conn.send(f'{num}\n'.encode())
        #print(info)
        # 把信息送入nars

    # 读取nars输出中op的指令，以操作小车移动
    def read_operation(self):
        op = self.nars.readline().decode().strip()
        print(f'read operation: {op}'+'--------------------------------------------------!!!!!!')
        #11.9--添加nars开始输入的信号后，停止训练，所以加入一个op信号常量
        op_num = 0 
        if op != None and op_num <= 0:
            Constants.OP_SIGNAL = True
            print(Constants.OP_SIGNAL)
            op_num += 1 #执行一次之后就不再执行
        if op == "left":
            self.condition_judge('left')
            self.move_left()
        else:
            self.condition_judge('right')
            self.move_right()
    #随机babble
    def babble(self):
        print("babble")
        rand_int = random.randint(1,2)
        if rand_int == 1:
            self.condition_judge('left')#在发生操作前就判断这次操作的后果是撞车、不撞车或安全，因为位移发生后判断出随之发生错误。
            self.move_left()
            
        if rand_int == 2:
            self.condition_judge('right')
            self.move_right()

    # 如果接收到移动的指令，先向nars传入移动的信息，之后判断撞车与否，并更新此时的感知信息。
    def move_left(self):
        #print(self.car.rect.x,self.car.rect.y)
        self.send_to_nars("<(*, {SELF}) --> ^left>. :|:")#应该在给nars传入应小车移动造成的感知信息变化前告知nars发生了运动操作。
        self.send_to_nars("<{lsensor} --> {" + str(self.car.rect.x) + "}>. :|:") # 告知NARS现在左侧的位置
        self.send_to_nars("<{rsensor} --> {" + str(self.car.rect.y) + "}>. :|:") # 告知NARS现在右侧的位置
        if self.car.rect.x - Constants.MOVE_DISTANCE  < Constants.WALL_WIDTH: #将车的位置改变后在临界位置并且将judge = 1 传输给nars
            print("左边撞车啦！")
            self.send_to_nars("<{lsensor} --> {" + str(self.car.rect.x) + "}>. :|:")
            self.send_to_nars("<{" + str(self.car.rect.x) + "} --> [dangerous]>. :|:")

            self.car.rect.x = Constants.WALL_WIDTH
            self.update_sensors(1)
        else:
            print("右移后安全！")
            self.car.rect.x -= Constants.MOVE_DISTANCE
            self.update_sensors(0)
        # self.send_to_nars("<(*, {SELF}) --> ^left>. :|:")
    
    def move_right(self):
        print(self.car.rect.x,self.car.rect.y)
        # self.send_to_nars("<^right --> [good]>?")
        self.send_to_nars("<(*, {SELF}) --> ^right>. :|:")
        self.send_to_nars("<{lsensor} --> {" + str(self.car.rect.x) + "}>. :|:") # 告知NARS现在左侧的位置
        self.send_to_nars("<{rsensor} --> {" + str(self.car.rect.y) + "}>. :|:") # 告知NARS现在右侧的位置
        if self.car.rect.x + Constants.MOVE_DISTANCE > Constants.SCREEN_WIDTH-Constants.WALL_WIDTH-Constants.CAR_WIDTH:
            print("右边撞车啦！")
            self.send_to_nars("<{rsensor} --> {" + str(self.car.rect.y) + "}>. :|:")
            self.send_to_nars("<{" + str(self.car.rect.y) + "} --> [dangerous]>. :|:")

            self.car.rect.x = Constants.SCREEN_WIDTH-Constants.WALL_WIDTH-Constants.CAR_WIDTH
            self.update_sensors(2)
        else:
            print("左移后安全")
            self.car.rect.x += Constants.MOVE_DISTANCE
            self.update_sensors(0)
        # self.send_to_nars("<(*, {SELF}) --> ^right>. :|:")
    
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
        print("------------------------")
        #这个判断方式直接适用于键盘操作训练中，对于babble和nars的判断分别加在baale()和read_operation()方法中
    #事件的设置，主要用于两个自定义事件的触发
    def __set_timer(self):
        UPDATE_NARS_EVENT_TIMER = 2000 
        OPENNARS_BABBLE_EVENT_TIMER = 2000 
        timer_update_NARS = int(UPDATE_NARS_EVENT_TIMER / self.game_speed) #
        timer_babble = int(OPENNARS_BABBLE_EVENT_TIMER / self.game_speed)
        pygame.time.set_timer(UPDATE_NARS_EVENT, timer_update_NARS)  # the activity of NARS
        pygame.time.set_timer(OPENNARS_BABBLE_EVENT, timer_babble)
    #随机babble中的文字显示
    def __display_text_babble(self):
        current_time = pygame.time.get_ticks()
        delta_time_s = (current_time - self.start_time) / 1000
        speeding_delta_time_s = delta_time_s * self.game_speed

        surface_time = self.font.render('时间: %d' % speeding_delta_time_s, True, Constants.BLACK)
        surface_fps = self.font.render('FPS: %d' % self.clock.get_fps(), True, Constants.BLACK)
        surface_babbling = self.font.render('随机次数: %d' % Constants.BABBLE_TIMES, True, Constants.BLACK)
        success_count = self.font.render('成功次数：%d' % Constants.SUCCESS_COUNT, True, Constants.BLACK)
        failure_count = self.font.render('失败次数：%d' % Constants.FAILURE_COUNT, True, Constants.BLACK)
        sum_count = self.font.render('总次数：%d' % Constants.SUM_COUNT, True, Constants.BLACK)
        self.screen.blit(surface_babbling, [20, 30])
        self.screen.blit(surface_time, [150, 30])
        self.screen.blit(surface_fps, [20, 50])
        self.screen.blit(success_count, [150, 50])
        self.screen.blit(failure_count, [20, 70])
        self.screen.blit(sum_count, [150, 70])
    #人为训练中的文字显示
    def __display_text_human(self):
        current_time = pygame.time.get_ticks()
        delta_time_s = (current_time - self.start_time) / 1000
        speeding_delta_time_s = delta_time_s * self.game_speed

        surface_time = self.font.render('时间: %d' % speeding_delta_time_s, True, Constants.BLACK)
        surface_fps = self.font.render('FPS: %d' % self.clock.get_fps(), True, Constants.BLACK)
        surface_human = self.font.render('键盘操作次数: %d' % Constants.KEY_TIMES, True, Constants.BLACK)
        success_count = self.font.render('成功次数：%d' % Constants.SUCCESS_COUNT, True, Constants.BLACK)
        failure_count = self.font.render('失败次数：%d' % Constants. FAILURE_COUNT, True, Constants.BLACK)
        sum_count = self.font.render('总次数：%d' % Constants.SUM_COUNT, True, Constants.BLACK)
        self.screen.blit(surface_human, [20, 30])
        self.screen.blit(surface_time, [150, 30])
        self.screen.blit(surface_fps, [20, 50])
        self.screen.blit(success_count, [150, 50])
        self.screen.blit(failure_count, [20, 70])
        self.screen.blit(sum_count, [150, 70])

    #负责babble的主要控制
    def random_babble(self):
        # Do the job here !
        print("random_babble")
        #画面绘制
        self.screen.fill(Constants.WHITE)

        # self.remaining_babble_times = 10  # babble时间
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
                    pygame.quit()
                    sys.exit()
                elif event.type == UPDATE_NARS_EVENT:
                    self.send_to_nars('<{SELF} --> [good]>! :|:')
                elif event.type == OPENNARS_BABBLE_EVENT: #babble事件
                    if Constants.OP_SIGNAL == True:#如果nars发出op操作，那么babble事件退出；或者可以降低babble的频率。
                        pygame.event.set_blocked(OPENNARS_BABBLE_EVENT)
                    else:
                        self.babble()
                        Constants.BABBLE_TIMES += 1
            

            self.__display_text_babble()
            pygame.display.update()
            self.clock.tick(self.fps)
    #负责人为键盘的主要控制
    def human_train(self):
        # Do the job here !
        print("human_train")
        #self.send_to_nars("<(*,{SELF})-->^left>! :|:")#目标

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
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # if event.type == UPDATE_NARS_EVENT:
                #     self.update_sensors_continuous()
                #     pass
                if event.type == KEYDOWN:#接收键盘左右键操作
                    Constants.KEY_TIMES += 1
                    if event.key == pygame.K_LEFT:
                        self.condition_judge('left')
                        self.move_left()#先判断再发生位移
                    if event.key == pygame.K_RIGHT:
                        self.condition_judge('right')
                        self.move_right()
                   

            pygame.display.update()
            self.__display_text_human()
            pygame.display.update()
            self.clock.tick(self.fps)
    #负责游戏的运行--主控制
    def run(self):
        self.screen.fill(Constants.WHITE)
        #创建菜单
        self.menu = pygame_menu.Menu('Choose Module', Constants.MENU_WIDTH, Constants.MENU_HEIGHT,
                                     theme=pygame_menu.themes.THEME_DARK)
        self.menu.add.button('Random Babble', self.random_babble)#根据按钮不同，进入不同方法中
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
    game.connect_nars('127.0.0.1', 8888)  # 连接nars
    game.run()#运行游戏