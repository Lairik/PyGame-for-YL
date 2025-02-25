import pygame
import json
import random
import math

# Инициализация Pygame
pygame.font.init()
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

# Константы
W, H = 900, 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
BLUE = (100, 100, 255)

# Загрузка изображений
bg_main = pygame.image.load('images/bg_main.png')

bg = pygame.image.load('images/фон.PNG')
bg = pygame.transform.scale(bg, (900, 600))

bg_2 = pygame.image.load('images/космос.jpg')
bg_2 = pygame.transform.scale(bg_2, (900, 600))

ufo_image = pygame.image.load("images/ufo.png")
ufo_image = pygame.transform.scale(ufo_image, (170, 110))
ufo_rect = ufo_image.get_rect()

boss_image = pygame.image.load("images/LazerBoss.png")
boss_image = pygame.transform.scale(boss_image, (200, 250))
boss_rect = boss_image.get_rect()

walk_left = [pygame.image.load(f'images/left/{i}.png') for i in range(1, 9)]
walk_no_movement = [pygame.image.load(f'images/no movement/{i}.png') for i in range(1, 10)]
walk_right = [pygame.image.load(f'images/right/{i}.png') for i in range(1, 9)]
meteor_frames = [pygame.image.load(f'images/meteorit/{i}.png') for i in range(1, 7)]

shield_img = pygame.image.load("images/shield.png")
booster_img = pygame.image.load("images/booster.png")
shield_overlay = pygame.image.load("images/shield_effect.png")
shield_overlay = pygame.transform.scale(shield_overlay, (200, 200))

# Глобальные переменные
boss = None
boss_2 = None
paused = False
game_over = False
score = 0
record = 0
meteor_speed = 5
player_speed = 7
ufo_speed = 3
spawn_delay = 1000
boss_active = False
boss_2_active = False
boss_timer = 0
vol = 0.4
music_enabled = True
ufo_charges = []

# Загрузка метеоритов
pygame.time.set_timer(pygame.USEREVENT, spawn_delay)

# Загрузка звуков
bg_music = pygame.mixer.Sound("sounds/bgmusic.ogg")
bg_music.set_volume(vol)
boss_music = pygame.mixer.Sound("sounds/boss_music.ogg")
boss_music.set_volume(vol)
br_m = pygame.mixer.Sound("sounds/vitayuschiy-v-oblakah-mechtatel-321.ogg")
br_m.set_volume(vol)
putin_core = pygame.mixer.Sound("sounds/vyi-rabotat-budete.ogg")
putin_core.set_volume(vol)
col_music = pygame.mixer.Sound("sounds/inecraft_damage.ogg")
col_music.set_volume(vol)

class UFOBoss:
    def __init__(self):
        self.image = ufo_image
        self.rect = self.image.get_rect(midtop=(W // 2, 20))
        self.direction = 1
        self.speed = 3

    def move(self):
        ufo_rect.x += self.speed
        if ufo_rect.right > W or ufo_rect.left < 0:
            self.speed = -self.speed

    def shoot(self):
        if random.randint(1, 90) == 1:
            ball = GreenBall(ufo_rect.centerx, self.rect.bottom, random.choice([-4, 4]), 3)
            ufo_charges.append(ball)


class GreenBall:
    def __init__(self, x, y, speed_x, speed_y):
        self.rect = pygame.Rect(x, y, 10, 10)
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.left <= 0 or self.rect.right >= W:
            self.speed_x = -self.speed_x

    def draw(self, sc):
        pygame.draw.circle(sc, DARK_GREEN, self.rect.center, 10)


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, image, power_type, group):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (70, 65))
        self.rect = self.image.get_rect(center=(x, 0))
        self.type = power_type
        self.speed = 5
        self.add(group)

    def update(self, *args):
        if not paused:
            self.rect.y += self.speed
        if self.rect.y > H:
            self.kill()


