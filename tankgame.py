import pygame
import random

# 初始化 Pygame
pygame.init()

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_RED = (139, 0, 0)

# 屏幕尺寸 (更大的网格)
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# 创建窗口
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("2D 像素坦克大战 - Boss 战")

# 定义字体
font = pygame.font.Font(None, 36)

# 坦克类
class Tank(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()

        # 创建坦克的图像
        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        # 获取矩形对象
        self.rect = self.image.get_rect()

        # 坦克初始位置
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - 60

        # 坦克的速度
        self.speed_x = 0
        self.speed_y = 0

    def update(self):
        # 更新坦克的位置
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def changespeed(self, x, y):
        # 改变坦克速度
        self.speed_x += x
        self.speed_y += y

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()

        # 创建子弹的图像
        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        # 获取矩形对象
        self.rect = self.image.get_rect()

    def update(self):
        # 向上移动子弹
        self.rect.y -= 5

# 墙壁类
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()

        # 创建墙的图像
        self.image = pygame.Surface([width, height])
        self.image.fill(BLUE)

        # 获取矩形对象
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Boss坦克类
class Boss(Tank):
    def __init__(self, color, width, height):
        super().__init__(color, width, height)

        # 设置Boss的生命和击中次数
        self.lives = 3
        self.hit_count = 0

    def update(self):
        # 随机移动Boss
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        move = random.choice(directions)
        self.rect.x += move[0]
        self.rect.y += move[1]

        # 保证Boss不超出屏幕
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.rect.x -= move[0]
        if self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT // 2:
            self.rect.y -= move[1]

    def hit(self):
        self.hit_count += 1
        if self.hit_count >= 10:
            self.lives -= 1
            self.hit_count = 0

# 血条显示函数
def draw_health_bar(boss):
    pygame.draw.rect(screen, DARK_RED, [10, SCREEN_HEIGHT - 30, 300, 20])
    if boss.lives > 0:
        pygame.draw.rect(screen, RED, [10, SCREEN_HEIGHT - 30, (boss.lives / 3) * 300, 20])

# 创建所有精灵组
all_sprites_list = pygame.sprite.Group()
bullet_list = pygame.sprite.Group()
wall_list = pygame.sprite.Group()

# 关卡配置，包括Boss和复杂地形
def level_1():
    # 玩家坦克
    player_tank = Tank(GREEN, 50, 50)
    all_sprites_list.add(player_tank)

    # 墙壁
    walls = [
        Wall(200, 150, 400, 30),
        Wall(600, 300, 200, 30),
        Wall(300, 500, 100, 30),
        Wall(1000, 600, 150, 30),
    ]
    for wall in walls:
        wall_list.add(wall)
        all_sprites_list.add(wall)

    # Boss 坦克
    boss = Boss(RED, 80, 80)
    boss.rect.x = SCREEN_WIDTH // 2
    boss.rect.y = 50
    all_sprites_list.add(boss)

    return player_tank, boss

# 游戏主循环
def game_loop():
    player_tank, boss = level_1()

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player_tank.changespeed(-3, 0)
                if event.key == pygame.K_RIGHT:
                    player_tank.changespeed(3, 0)
                if event.key == pygame.K_UP:
                    player_tank.changespeed(0, -3)
                if event.key == pygame.K_DOWN:
                    player_tank.changespeed(0, 3)
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(YELLOW, 10, 10)
                    bullet.rect.x = player_tank.rect.x + 20
                    bullet.rect.y = player_tank.rect.y
                    all_sprites_list.add(bullet)
                    bullet_list.add(bullet)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player_tank.changespeed(3, 0)
                if event.key == pygame.K_RIGHT:
                    player_tank.changespeed(-3, 0)
                if event.key == pygame.K_UP:
                    player_tank.changespeed(0, 3)
                if event.key == pygame.K_DOWN:
                    player_tank.changespeed(0, -3)

        # 更新所有精灵
        all_sprites_list.update()

        # 检查子弹是否击中Boss
        for bullet in bullet_list:
            if pygame.sprite.collide_rect(bullet, boss):
                bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)
                boss.hit()
                if boss.lives == 0:
                    running = False
            # 删除飞出屏幕的子弹
            if bullet.rect.y < -10:
                bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)

        # 清屏
        screen.fill(BLACK)

        # 绘制所有精灵
        all_sprites_list.draw(screen)

        # 绘制血条
        draw_health_bar(boss)

        # 更新屏幕
        pygame.display.flip() 

        # 设置帧率
        clock.tick(60)

# 游戏启动
game_loop()

pygame.quit()
