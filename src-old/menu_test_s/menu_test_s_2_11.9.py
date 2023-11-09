import random
import sys
import threading
import socket
from typing import Tuple, Any, Optional, List
from pygame.locals import *


import pygame
import pygame_menu

#定义babble事件
UPDATE_NARS_EVENT = pygame.USEREVENT + 2  # pygame事件
OPENNARS_BABBLE_EVENT = pygame.USEREVENT + 3

class Constants:
    BLACK = (0,0,0)
    WHITE = (255,255,255)

    SCREEN_WIDTH = 320  #教学内容空间（3、5、7、9），最初的预实验选择3格：也就是64*3+64*2=320
    SCREEN_HEIGHT = 350
    
    MENU_WIDTH = 300
    MENU_HEIGHT = 250
    
    WALL_WIDTH = 64
    WALL_HEIGHT = 64
    
    CAR_WIDTH = 64
    CAR_HEIGHT = 64
    
    MOVE_DISTANCE = CAR_WIDTH #小车的一个身位
   
    SUCCESS_COUNT = 0
    FAILURE_COUNT = 0
    SUM_COUNT = 0
    
    BABBLE_TIMES = 0 #11.9
    KEY_TIMES = 0  #11.9

    OP_SIGNAL = 0 #11.9

    LEFT_CRITICAL_DISTANCE = WALL_WIDTH #64
    RIGHT_CRITICAL_DISTANCE =SCREEN_WIDTH-WALL_WIDTH-CAR_WIDTH #320-64-64=192 


    main_menu: Optional['pygame_menu.Menu'] = None

class Wall_1(pygame.sprite.Sprite):#使Player继承pygame.sprite.Sprite类
    def __init__(self):#定义属性
        super().__init__()
        self.image = pygame.image.load("wall.png")
        self.rect = self.image.get_rect(top=Constants.SCREEN_HEIGHT-Constants.WALL_HEIGHT,left=0)

    def move(self):#定义行为
        pass

class Wall_2(pygame.sprite.Sprite):#使Player继承pygame.sprite.Sprite类
    def __init__(self):#定义属性
        super().__init__()
        self.image = pygame.image.load("wall.png")
        self.rect = self.image.get_rect(top=Constants.SCREEN_HEIGHT-Constants.WALL_HEIGHT,left=Constants.SCREEN_WIDTH-Constants.WALL_WIDTH)

    def move(self):#定义行为
        pass

class Car(pygame.sprite.Sprite):#使Player继承pygame.sprite.Sprite类
    def __init__(self):#定义属性
        super().__init__()
        self.image = pygame.image.load("car.png")
        x = Constants.SCREEN_WIDTH / 2
        self.rect = self.image.get_rect(center=(x,Constants.SCREEN_HEIGHT-Constants.CAR_HEIGHT*0.5))

    def move(self):
        pass