class Meteorit(pygame.sprite.Sprite):
    def __init__(self, x, group):
        global meteor_speed
        pygame.sprite.Sprite.__init__(self)
        self.frames = meteor_frames
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, 0))
        self.speed = meteor_speed
        self.add(group)
        self.animation_count = 0

    def update(self, *args):
        global score
        self.animation_count += 1
        if self.animation_count >= len(self.frames) * 5:
            self.animation_count = 0
        self.image = self.frames[self.animation_count // 5]
        if self.rect.y < args[0] - 20:
            if not paused:
                self.rect.y += self.speed
        else:
            score += 1
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.img = walk_no_movement[0]
        self.image = pygame.transform.scale(self.img, (10, 10))
        self.rect = self.img.get_rect(center=(x, y))
        self.rect.x = x
        self.rect.y = y
        self.is_shielded = False
        self.bosted = False
        self.left = False
        self.right = False
        self.count = 0
        self.speed = speed

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > -10:
            self.rect.x -= self.speed
            self.left = True
            self.right = False
        elif keys[pygame.K_RIGHT] and self.rect.x < W - 125:
            self.rect.x += self.speed
            self.left = False
            self.right = True
        else:
            self.left = False
            self.right = False

    def apply_powerup(self, powerup):
        if powerup.type == "shield":
            self.is_shielded = True
            pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
        elif powerup.type == "booster":
            if self.speed == 7:
                self.speed = 10
            pygame.time.set_timer(pygame.USEREVENT + 2, 5000)
        powerup.kill()

    def animation(self):
        if self.count + 1 > 60:
            self.count = 0
        if self.left:
            sc.blit(pygame.transform.scale(walk_left[self.count // 8], (128, 128)), (self.rect.x, self.rect.y))
        elif self.right:
            sc.blit(pygame.transform.scale(walk_right[self.count // 8], (128, 128)), (self.rect.x, self.rect.y))
        else:
            sc.blit(pygame.transform.scale(walk_no_movement[self.count // 9], (128, 128)), (self.rect.x, self.rect.y))

        if self.is_shielded:
            shield_x = self.rect.x - 25
            shield_y = self.rect.y - 25
            sc.blit(shield_overlay, (shield_x, shield_y))

        self.count += 1

    def collides(self):
        global game_over, vol
        for powerup in powerups:
            if self.rect.colliderect(powerup.rect):
                self.apply_powerup(powerup)
                powerup.kill()

        for meteor in meteors:
            if self.rect.inflate(-100, -20).colliderect(meteor.rect.inflate(-20, -50)):
                if self.is_shielded:
                    meteor.kill()
                    self.is_shielded = False
                else:
                    game_over = True
                col_music.play()

        for ball in ufo_charges:
            if ball.rect.top >= H - 10:
                ufo_charges.remove(ball)
            if self.rect.inflate(-100, -20).colliderect(ball.rect):
                if self.is_shielded:
                    ufo_charges.remove(ball)
                    self.is_shielded = False
                else:
                    game_over = True
                col_music.play()

        for laser in boss_lasers:
            if self.rect.inflate(-100, -20).colliderect(laser.rect):
                if self.is_shielded:
                    laser.kill()
                    self.is_shielded = False
                else:
                    game_over = True
                col_music.play()

class LaserBoss():
    def __init__(self):
        super().__init__()
        self.image = boss_image
        self.rect = self.image.get_rect(midtop=(W // 2, 10))
        self.speed = 3
        self.direction = 1
        self.shoot_timer = 100

    def move(self):
        boss_rect.x += self.speed
        if boss_rect.right > W or boss_rect.left < 0:
            self.speed = -self.speed

        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(80, 120)
            self.shoot()

    def shoot(self):
        angles = [-20, -15, -10, 10, 15, 20]
        hand_positions = [
            (boss_rect.left, 100),
            (boss_rect.right, 100)
        ]

        for pos in hand_positions:
            angle = random.choice(angles)
            laser = Laser(pos[0], pos[1], angle)
            boss_lasers.add(laser)

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.width = 10
        self.height = 50
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        self.image = pygame.transform.rotate(self.image, angle)

        self.rect = self.image.get_rect(center=(x, y))

        rad_angle = math.radians(angle)
        self.dx = math.sin(rad_angle) * 8
        self.dy = math.cos(rad_angle) * 8
        self.lifetime = 120

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        self.lifetime -= 1
        if self.lifetime <= 0 or self.rect.top > H or self.rect.left < 0 or self.rect.right > W:
            self.kill()

def create_powerup(group):
    max_attempts = 10
    if random.randint(1, 10) > 8:
        for _ in range(max_attempts):
            x = random.randint(20, W - 20)
            powerup_rect = pygame.Rect(x, 0, 70, 65)
            if not any(powerup_rect.colliderect(meteor.rect) for meteor in meteors):
                power_type = random.choice(["shield", "booster"])
                image = shield_img if power_type == "shield" else booster_img
                return PowerUp(x, image, power_type, group)


def createMeteorit(group):
    max_attempts = 10
    for _ in range(max_attempts):
        x = random.randint(20, W - 20)
        meteor_rect = pygame.Rect(x, 0, 100, 100)
        if not any(meteor_rect.colliderect(powerup.rect) for powerup in powerups):
            return Meteorit(x, group)
    return None


def draw_score(score):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Счёт: {score}", True, WHITE)
    score_rect = score_text.get_rect(topright=(W - 20, 20))
    pygame.draw.rect(sc, BLACK, (score_rect.x - 10, score_rect.y - 5, score_rect.width + 20, score_rect.height + 10), border_radius=10)
    sc.blit(score_text, score_rect)

def toggle_music():
    global music_enabled
    if music_enabled:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

def change_volume(delta):
    global vol
    vol += delta
    vol = max(0, min(1, vol))  # Ограничение громкости в диапазоне от 0 до 1
    pygame.mixer.music.set_volume(vol)
    bg_music.set_volume(vol)
    boss_music.set_volume(vol)
    br_m.set_volume(vol)
    putin_core.set_volume(vol)
    col_music.set_volume(vol)

def main_menu():
    global play, paused, bg_main

    br_m.stop()

    running = True
    while running:
        sc.blit(bg_main, (0, 0))

        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load('sounds/bgmusic.ogg')
            pygame.mixer.music.play(-1)

        chill_preview = pygame.image.load('images/no movement/4.png')
        sc.blit(chill_preview, (700, 400))

        font = pygame.font.Font(None, 50)

        name_game = pygame.image.load('images/name of game.png')
        name_game = pygame.transform.scale(name_game, (300, 300))

        sc.blit(name_game, (W - 600, H - 620))

        play_button = font.render("Играть", True, WHITE)
        settings_button = font.render("Настройки", True, WHITE)
        rules_button = font.render("Правила игры", True, WHITE)

        play_button_rect = play_button.get_rect(center=(W // 2, H // 3))
        settings_button_rect = settings_button.get_rect(center=(W // 2, H // 2))
        rules_button_rect = rules_button.get_rect(center=(W // 2, H // 1.5))

        sc.blit(play_button, play_button_rect)
        sc.blit(settings_button, settings_button_rect)
        sc.blit(rules_button, rules_button_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if play_button_rect.collidepoint(x, y):
                    resert()
                    running = False
                elif settings_button_rect.collidepoint(x, y):
                    settings_menu()
                elif rules_button_rect.collidepoint(x, y):
                    rules_menu()

def settings_menu():
    global vol

    running = True
    while running:
        settings_img = pygame.image.load("images/set.png")
        sc.blit(settings_img, (-100, -50))
        font = pygame.font.Font(None, 36)

        # Текст настроек
        settings_text = font.render("Настройки (нажмите Esc для возврата)", True, WHITE, BLACK)
        sc.blit(settings_text, (10, 10))

        # Кнопка включения/выключения музыки
        music_toggle_text = font.render("Регулировка музыки", True, WHITE, BLACK)
        music_toggle_rect = music_toggle_text.get_rect(topleft=(10, 50))
        sc.blit(music_toggle_text, music_toggle_rect)

        # Кнопки регулировки громкости
        volume_up_text = font.render("Громкость +", True, WHITE, BLACK)
        volume_up_rect = volume_up_text.get_rect(topleft=(10, 100))
        sc.blit(volume_up_text, volume_up_rect)

        volume_down_text = font.render("Громкость -", True, WHITE, BLACK)
        volume_down_rect = volume_down_text.get_rect(topleft=(10, 150))
        sc.blit(volume_down_text, volume_down_rect)


        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if volume_up_rect.collidepoint(x, y):
                    change_volume(0.1)
                elif volume_down_rect.collidepoint(x, y):
                    change_volume(-0.1)

def rules_menu():
    running = True
    while running:
        rules_img = pygame.image.load("images/rules.png")
        rules_img = pygame.transform.scale(rules_img, (W, H))
        sc.blit(rules_img, (0, 0))
        font = pygame.font.Font(None, 36)
        rules_text = font.render('''Правила игры: Избегайте метеоритов! Передвижение на стрелки. Удачи!''', True, WHITE, BLACK)
        sc.blit(rules_text, (10, 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

# Инициализация групп спрайтов
meteors = pygame.sprite.Group()
powerups = pygame.sprite.Group()
boss_lasers = pygame.sprite.Group()

# Инициализация игрока
player = Player(W//2 - 64, H - 210, player_speed)

# Инициализация экрана
sc = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()


def handle_game_over():
    global game_over, score, record, powerups, ufo_charges, boss_active, boss, spawn_delay, fl_music, paused, music_enabled, boss_music

    # Остановка музыки и воспроизведение звука завершения игры
    music_enabled = False
    toggle_music()
    boss_music.stop()
    br_m.play()

    # Обновление рекорда, если текущий счет больше
    if score > record:
        record = score
        with open("record.json", "w") as f:
            json.dump(record, f)

    # Основной цикл экрана завершения игры
    while game_over:
        # Отрисовка фона
        sc.blit(bg_2, (0, 0))

        # Шрифт для текста
        f1 = pygame.font.Font(None, 36)

        # Заголовок "Игра окончена!"
        title = f1.render("Игра окончена!", True, BLACK, WHITE)
        sc.blit(title, (W // 2 - 100, H // 4))

        # Отображение счета и рекорда
        score_text = f1.render(f"Ваш счет: {score}", True, BLACK, WHITE)
        record_text = f1.render(f"Рекорд: {record}", True, BLACK, WHITE)
        sc.blit(score_text, (W // 2 - 80, H // 4 + 50))
        sc.blit(record_text, (W // 2 - 80, H // 4 + 100))

        # Кнопки "Играть снова" и "Выход" и "Главное меню"
        play_again_button = f1.render("Играть снова", True, BLACK, GREEN)
        exit_button = f1.render("Выход", True, BLACK, GREEN)
        main_button = f1.render("Главное меню", True, BLACK, GREEN)

        play_again_button_rect = play_again_button.get_rect(center=(W // 2 - 20, H // 2 + 10))
        exit_button_rect = exit_button.get_rect(center=(W // 2 - 10, H // 2 + 60))
        main_button_rect = main_button.get_rect(center=(W // 2 - 20, H // 2 + 110))

        sc.blit(play_again_button, play_again_button_rect)
        sc.blit(exit_button, exit_button_rect)
        sc.blit(main_button, main_button_rect)

        # Обновление экрана
        pygame.display.flip()

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Если нажата кнопка "Играть снова"
                if play_again_button_rect.collidepoint(x, y):
                    # Сброс состояния игры
                    resert()  # Выход из функции и возврат в основной цикл
                # Если нажата кнопка "Главное меню"
                elif main_button_rect.collidepoint(x, y):
                    main_menu()


                # Если нажата кнопка "Выход"
                elif exit_button_rect.collidepoint(x, y):
                    pygame.quit()
                    exit()

def resert():
    global game_over, score, meteors, powerups, ufo_charges, boss_lasers, boss_active, boss_2_active, boss, boss_2, meteor_speed, spawn_delay, player, music_enabled
    player = None
    player = Player(W//2 - 64, H - 210, player_speed)
    meteors.empty()
    powerups.empty()
    boss_lasers.empty()
    ufo_charges.clear()
    boss_active = False
    boss_2_active = False
    boss = None
    boss_2 = None
    score = 0
    meteor_speed = 5
    spawn_delay = 1000
    pygame.time.set_timer(pygame.USEREVENT, spawn_delay)
    game_over = False
    br_m.stop()
    music_enabled = True
    toggle_music()

# Example of modularizing the game loop
def handle_events():
    global paused, boss_active, boss_2_active, br_m, putin_core, vol, boss, boss_2, boss_timer, spawn_delay, meteor_speed, ufo_charges, music_enabled
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.USEREVENT:
            if not paused:
                if not(boss_active) and not(boss_2_active):
                    createMeteorit(meteors)
                create_powerup(powerups)
        elif event.type == pygame.USEREVENT + 1:
            player.is_shielded = False
        elif event.type == pygame.USEREVENT + 2:
            player.speed = 7

        if score == 20 and not boss_active:
            music_enabled = False
            toggle_music()
            boss_music.play()
            boss = UFOBoss()
            boss_active = True
            boss_timer = pygame.time.get_ticks()

        if score == 40 and not boss_2_active:
            music_enabled = False
            toggle_music()
            boss_music.play()
            boss_2 = LaserBoss()
            boss_2_active = True
            boss_timer = pygame.time.get_ticks()

        if score % 10 == 0 and score > 0:
            meteor_speed += 0.2
            spawn_delay = max(300, spawn_delay - 50)
            pygame.time.set_timer(pygame.USEREVENT, spawn_delay)

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 790 <= x <= 840 and 550 <= y <= 590:
                scary = pygame.image.load("images/putin.jpg")
                scary = pygame.transform.scale(scary, (W, H))
                sc.blit(scary, (0, 0))
                pygame.display.flip()
                putin_core.play()
                pygame.time.delay(5500)
                exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            if pygame.time.get_ticks() - boss_timer >= 15000:
                boss_music.stop()
                music_enabled = True
                toggle_music()
                boss_active = False
                boss_2_active = False
                boss = None
                boss_2 = None
                ufo_charges = []
                boss_lasers.empty()
                meteor_speed = 5

def update_game_state():
    global paused, boss
    if not paused:
        player.update()
        meteors.update(H)
        powerups.update()
        if boss_active:
            boss.move()
            boss.shoot()
            for ball in ufo_charges:
                ball.update()
        if boss_2_active:
            boss_2.move()
            boss_lasers.update()


def render_game():
    sc.blit(bg, (0, 0))
    if boss_active:
        sc.blit(ufo_image, ufo_rect)
        for ball in ufo_charges:
            ball.draw(sc)
    if boss_2_active:
        sc.blit(boss_image, boss_rect)
        boss_lasers.draw(sc)

    draw_score(score)
    player.collides()
    player.animation()
    meteors.draw(sc)
    powerups.draw(sc)
    pygame.display.update()

main_menu()
while True:
    if game_over:
        handle_game_over()
    else:
        handle_events()
        update_game_state()
        render_game()
        clock.tick(FPS)