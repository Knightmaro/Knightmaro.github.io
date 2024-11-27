import pygame
import random
import sys
import os
import platform
import asyncio

# 设置标准输出编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 初始化 Pygame 和音频
pygame.init()
pygame.mixer.init()

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
LIGHT_GREEN = (0, 200, 0)
DARK_RED = (200, 0, 0)
GOLD = (255, 215, 0)

# 设置游戏窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_SIZE = 20

# 创建窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('贪吃蛇游戏')

# 修改字体加载部分
def load_font():
    # 常见的中文字体列表
    chinese_fonts = [
        'Microsoft YaHei UI', 
        'SimHei',
        'NSimSun',
        'FangSong',
        'KaiTi'
    ]
    
    # 获取系统已安装的所有字体
    available_fonts = pygame.font.get_fonts()
    
    # 尝试使用系统中已安装的中文字体
    for chinese_font in chinese_fonts:
        if chinese_font.lower() in available_fonts:
            try:
                return pygame.font.SysFont(chinese_font, 36), pygame.font.SysFont(chinese_font, 72)
            except:
                continue
    
    # 如果没有找到合适的中文字体，使用系统默认字体
    print('未能找到中文字体，使用系统默认字体')
    return pygame.font.SysFont(None, 36), pygame.font.SysFont(None, 72)

# 使用新的字体加载函数
font, large_font = load_font()

# 添加新的颜色和常量
GRID_COLOR = (40, 40, 40)
GRADIENT_GREEN = [(0, 255, 127), (0, 235, 117), (0, 215, 107)]
PARTICLE_COLORS = [(255, 255, 0), (255, 165, 0), (255, 69, 0)]

# 添加新的音效加载
def load_sounds():
    sounds = {
        'eat': None,
        'crash': None,
        'button': None,
        'background': None
    }
    try:
        sounds['eat'] = pygame.mixer.Sound('sounds/eat.wav')
        sounds['crash'] = pygame.mixer.Sound('sounds/crash.wav')
        sounds['button'] = pygame.mixer.Sound('sounds/button.wav')
        sounds['background'] = pygame.mixer.Sound('sounds/background.wav')
        
        # 设置音量
        for sound in sounds.values():
            if sound:
                sound.set_volume(0.5)
    except:
        print("部分音效文件未找到")
    return sounds

# 添加粒子效果类
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.lifetime = 20
        self.color = random.choice(PARTICLE_COLORS)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
    def draw(self, surface):
        alpha = int((self.lifetime / 20) * 255)
        particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*self.color, alpha), (2, 2), 2)
        surface.blit(particle_surface, (int(self.x), int(self.y)))

