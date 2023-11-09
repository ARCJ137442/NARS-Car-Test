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
    SCREEN_WIDTH = 700
    SCREEN_HEIGHT = 350
    MENU_WIDTH = 350
    MENU_HEIGHT = 250

    main_menu: Optional['pygame_menu.Menu'] = None

class Wall_1(pygame.sprite.Sprite):#使Player继承pygame.sprite.Sprite类
    def __init__(self):#定义属性
        super().__init__()
        self.image = pygame.image.load("wall.png")
        self.rect = self.image.get_rect(top=286,left=0)

    def move(self):#定义行为
        pass

class Wall_2(pygame.sprite.Sprite):#使Player继承pygame.sprite.Sprite类
    def __init__(self):#定义属性
        super().__init__()
        self.image = pygame.image.load("wall.png")
        self.rect = self.image.get_rect(top=286,left=636)

    def move(self):#定义行为
        pass

class Car(pygame.sprite.Sprite):#使Player继承pygame.sprite.Sprite类
    def __init__(self):#定义属性
        super().__init__()
        self.image = pygame.image.load("car.png")
        x = Constants.SCREEN_WIDTH / 2
        self.rect = self.image.get_rect(center=(x,318))

    def move(self):#定义行为
        pressed_keys = pygame.key.get_pressed()  # 键盘操作
        if pressed_keys[K_LEFT] and self.rect.left >= 64:  # 这里的K_LEFT来自于locals
            self.move_left()
        if pressed_keys[K_RIGHT] and self.rect.right <= 636:
            self.move_right()

    def move_left(self):
        self.rect.move_ip(-254,0)

    def move_right(self):
        self.rect.move_ip(254,0)
class Game:

    def __init__(self):
        pygame.init()
        size = width, height = (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT)

        pygame.display.set_caption("小车测试")
        self.screen = pygame.display.set_mode(size)

        # 定义玩家对象
        self.car = Car()
        self.wall_1 = Wall_1()
        self.wall_2 = Wall_2()

        # 定义精灵组
        self.enemies = pygame.sprite.Group()
        self.enemies.add(self.wall_1)  # 稍后会对这个里的所有对象进行是否碰撞到的判断
        self.enemies.add(self.wall_2)

        # 所有经历放在其中
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.car)
        self.all_sprites.add(self.wall_1)
        self.all_sprites.add(self.wall_2)

        #创建一个时钟
        self.clock = pygame.time.Clock()
        # 并行的线程只负责读

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

    def read_operation(self):
        op = self.nars.readline().decode().strip()
        print(f'read operation: {op}')
        if op == "left":
            self.move_left()
        else:
            self.move_right()

    def move_left(self):
        print("babble_move_left")
        self.car.move_left()

    def move_right(self):
        print("babble_move_right")
        self.car.move_right()


    def send_to_nars(self, info):
        self.conn.send(f'{info}\n'.encode())
        print(info)
        #把信息送入nars

    def update_sensors(self):
        if self.car.rect.left <= 64:
            self.send_to_nars('<{lsensor} --> [dangerous]>. :|:')
            self.send_to_nars('<{rsensor} --> [safe]>. :|:')
            self.send_to_nars('<{SELF} --> [good]>. :|: %0%')
        elif self.car.rect.right >= 636:
            self.send_to_nars('<{lsensor} --> [safe]>. :|:')
            self.send_to_nars('<{rsensor} --> [dangerous]>. :|:')
            self.send_to_nars('<{SELF} --> [good]>. :|: %0%')
        else:
            self.send_to_nars('<{lsensor} --> [safe]>. :|:')
            self.send_to_nars('<{rsensor} --> [safe]>. :|:')
            self.send_to_nars('<{SELF} --> [good]>. :|:')

    def babble(self):
        print("babble")
        rand_int = random.randint(1,2)
        if rand_int == 1:
            self.send_to_nars('<(*,{SELF}) --> ^left>. :|:')
            self.move_left()
        if rand_int == 2:
            self.send_to_nars('<(*,{SELF}) --> ^right>. :|:')
            self.move_right()

    def __set_timer(self):
        UPDATE_NARS_EVENT_TIMER = 200  #200个单位更新NARS的通道信息
        OPENNARS_BABBLE_EVENT_TIMER = 4000 #4000个单位发送babble指令
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
        surface_babbling = self.font.render('随机次数: %d' % self.remaining_babble_times, True, Constants.BLACK)
        self.screen.blit(surface_babbling, [20, 30])
        self.screen.blit(surface_time, [20, 50])
        self.screen.blit(surface_fps, [370, 30])

    def __display_text_human(self):
        current_time = pygame.time.get_ticks()
        delta_time_s = (current_time - self.start_time) / 1000
        speeding_delta_time_s = delta_time_s * self.game_speed

        surface_time = self.font.render('时间: %d' % speeding_delta_time_s, True, Constants.BLACK)
        surface_fps = self.font.render('FPS: %d' % self.clock.get_fps(), True, Constants.BLACK)
        self.screen.blit(surface_time, [20, 50])
        self.screen.blit(surface_fps, [20, 30])


    def random_babble(self):
        # Do the job here !
        print("random_babble")
        self.screen.fill(Constants.WHITE)

        self.remaining_babble_times = 10  # babble时间
        self.game_speed = 1  # don't set too large, self.game_speed = 1.0 is the default speed.
        self.fps = 60 * self.game_speed
        self.clock = pygame.time.Clock()  # create a game clock
        self.font = pygame.font.Font("SimSun.ttf", 18)  # display text like scores, times, etc.
        self.__set_timer()
        self.start_time = pygame.time.get_ticks()
        while True:
            # 绘制图像
            self.screen.fill(Constants.WHITE)
            # 统一对精灵进行图像绘制，角色移动的方法调用.替代上面的代码
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == UPDATE_NARS_EVENT:
                    # 在这里把感知信息写给self.nars 传递过去
                    self.update_sensors()
                elif event.type == OPENNARS_BABBLE_EVENT:
                    if self.remaining_babble_times == 0:
                        pygame.event.set_blocked(OPENNARS_BABBLE_EVENT)
                    else:
                        self.babble()
                        self.remaining_babble_times -= 1
            if pygame.sprite.spritecollideany(self.car, self.enemies):
                print("撞车啦！" )

            self.__display_text_babble()
            pygame.display.update()
            self.clock.tick(self.fps)

    def human_train(self):
        # Do the job here !
        print("human_train")
        self.screen.fill(Constants.WHITE)

        self.game_speed = 1  # don't set too large, self.game_speed = 1.0 is the default speed.
        self.fps = 60 * self.game_speed
        self.clock = pygame.time.Clock()  # create a game clock
        self.font = pygame.font.Font("SimSun.ttf", 18)  # display text like scores, times, etc.
        self.__set_timer()
        self.start_time = pygame.time.get_ticks()
        while True:
            # 绘制图像
            self.screen.fill(Constants.WHITE)
            # 统一对精灵进行图像绘制，角色移动的方法调用.替代上面的代码
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect)
            self.car.move()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == UPDATE_NARS_EVENT:
                    # 在这里把感知信息写给self.nars 传递过去
                    self.update_sensors()
            if pygame.sprite.spritecollideany(self.car, self.enemies):
                print("撞车啦！" )
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