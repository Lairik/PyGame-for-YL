import pygame
import json
import random
import math
import time

pygame.font.init()
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

W, H = 900, 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
BLUE = (100, 100, 255)
GRAY = (150, 150, 150)
RED = (255, 50, 50)

bg_main = pygame.image.load('images/bg_main.png')

bg = pygame.image.load('images/фон.PNG')
bg = pygame.transform.scale(bg, (W, H))

bg_2 = pygame.image.load('images/космос.jpg')
bg_2 = pygame.transform.scale(bg_2, (W, H))

ufo_image = pygame.image.load("images/ufo.png")
ufo_image = pygame.transform.scale(ufo_image, (170, 110))
ufo_rect = ufo_image.get_rect(centerx = W//2, centery = 100)

boss_image = pygame.image.load("images/LazerBoss.png")
boss_image = pygame.transform.scale(boss_image, (565 // 6, 920 // 6))
boss_rect = boss_image.get_rect(centerx = W//2, centery = 100)

full_heart = pygame.image.load("images/full_heart.png")
empty_heart = pygame.image.load("images/empty_heart.png")
full_heart = pygame.transform.scale(full_heart, (40, 40))
empty_heart = pygame.transform.scale(empty_heart, (40, 40))

score_view = pygame.image.load("images/score_view.png")
score_view = pygame.transform.scale(score_view, (908 // 6, 678 // 6))

walk_left = [pygame.image.load(f'images/left/{i}.png') for i in range(1, 9)]
walk_no_movement_left = [pygame.image.load(f'images/no movement/left/{i}.png') for i in range(1, 10)]
walk_no_movement_right = [pygame.image.load(f'images/no movement/right/{i}.png') for i in range(1, 10)]
walk_right = [pygame.image.load(f'images/right/{i}.png') for i in range(1, 8)]
meteor_frames = [pygame.image.load(f'images/meteorit/{i}.png') for i in range(1, 7)]

shield_img = pygame.image.load("images/shield.png")
booster_img = pygame.image.load("images/booster.png")
health_img = pygame.image.load("images/health.png")
shield_overlay = pygame.image.load("images/shield_effect.png")
shield_overlay = pygame.transform.scale(shield_overlay, (164, 164))


colors = {
    "Щит": BLUE,
    "Ускорение": GREEN,
}

active_powerups = {}
game_start_time = 0
elapsed_time = None
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
music_enabled = True
ufo_charges = []

pygame.time.set_timer(pygame.USEREVENT, spawn_delay)

music_volume = 0.5
pygame.mixer.music.set_volume(music_volume)

slider_start_x = 10
slider_end_x = 210
slider_y = 100
slider_width = 200
slider_height = 5
marker_radius = 10

slider_x = slider_start_x + int(music_volume * slider_width)

dragging = False
bg_music = pygame.mixer.Sound("sounds/bgmusic.ogg")
bg_music.set_volume(music_volume)
boss_music = pygame.mixer.Sound("sounds/boss_music.ogg")
boss_music.set_volume(music_volume)
br_m = pygame.mixer.Sound("sounds/vitayuschiy-v-oblakah-mechtatel-321.ogg")
br_m.set_volume(music_volume)
putin_core = pygame.mixer.Sound("sounds/vyi-rabotat-budete.ogg")
putin_core.set_volume(music_volume)
col_music = pygame.mixer.Sound("sounds/inecraft_damage.ogg")
col_music.set_volume(music_volume)

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
        if random.randint(1, 70) == 1:
            ball = GreenBall(ufo_rect.centerx, self.rect.centery, random.choice([-4, 4]), 3)
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

    def kill(self):
        ufo_charges.remove(self)

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
        self.img = pygame.transform.scale(pygame.image.load("images/no movement/left/1.png"), (128, 128))
        self.rect = self.img.get_rect(center=(x, y))
        self.rect.x = x
        self.rect.y = y
        self.hitbox = pygame.Rect(self.rect.x + 20 , self.rect.y + 20, self.rect.width - 40, self.rect.height - 35)
        self.is_shielded = False
        self.boosted = False
        self.left = False
        self.right = False
        self.count = 0
        self.speed = speed
        self.health = 3
        self.facing_left = True
        self.invincibility_timer = 0


    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
            self.left = True
            self.right = False
        elif keys[pygame.K_RIGHT] and self.rect.x < W - 100:
            self.rect.x += self.speed
            self.left = False
            self.right = True
        else:
            self.left = False
            self.right = False

        self.hitbox.x = self.rect.x + 5
        self.hitbox.y = self.rect.y + 20

        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

    # def draw_hitbox(self, screen):
    #     pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)

    def apply_powerup(self, powerup):
        global active_powerups
        if powerup.type == "shield":
            self.is_shielded = True
            active_powerups["Щит"] = 5
            pygame.time.set_timer(pygame.USEREVENT + 1, 5000)
        elif powerup.type == "booster":
            if self.speed == 7:
                self.speed = 10
            active_powerups["Ускорение"] = 5
            pygame.time.set_timer(pygame.USEREVENT + 2, 5000)
        elif powerup.type == "health":
            if self.health != 3:
                self.health += 1
        powerup.kill()

    def animation(self):
        total_frames = 60
        self.count = (self.count + 1) % total_frames

        walk_right_index = (self.count // 8) % len(walk_right)
        walk_left_index = (self.count // 8) % len(walk_left)
        idle_left_index = (self.count // 9) % len(walk_no_movement_left)
        idle_right_index = (self.count // 9) % len(walk_no_movement_right)

        if self.left:
            sc.blit(walk_left[walk_left_index], (self.rect.x, self.rect.y))
            self.facing_left = True
        elif self.right:
            sc.blit(walk_right[walk_right_index], (self.rect.x, self.rect.y))
            self.facing_left = False
        else:
            idle_animation = walk_no_movement_left if self.facing_left else walk_no_movement_right
            idle_index = idle_left_index if self.facing_left else idle_right_index
            sc.blit(pygame.transform.scale(idle_animation[idle_index], (92, 128)), (self.rect.x, self.rect.y))

        if self.is_shielded:
            shield_x = self.rect.centerx - shield_overlay.get_width() // 2
            shield_y = self.rect.centery - shield_overlay.get_height() // 2
            sc.blit(shield_overlay, (shield_x, shield_y))

    def handle_collision(self, sprite_group, collision_type):
        global game_over, active_powerups
        for sprite in sprite_group:
            if self.hitbox.colliderect(sprite.rect):
                sprite.kill()
                if self.is_shielded:
                    self.is_shielded = False
                    active_powerups["Щит"] = 0
                elif self.invincibility_timer == 0:
                    self.health -= 1
                    self.invincibility_timer = 30
                    if self.health <= 0:
                        game_over = True
                    col_music.play()

    def collides(self):
        for powerup in powerups:
            if self.hitbox.colliderect(powerup.rect):
                self.apply_powerup(powerup)

        self.handle_collision(meteors, 'meteor')
        self.handle_collision(ufo_charges, 'ufo_charge')
        self.handle_collision(boss_lasers, 'laser')

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
                power_type = random.choice(["shield", "booster", "health"])
                if power_type == "shield":
                    image = shield_img
                elif power_type == "booster":
                    image = booster_img
                else:
                    image = health_img
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
    global score_view
    score_img_rect = score_view.get_rect(topleft=(10, 55))
    sc.blit(score_view, score_img_rect)
    font = pygame.font.Font(None, 40)
    score_text = font.render(f" {score}", True, WHITE)
    score_rect = score_text.get_rect(topleft=(95, 140))
    sc.blit(score_text, score_rect)
    elapsed_time = int(time.time() - game_start_time)
    time_text = font.render(f" {elapsed_time}с.", True, WHITE)
    time_rect = time_text.get_rect(topleft=(115, 90))
    sc.blit(time_text, time_rect)

def toggle_music():
    global music_enabled
    if music_enabled:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

def draw_health(sc):
    for i in range(3):
        heart_x = 10 + i * 50
        if i < player.health:
            sc.blit(full_heart, (heart_x, 10))
        else:
            sc.blit(empty_heart, (heart_x, 10))

def main_menu():
    global play, paused, bg_main

    br_m.stop()

    running = True
    while running:
        sc.blit(bg_main, (0, 0))

        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load('sounds/bgmusic.ogg')
            pygame.mixer.music.play(-1)

        chill_preview = pygame.image.load('images/no movement/left/1.png')
        chill_preview = pygame.transform.scale(chill_preview, (128, 128))
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
    global dragging, music_volume, slider_start_x


    slider_x = slider_start_x + int(music_volume * slider_width)

    running = True
    while running:
        settings_img = pygame.image.load("images/set.png")
        sc.blit(settings_img, (-100, -50))
        font = pygame.font.Font(None, 36)

        settings_text = font.render("Настройки (нажмите Esc для возврата)", True, WHITE, BLACK)
        sc.blit(settings_text, (10, 10))

        music_toggle_text = font.render("Регулировка музыки", True, WHITE, BLACK)
        music_toggle_rect = music_toggle_text.get_rect(topleft=(10, 50))
        sc.blit(music_toggle_text, music_toggle_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if (slider_x - marker_radius <= mouse_x <= slider_x + marker_radius and
                        slider_y - marker_radius <= mouse_y <= slider_y + marker_radius):
                    dragging = True

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    slider_x = max(slider_start_x, min(slider_end_x, event.pos[0]))
                    music_volume = (slider_x - slider_start_x) / slider_width
                    pygame.mixer.music.set_volume(music_volume)
                    bg_music.set_volume(music_volume)
                    boss_music.set_volume(music_volume)
                    br_m.set_volume(music_volume)
                    putin_core.set_volume(music_volume)
                    col_music.set_volume(music_volume)

        pygame.draw.line(sc, GRAY, (slider_start_x, slider_y), (slider_end_x, slider_y), slider_height)
        pygame.draw.circle(sc, RED, (slider_x, slider_y), marker_radius)

        volume_text = font.render(f"Громкость: {int(music_volume * 100)}%", True, WHITE)
        sc.blit(volume_text, (10, slider_y + 25))

        pygame.display.update()

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

def draw_powerup_timer(sc):
    global active_powerups, colors
    font = pygame.font.Font(None, 36)
    y_offset = 135

    for powerup_name, time_left in active_powerups.items():
        timer_text = font.render(f"{powerup_name}: {int(time_left)}s", True, colors.get(powerup_name, WHITE))
        timer_rect = timer_text.get_rect(topright=(W - 20, y_offset))
        pygame.draw.rect(sc, GRAY,(timer_rect.x - 10, timer_rect.y - 5, timer_rect.width + 20, timer_rect.height + 10), border_radius=10)
        sc.blit(timer_text, timer_rect)
        y_offset += 40

meteors = pygame.sprite.Group()
powerups = pygame.sprite.Group()
boss_lasers = pygame.sprite.Group()

player = Player(W//2 - 64, H - 210, player_speed)

sc = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()


def handle_game_over():
    global game_over, score, record, powerups, ufo_charges, spawn_delay, paused, music_enabled, boss_music, elapsed_time

    music_enabled = False
    toggle_music()
    boss_music.stop()
    br_m.play()

    if score > record:
        record = score
        with open("record.json", "w") as f:
            json.dump(record, f)

    while game_over:
        sc.blit(bg_2, (0, 0))

        f1 = pygame.font.Font(None, 36)

        title = f1.render("Игра окончена!", True, BLACK, WHITE)
        sc.blit(title, (W // 2 - 100, H // 4 - 50))

        score_text = f1.render(f"Ваш счет: {score}", True, BLACK, WHITE)
        record_text = f1.render(f"Рекорд: {record}", True, BLACK, WHITE)
        sc.blit(score_text, (W // 2 - 80, H // 4 + 50))
        sc.blit(record_text, (W // 2 - 80, H // 4 + 100))

        if elapsed_time is None:
            elapsed_time = int(time.time() - game_start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_text = f1.render(f"Вы продержались: {minutes}:{seconds:02}", True, BLACK, WHITE)
        sc.blit(time_text, (W // 2 - 160, H // 4))

        play_again_button = f1.render("Играть снова", True, BLACK, GREEN)
        exit_button = f1.render("Выход", True, BLACK, GREEN)
        main_button = f1.render("Главное меню", True, BLACK, GREEN)

        play_again_button_rect = play_again_button.get_rect(center=(W // 2 - 20, H // 2 + 10))
        exit_button_rect = exit_button.get_rect(center=(W // 2 - 10, H // 2 + 60))
        main_button_rect = main_button.get_rect(center=(W // 2 - 20, H // 2 + 110))

        sc.blit(play_again_button, play_again_button_rect)
        sc.blit(exit_button, exit_button_rect)
        sc.blit(main_button, main_button_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if play_again_button_rect.collidepoint(x, y):
                    resert()
                elif main_button_rect.collidepoint(x, y):
                    main_menu()

                elif exit_button_rect.collidepoint(x, y):
                    pygame.quit()
                    exit()

def resert():
    global player_speed, game_over, score, meteors, powerups, ufo_charges, boss_lasers, boss_active, boss_2_active, boss, boss_2, meteor_speed, spawn_delay, player, music_enabled, game_start_time, active_powerups
    player = None
    player = Player(W//2 - 64, H - 210, player_speed)
    meteors.empty()
    powerups.empty()
    boss_lasers.empty()
    ufo_charges.clear()
    active_powerups = {}
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
    game_start_time = time.time()

def handle_boss_spawn():
    global boss_active, boss_2_active, boss, boss_2, boss_timer, music_enabled
    if score == 45 and not boss_active:
        music_enabled = False
        toggle_music()
        boss_music.play()
        boss = UFOBoss()
        boss_active = True
        boss_timer = pygame.time.get_ticks()

    if score == 20 and not boss_2_active:
        music_enabled = False
        toggle_music()
        boss_music.play()
        boss_2 = LaserBoss()
        boss_2_active = True
        boss_timer = pygame.time.get_ticks()

def handle_difficulty_increase():
    global meteor_speed, spawn_delay
    if score % 5 == 0 and score > 0:
        meteor_speed += 0.2
        spawn_delay = max(400, spawn_delay - 50)
        pygame.time.set_timer(pygame.USEREVENT, spawn_delay)

def handle_events():
    global paused, boss_active, boss_2_active, br_m, putin_core, boss, boss_2, boss_timer, spawn_delay, meteor_speed, ufo_charges, music_enabled
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

        handle_boss_spawn()
        handle_difficulty_increase()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 790 <= x <= 840 and 550 <= y <= 590:
                scary = pygame.image.load("images/putin.jpg")
                scary = pygame.transform.scale(scary, (W, H))
                sc.blit(scary, (0, 0))
                pygame.display.flip()
                music_enabled = False
                toggle_music()
                putin_core.play()
                pygame.time.delay(5500)
                exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            if pygame.time.get_ticks() - boss_timer >= 22000:
                boss_music.stop()
                music_enabled = True
                toggle_music()
                boss_active = False
                boss_2_active = False
                boss = None
                boss_2 = None
                meteor_speed = 5

def update_game_state():
    global paused, boss, active_powerups
    if not paused:
        player.update()
        meteors.update(H)
        powerups.update()
        if boss_active:
            boss.move()
            boss.shoot()
        if boss_2_active:
            boss_2.move()
        boss_lasers.update()
        for ball in ufo_charges:
            ball.update()

    for powerup_name in list(active_powerups.keys()):
        active_powerups[powerup_name] -= 1 / FPS
        if active_powerups[powerup_name] <= 0:
            del active_powerups[powerup_name]
            if powerup_name == "Щит":
                player.is_shielded = False
            elif powerup_name == "Ускорение":
                player.boosted = False
                player.speed = 7


def render_game():
    sc.blit(bg, (0, 0))
    if boss_active:
        sc.blit(ufo_image, ufo_rect)

    if boss_2_active:
        sc.blit(boss_image, boss_rect)

    for ball in ufo_charges:
        ball.draw(sc)

    boss_lasers.draw(sc)
    draw_score(score)
    player.collides()
    player.animation()
    # player.draw_hitbox(sc)
    draw_health(sc)
    meteors.draw(sc)
    powerups.draw(sc)
    draw_powerup_timer(sc)
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