import pygame
import random
import time

# 初始化 Pygame
pygame.init()

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 屏幕尺寸
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40  # 每个格子的大小

# 坦克和子弹大小
TANK_SIZE = 15
BULLET_SIZE = 5

# 创建窗口
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("2D 坦克大战 - 修正版")

# 定义字体
font = pygame.font.Font(None, 36)

# 迷宫地图（0表示空地，1表示墙壁）
maze = [[1 for _ in range(SCREEN_WIDTH // TILE_SIZE)] for _ in range(SCREEN_HEIGHT // TILE_SIZE)]

# 关卡设置
LEVELS = {1: 2, 2: 3, 3: 4}  # 每个关卡的敌人数

# 分数
scores = {'player1': 0, 'player2': 0, 'enemies': 0}

# 定义坦克类
class Tank(pygame.sprite.Sprite):
    def __init__(self, color, width, height, start_x, start_y):
        super().__init__()

        # 创建坦克的图像
        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        # 获取矩形对象
        self.rect = self.image.get_rect()

        # 坦克初始位置
        self.rect.x = start_x
        self.rect.y = start_y

        # 坦克的速度
        self.speed_x = 0
        self.speed_y = 0

    def update(self, walls):
        # 更新坦克的位置
        old_x, old_y = self.rect.x, self.rect.y

        # 尝试移动坦克
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # 碰撞检测
        for wall in walls:
            if self.rect.colliderect(wall):
                self.rect.x, self.rect.y = old_x, old_y
                break

    def changespeed(self, x, y):
        self.speed_x = x
        self.speed_y = y

# 定义子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, color, direction, start_x, start_y):
        super().__init__()

        self.image = pygame.Surface([BULLET_SIZE, BULLET_SIZE])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y
        self.direction = direction
        self.start_time = time.time()

    def update(self, walls):
        # 移动子弹
        if self.direction == "UP":
            self.rect.y -= 5
        elif self.direction == "DOWN":
            self.rect.y += 5
        elif self.direction == "LEFT":
            self.rect.x -= 5
        elif self.direction == "RIGHT":
            self.rect.x += 5

        # 子弹碰撞墙壁后反弹
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.direction == "UP":
                    self.direction = "DOWN"
                elif self.direction == "DOWN":
                    self.direction = "UP"
                elif self.direction == "LEFT":
                    self.direction = "RIGHT"
                elif self.direction == "RIGHT":
                    self.direction = "LEFT"

        # 子弹在4秒后消失
        if time.time() - self.start_time > 4:
            self.kill()

# 生成迷宫
def generate_maze():
    def is_in_bounds(x, y):
        return 0 <= x < SCREEN_HEIGHT // TILE_SIZE and 0 <= y < SCREEN_WIDTH // TILE_SIZE

    # 深度优先搜索生成迷宫
    def dfs(x, y):
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_in_bounds(nx, ny) and maze[nx][ny] == 1:
                maze[nx][ny] = 0
                maze[x + dx // 2][y + dy // 2] = 0
                dfs(nx, ny)

    start_x, start_y = 1, 1
    maze[start_x][start_y] = 0
    dfs(start_x, start_y)

# 绘制迷宫并返回墙壁的矩形列表
def draw_maze():
    walls = []
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            if maze[row][col] == 1:
                wall_rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                walls.append(wall_rect)
                pygame.draw.rect(screen, BLUE, wall_rect)
    return walls

# 显示比分
def display_scores():
    score_text = font.render(f"Player1: {scores['player1']}  Player2: {scores['player2']}  Enemies: {scores['enemies']}", True, BLACK)
    screen.blit(score_text, [10, SCREEN_HEIGHT - 40])

# 初始化关卡
def init_level(level):
    all_sprites_list = pygame.sprite.Group()
    bullet_list = pygame.sprite.Group()
    enemy_list = pygame.sprite.Group()

    # 生成迷宫
    generate_maze()

    # 玩家1（绿色坦克）
    player1 = Tank(GREEN, TANK_SIZE, TANK_SIZE, TILE_SIZE, TILE_SIZE)
    all_sprites_list.add(player1)

    # 玩家2（红色坦克）
    player2 = Tank(RED, TANK_SIZE, TANK_SIZE, SCREEN_WIDTH - TILE_SIZE * 2, SCREEN_HEIGHT - TILE_SIZE * 2)
    all_sprites_list.add(player2)

    # 敌人坦克
    for _ in range(LEVELS[level]):
        while True:
            enemy = Tank(YELLOW, TANK_SIZE, TANK_SIZE, random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT - 100))
            # 防止敌人生成在墙内
            if not any([enemy.rect.colliderect(wall) for wall in draw_maze()]):
                break
        enemy_list.add(enemy)
        all_sprites_list.add(enemy)

    return player1, player2, enemy_list, all_sprites_list, bullet_list

# 游戏主循环
def game_loop():
    level = 1
    player1, player2, enemies, all_sprites_list, bullet_list = init_level(level)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 获取按键状态
        keys = pygame.key.get_pressed()

        # 玩家1 WASD控制
        player1.changespeed(0, 0)
        if keys[pygame.K_a]:
            player1.changespeed(-3, 0)
        if keys[pygame.K_d]:
            player1.changespeed(3, 0)
        if keys[pygame.K_w]:
            player1.changespeed(0, -3)
        if keys[pygame.K_s]:
            player1.changespeed(0, 3)

        # 玩家2 方向键控制
        player2.changespeed(0, 0)
        if keys[pygame.K_LEFT]:
            player2.changespeed(-3, 0)
        if keys[pygame.K_RIGHT]:
            player2.changespeed(3, 0)
        if keys[pygame.K_UP]:
            player2.changespeed(0, -3)
        if keys[pygame.K_DOWN]:
            player2.changespeed(0, 3)

        # 检测玩家1的攻击
        if keys[pygame.K_c]:
            bullet = Bullet(GREEN, "UP", player1.rect.x + TANK_SIZE // 2, player1.rect.y)
            all_sprites_list.add(bullet)
            bullet_list.add(bullet)

        # 检测玩家2的攻击
        if keys[pygame.K_m]:
            bullet = Bullet(RED, "UP", player2.rect.x + TANK_SIZE // 2, player2.rect.y)
            all_sprites_list.add(bullet)
            bullet_list.add(bullet)

        # 清屏
        screen.fill(WHITE)

        # 绘制迷宫并获取所有墙壁的矩形
        walls = draw_maze()

        # 更新坦克和子弹位置
        player1.update(walls)
        player2.update(walls)
        enemies.update(walls)
        bullet_list.update(walls)

        # 绘制所有精灵
        all_sprites_list.draw(screen)

        # 显示分数
        display_scores()

        # 更新屏幕
        pygame.display.flip()

        # 设置帧率
        clock.tick(60)

# 游戏启动
game_loop()

pygame.quit()