class Game:

    def __init__(self):
        pygame.init()
        size = width, height = (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT)

        pygame.display.set_caption("小车测试")
        self.screen = pygame.display.set_mode(size)

        self.car = Car()
        self.wall_1 = Wall_1()
        self.wall_2 = Wall_2()

        self.enemies = pygame.sprite.Group()
        self.enemies.add(self.wall_1)  
        self.enemies.add(self.wall_2)

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.car)
        self.all_sprites.add(self.wall_1)
        self.all_sprites.add(self.wall_2)

        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font("SimSun.ttf", 14)  # display text like scores, times, etc.
         

    def launch_thread(self):
        self.read_line_thread = threading.Thread(target=self.read_operation)
        self.read_line_thread.daemon = True  # thread dies with the exit of the program
        self.read_line_thread.start()

    def connect_nars(self, host, port):
        self.conn = socket.socket()
        self.conn.connect((host, port))
        self.nars = self.conn.makefile('rwb')
        self.launch_thread()
        #连接nars

    def update_sensors_continuous(self):
        if self.car.rect.left < 64:
            self.send_to_nars('<{lsensor} --> [dangerous]>. :|:')
            self.send_to_nars('<{rsensor} --> [safe]>. :|:')
            self.send_to_nars('<{SELF} --> [good]>. :|: %0%')
        elif self.car.rect.right > 192:
            self.send_to_nars('<{lsensor} --> [safe]>. :|:')
            self.send_to_nars('<{rsensor} --> [dangerous]>. :|:')
            self.send_to_nars('<{SELF} --> [good]>. :|: %0%')
        else:
            self.send_to_nars('<{lsensor} --> [safe]>. :|:')
            self.send_to_nars('<{rsensor} --> [safe]>. :|:')
            self.send_to_nars('<{SELF} --> [good]>. :|:')
    
    # 1是左边撞；2是右边撞；3是没有撞
    def update_sensors(self,judge_num):
        print(judge_num)
        if judge_num == 1:
            self.send_to_nars('<{lsensor} --> [dangerous]>. :|:')
            self.send_to_nars('<{rsensor} --> [safe]>. :|:')
            self.send_to_nars('<{SELF} --> [good]>. :|: %0%')
        elif judge_num == 2:
            self.send_to_nars('<{lsensor} --> [safe]>. :|:')
            self.send_to_nars('<{rsensor} --> [dangerous]>. :|:')
            self.send_to_nars('<{SELF} --> [good]>. :|: %0%')
        elif judge_num == 0:
            self.send_to_nars('<{lsensor} --> [safe]>. :|:')
            self.send_to_nars('<{rsensor} --> [safe]>. :|:')
            self.send_to_nars('<{SELF} --> [good]>. :|:')
    
    def send_to_nars(self, info):
        self.conn.send(f'{info}\n'.encode())
        print(info)
        #把信息送入nars

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
            

    def babble(self):
        print("babble")
        rand_int = random.randint(1,2)
        if rand_int == 1:
            self.condition_judge('left')
            self.move_left()
            
        if rand_int == 2:
            self.condition_judge('right')
            self.move_right()

    def move_left(self):
        if self.car.rect.x - Constants.MOVE_DISTANCE  < Constants.WALL_WIDTH: #将车的位置改变后在临界位置并且将judge = 1 传输给nars
            print("左边撞车啦！")
            self.car.rect.x = Constants.WALL_WIDTH
            self.update_sensors(1)
        else:
            print("左移后安全！")
            self.car.rect.x -= Constants.MOVE_DISTANCE
            self.update_sensors(0)
        self.send_to_nars("<(*, {SELF}) --> ^left>. :|:")
    
    def move_right(self):
        if self.car.rect.x + Constants.MOVE_DISTANCE > Constants.SCREEN_WIDTH-Constants.WALL_WIDTH-Constants.CAR_WIDTH:
            print("右边撞车啦！")
            self.car.rect.x = Constants.SCREEN_WIDTH-Constants.WALL_WIDTH-Constants.CAR_WIDTH
            self.update_sensors(2)
        else:
            print("右移后安全")
            self.car.rect.x += Constants.MOVE_DISTANCE
            self.update_sensors(0)
        self.send_to_nars("<(*, {SELF}) --> ^right>. :|:")
    
    #11.9--用于判断当前状况成功或失败
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



    def __set_timer(self):
        UPDATE_NARS_EVENT_TIMER = 200 
        OPENNARS_BABBLE_EVENT_TIMER = 2000 
        timer_update_NARS = int(UPDATE_NARS_EVENT_TIMER / self.game_speed) #
        timer_babble = int(OPENNARS_BABBLE_EVENT_TIMER / self.game_speed)
        pygame.time.set_timer(UPDATE_NARS_EVENT, timer_update_NARS)  # the activity of NARS
        pygame.time.set_timer(OPENNARS_BABBLE_EVENT, timer_babble)

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


    def random_babble(self):
        # Do the job here !
        print("random_babble")
        self.screen.fill(Constants.WHITE)

        # self.remaining_babble_times = 10  # babble时间
        self.game_speed = 1  # don't set too large, self.game_speed = 1.0 is the default speed.
        self.fps = 60 * self.game_speed
        self.clock = pygame.time.Clock()  # create a game clock
        self.__set_timer()
        self.start_time = pygame.time.get_ticks()

        while True:
            self.screen.fill(Constants.WHITE)

            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # elif event.type == UPDATE_NARS_EVENT:
                #     self.update_sensors_continuous()#不间断实时感知信息输入
                elif event.type == OPENNARS_BABBLE_EVENT:
                    if Constants.OP_SIGNAL == True:
                        pygame.event.set_blocked(OPENNARS_BABBLE_EVENT)
                    else:
                        self.babble()
                        # if pygame.sprite.spritecollideany(self.car, self.enemies):
                        #     print("撞车啦！" )
                        #     self.update_sensors()
                        Constants.BABBLE_TIMES += 1
            

            self.__display_text_babble()
            pygame.display.update()
            self.clock.tick(self.fps)

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
                if event.type == KEYDOWN:
                    Constants.KEY_TIMES += 1
                    if event.key == pygame.K_LEFT:
                        self.condition_judge('left')
                        self.move_left()
                        # if self.car.rect.x < 64 or self.car.rect.x > 192:
                        #     print("撞车啦！")
                        #     self.update_sensors()
                    if event.key == pygame.K_RIGHT:
                        self.condition_judge('right')
                        self.move_right()
                        # if self.car.rect.x < 64 or self.car.rect.x > 192:
                        #     print("撞车啦！")
                        #     self.update_sensors()
                        # self.move_right_human()
                   

            pygame.display.update()
            self.__display_text_human()
            pygame.display.update()
            self.clock.tick(self.fps)

    def run(self):
        self.screen.fill(Constants.WHITE)
        self.menu = pygame_menu.Menu('Choose Module', Constants.MENU_WIDTH, Constants.MENU_HEIGHT,
                                     theme=pygame_menu.themes.THEME_DARK)
        self.menu.add.button('Random Babble', self.random_babble)
        self.menu.add.button('Human Train', self.human_train)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)

        while True:

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()

            if self.menu.is_enabled():
                self.menu.update(events)
                self.menu.draw(self.screen)
            pygame.display.update()


if __name__ =='__main__':

    game = Game()#初始化
    game.connect_nars('127.0.0.1', 8888)  # 连接nars
    game.run()