# 添加新的按钮类
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, sound_manager=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.sound_manager = sound_manager
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                if self.sound_manager:
                    self.sound_manager.play('button')
                return True
        return False

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.body = [(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)]
        self.direction = 'RIGHT'
        self.grow = False
        self.score = 0

    def check_collision(self):
        head = self.body[0]
        x, y = head
        
        # 检查是否撞墙
        if (x < 0 or x >= WINDOW_WIDTH or 
            y < 0 or y >= WINDOW_HEIGHT):
            return True
            
        # 检查是否撞到自己（从第二个身体部分开始检查）
        if head in self.body[1:]:
            return True
            
        return False

    def move(self):
        x, y = self.body[0]
        if self.direction == 'UP':
            y -= BLOCK_SIZE
        elif self.direction == 'DOWN':
            y += BLOCK_SIZE
        elif self.direction == 'LEFT':
            x -= BLOCK_SIZE
        elif self.direction == 'RIGHT':
            x += BLOCK_SIZE

        new_head = (x, y)
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        self.grow = False
        
        # 返回是否发生碰撞
        return self.check_collision()

    def draw(self):
        # 绘制蛇身，使用渐变色
        for i, segment in enumerate(self.body):
            color_index = i % len(GRADIENT_GREEN)
            color = GRADIENT_GREEN[color_index]
            
            # 绘制圆角矩形
            segment_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(segment_surface, (*color, 255), 
                           (0, 0, BLOCK_SIZE, BLOCK_SIZE), 
                           border_radius=5)
            
            # 添加光泽效果
            if i == 0:  # 蛇头
                pygame.draw.circle(segment_surface, (255, 255, 255, 100),
                                 (BLOCK_SIZE//4, BLOCK_SIZE//4),
                                 2)
            
            screen.blit(segment_surface, segment)

class Food:
    def __init__(self):
        self.position = self.generate_position()
        self.particles = []
        self.angle = 0
        
    def generate_position(self):
        x = random.randrange(0, WINDOW_WIDTH - BLOCK_SIZE, BLOCK_SIZE)
        y = random.randrange(0, WINDOW_HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
        return (x, y)

    def update(self):
        self.angle += 2
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()
        
        if random.random() < 0.1:
            self.particles.append(Particle(
                self.position[0] + BLOCK_SIZE//2,
                self.position[1] + BLOCK_SIZE//2
            ))
    
    def draw(self):
        # 绘制光晕效果
        glow_surface = pygame.Surface((BLOCK_SIZE*2, BLOCK_SIZE*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 0, 0, 30), 
                         (BLOCK_SIZE, BLOCK_SIZE), 
                         BLOCK_SIZE)
        screen.blit(glow_surface, 
                   (self.position[0] - BLOCK_SIZE//2,
                    self.position[1] - BLOCK_SIZE//2))
        
        # 绘制食物主体
        food_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(food_surface, (255, 0, 0, 255),
                         (BLOCK_SIZE//2, BLOCK_SIZE//2),
                         BLOCK_SIZE//2)
        
        # 添加高光效果
        highlight = pygame.transform.rotate(
            pygame.Surface((BLOCK_SIZE//4, BLOCK_SIZE//2), pygame.SRCALPHA),
            self.angle
        )
        pygame.draw.ellipse(highlight, (255, 255, 255, 100),
                          highlight.get_rect())
        
        food_surface.blit(highlight, 
                         (BLOCK_SIZE//4, 0))
        screen.blit(food_surface, self.position)
        
        # 绘制粒子
        for particle in self.particles:
            particle.draw(screen)

# 添加背景网格绘制函数
def draw_background():
    # 绘制网格
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

def show_menu(sound_manager):
    difficulties = {
        '简单': 8,
        '中等': 12,
        '困难': 16
    }
    
    buttons = [
        Button(WINDOW_WIDTH//2 - 100, 300 + i*70, 200, 50, 
               text, GREEN, LIGHT_GREEN, sound_manager)
        for i, text in enumerate(difficulties.keys())
    ]
    
    while True:
        screen.fill(BLACK)
        
        # 绘制标题
        title = large_font.render('贪吃蛇', True, GOLD)
        title_shadow = large_font.render('贪吃蛇', True, RED)
        screen.blit(title_shadow, (WINDOW_WIDTH//2 - title.get_width()//2 + 2, 102))
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        
        # 绘制按钮
        for button in buttons:
            button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            for i, button in enumerate(buttons):
                if button.handle_event(event):
                    return difficulties[list(difficulties.keys())[i]]

def show_game_over(score):
    restart_button = Button(WINDOW_WIDTH//2 - 200, 400, 180, 50, "重新开始", GREEN, LIGHT_GREEN)
    quit_button = Button(WINDOW_WIDTH//2 + 20, 400, 180, 50, "退出游戏", RED, DARK_RED)
    
    while True:
        screen.fill(BLACK)
        
        game_over_text = large_font.render('游戏结束', True, RED)
        score_text = font.render(f'最终得分: {score}', True, GOLD)
        
        screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, 200))
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 300))
        
        restart_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if restart_button.handle_event(event):
                return True
            if quit_button.handle_event(event):
                pygame.quit()
                sys.exit()

# 音效管理类
class SoundManager:
    def __init__(self):
        self.sounds = {}
        # 移除平台检查，让网页版也能播放音效
        self.sounds = {
            'eat': self.load_sound('eat.wav', 0.5),
            'crash': self.load_sound('crash.wav', 0.6),
            'button': self.load_sound('button.wav', 0.4),
            'background': self.load_sound('background.wav', 0.3)
        }
        
        # 播放背景音乐
        if self.sounds.get('background'):
            self.sounds['background'].play(-1)
    
    def load_sound(self, filename, volume=1.0):
        try:
            # 修改音效文件路径以适应网页环境
            sound = pygame.mixer.Sound(f'sounds/{filename}')
            sound.set_volume(volume)
            return sound
        except Exception as e:
            print(f"无法加载音效: {filename}, 错误: {e}")
            return None
class SlowMotionManager:
    def __init__(self):
        self.is_active = False
        self.duration = 10  # 修改这里可以调整震动时间（帧数）
        self.current_frame = 0
        self.shake_amplitude = 10
        self.original_positions = []
        self.shake_offset = [0, 0]
        self.final_state = None
        self.collision_state = None  # 添加碰撞时的状态
    
    def start(self, snake):
        self.is_active = True
        self.current_frame = 0
        self.original_positions = snake.body.copy()
        self.final_state = None
        # 保存碰撞时的状态
        screen_copy = pygame.display.get_surface().copy()
        self.collision_state = screen_copy
    
    def update(self, screen):
        if not self.is_active:
            if self.collision_state:  # 使用碰撞时的状态
                screen.blit(self.collision_state, (0, 0))
            return [0, 0]
            
        self.current_frame += 1
        if self.current_frame <= self.duration:
            # 计算震动偏移
            shake_power = (self.duration - self.current_frame) / self.duration
            self.shake_offset = [
                random.randint(-1, 1) * self.shake_amplitude * shake_power,
                random.randint(-1, 1) * self.shake_amplitude * shake_power
            ]
            # 在震动时显示碰撞状态
            if self.collision_state:
                screen.blit(self.collision_state, self.shake_offset)
        else:
            self.shake_offset = [0, 0]
            if self.collision_state:
                screen.blit(self.collision_state, (0, 0))
            
        return self.shake_offset
        
    def is_finished(self):
        return self.current_frame > self.duration

# 修改主函数为异步函数
async def main():
    sound_manager = SoundManager()
    
    while True:
        speed = await show_menu(sound_manager)
        clock = pygame.time.Clock()
        snake = Snake()
        food = Food()
        game_over = False
        paused = False
        slow_motion = SlowMotionManager()
        continue_button = Button(
            WINDOW_WIDTH - 220, WINDOW_HEIGHT - 70,
            200, 50, "继续", GREEN, LIGHT_GREEN, sound_manager
        )
        show_continue_button = False

        while True:
            # 添加事件处理的异步支持
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                # 处理继续按钮
                if show_continue_button:
                    if continue_button.handle_event(event):
                        if show_game_over(snake.score):
                            # 重置游戏状态
                            game_over = False
                            snake.reset()
                            food = Food()
                            show_continue_button = False
                            slow_motion = SlowMotionManager()
                            break  # 跳出内层循环，重新开始游戏
                        else:
                            pygame.quit()
                            sys.exit()
                            
                elif event.type == pygame.KEYDOWN and not game_over and not slow_motion.is_active:
                    if event.key == pygame.K_p:
                        paused = not paused
                    elif not paused:
                        if event.key == pygame.K_UP and snake.direction != 'DOWN':
                            snake.direction = 'UP'
                        elif event.key == pygame.K_DOWN and snake.direction != 'UP':
                            snake.direction = 'DOWN'
                        elif event.key == pygame.K_LEFT and snake.direction != 'RIGHT':
                            snake.direction = 'LEFT'
                        elif event.key == pygame.K_RIGHT and snake.direction != 'LEFT':
                            snake.direction = 'RIGHT'

            # 添加异步等待
            await asyncio.sleep(0)

            if not paused and not game_over and not slow_motion.is_active:
                # 绘制当前帧
                screen.fill(BLACK)
                draw_background()
                snake.draw()
                food.draw()
                score_text = font.render(f'得分: {snake.score}', True, WHITE)
                screen.blit(score_text, (10, 10))
                
                # 保存移动前的状态
                current_state = screen.copy()
                
                # 检查移动是否导致碰撞
                if snake.move():
                    game_over = True
                    # 使用移动前的状态
                    screen.blit(current_state, (0, 0))
                    slow_motion.start(snake)
                    sound_manager.play('crash')
                    continue

                # 检查是否吃到食物
                if snake.body[0] == food.position:
                    snake.grow = True
                    snake.score += 10
                    food.position = food.generate_position()
                    sound_manager.play('eat')

            # 更新食物动画
            food.update()

            # 如果不是在慢动作状态，重新绘制游戏画面
            if not slow_motion.is_active:
                screen.fill(BLACK)
                draw_background()
                snake.draw()
                food.draw()
                score_text = font.render(f'得分: {snake.score}', True, WHITE)
                screen.blit(score_text, (10, 10))

            # 应用慢动作效果
            if slow_motion.is_active or slow_motion.final_state:
                offset = slow_motion.update(screen)
                if slow_motion.is_active:  # 只在慢动作激活时应用震动效果
                    screen_copy = screen.copy()
                    screen.blit(screen_copy, offset)
                
                if slow_motion.is_finished() and not show_continue_button:
                    slow_motion.is_active = False
                    show_continue_button = True

            # 显示继续按钮
            if show_continue_button:
                offset = slow_motion.update(screen)
                continue_button.draw(screen)
                

            pygame.display.flip()

            # 控制游戏速度
            if slow_motion.is_active:
                clock.tick(speed // 2)
            else:
                clock.tick(speed)

    sound_manager.stop_background()
    pygame.quit()
    sys.exit()

# 修改菜单函数为异步函数
async def show_menu(sound_manager):
    difficulties = {
        '简单': 8,
        '中等': 12,
        '困难': 16
    }
    
    buttons = [
        Button(WINDOW_WIDTH//2 - 100, 300 + i*70, 200, 50, 
               text, GREEN, LIGHT_GREEN, sound_manager)
        for i, text in enumerate(difficulties.keys())
    ]
    
    while True:
        screen.fill(BLACK)
        
        # 绘制标题
        title = large_font.render('贪吃蛇', True, GOLD)
        title_shadow = large_font.render('贪吃蛇', True, RED)
        screen.blit(title_shadow, (WINDOW_WIDTH//2 - title.get_width()//2 + 2, 102))
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        
        # 绘制按钮
        for button in buttons:
            button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            for i, button in enumerate(buttons):
                if button.handle_event(event):
                    return difficulties[list(difficulties.keys())[i]]
        
        await asyncio.sleep(0)

# 修改游戏结束函数为异步函数
async def show_game_over(score):
    restart_button = Button(WINDOW_WIDTH//2 - 200, 400, 180, 50, "重新开始", GREEN, LIGHT_GREEN)
    quit_button = Button(WINDOW_WIDTH//2 + 20, 400, 180, 50, "退出游戏", RED, DARK_RED)
    
    while True:
        screen.fill(BLACK)
        
        game_over_text = large_font.render('游戏结束', True, RED)
        score_text = font.render(f'最终得分: {score}', True, GOLD)
        
        screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, 200))
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 300))
        
        restart_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if restart_button.handle_event(event):
                return True
            if quit_button.handle_event(event):
                pygame.quit()
                sys.exit()
        
        await asyncio.sleep(0)

# 添加启动代码
if platform.system() == "Emscripten":
    asyncio.run(main())
else:
    if __name__ == '__main__':
        asyncio.run(main())