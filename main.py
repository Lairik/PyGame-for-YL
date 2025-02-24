import pygame
import json
import random

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
paused = False
game_over = False
score = 0
record = 0
meteor_speed = 5
spawn_delay = 1000
boss_active = False
boss_timer = 0
vol = 0.4
fl_music = True
ufo_speed = 3
ufo_charges = []

# Загрузка метеоритов
pygame.time.set_timer(pygame.USEREVENT, spawn_delay)

# Загрузка звуков
col_m = pygame.mixer.Sound("sounds/inecraft_damage.ogg")
br_m = pygame.mixer.Sound("sounds/vitayuschiy-v-oblakah-mechtatel-321.ogg")
br_m.set_volume(0.3)
putin_core = pygame.mixer.Sound("sounds/vyi-rabotat-budete.ogg")
putin_core.set_volume(0.7)
met_m = pygame.mixer.Sound("sounds/inecraft_levelu.ogg")
met_m.set_volume(0)

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
        pygame.draw.circle(sc, GREEN, self.rect.center, 10)


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
            met_m.play()
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.img = walk_no_movement[0]
        self.image = pygame.transform.scale(self.img, (10, 10))
        self.rect = self.img.get_rect(center=(x, y))
        self.rect.x = x - 20
        self.rect.y = y
        self.speed = 7
        self.is_shielded = False
        self.boosted = False
        self.left = False
        self.right = False
        self.count = 0

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
            self.boosted = True
            self.speed += 3
            pygame.time.set_timer(pygame.USEREVENT + 2, 7000)
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
        global game_over
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
                    col_m.play()
                    game_over = True

        for ball in ufo_charges:
            if ball.rect.top >= H - 10:
                ufo_charges.remove(ball)
            if self.rect.inflate(-100, -20).colliderect(ball.rect):
                col_m.play()
                game_over = True

def create_powerup(group):
    max_attempts = 10
    if random.randint(1, 10) > 9:
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


def music_stop():
    global fl_music
    fl_music = not fl_music
    if fl_music:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

def main_menu():
    global play, paused

    running = True
    while running:


        bg_main = pygame.image.load('images/bg_main.png')
        sc.blit(bg_main, (0, 0))

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
                    running = False
                elif settings_button_rect.collidepoint(x, y):
                    settings_menu()
                elif rules_button_rect.collidepoint(x, y):
                    rules_menu()

def settings_menu():
    running = True
    while running:
        settings_img = pygame.image.load("images/set.png")
        sc.blit(settings_img, (-100, -50))
        font = pygame.font.Font(None, 36)
        settings_text = font.render("Настройки (нажмите Esc для возврата)", True, WHITE, BLACK)
        sc.blit(settings_text, (10, 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

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


# Инициализация игрока
player = Player(W // 2 - 50, 390)

# Инициализация экрана
sc = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()


def handle_game_over():
    global game_over, score, record, meteors, powerups, ufo_charges, boss_active, boss, meteor_speed, spawn_delay, fl_music, paused

    # Остановка музыки и воспроизведение звука завершения игры
    music_stop()
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

        # Кнопки "Играть снова" и "Выход"
        play_again_button = f1.render("Играть снова", True, BLACK, GREEN)
        exit_button = f1.render("Выход", True, BLACK, GREEN)
        sc.blit(play_again_button, (W // 2 - 80, H // 2))
        sc.blit(exit_button, (W // 2 - 50, H // 2 + 50))

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
                if W // 2 - 80 <= x <= W // 2 + 80 and H // 2 <= y <= H // 2 + 30:
                    # Сброс состояния игры
                    meteors.empty()
                    powerups.empty()
                    ufo_charges.clear()
                    boss_active = False
                    boss = None
                    score = 0
                    meteor_speed = 5
                    spawn_delay = 1000
                    pygame.time.set_timer(pygame.USEREVENT, spawn_delay)
                    game_over = False
                    br_m.stop()
                    music_stop()
                    return  # Выход из функции и возврат в основной цикл
                # Если нажата кнопка "Выход"
                elif W // 2 - 50 <= x <= W // 2 + 50 and H // 2 + 50 <= y <= H // 2 + 80:
                    pygame.quit()
                    exit()

# Example of modularizing the game loop
def handle_events():
    global paused, boss_active, br_m, putin_core, vol, boss, boss_timer, spawn_delay, meteor_speed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.USEREVENT:
            if not paused and not(boss_active):
                createMeteorit(meteors)
                create_powerup(powerups)
        elif event.type == pygame.USEREVENT + 1:
            player.is_shielded = False
        elif event.type == pygame.USEREVENT + 2:
            player.speed = 7

        if score == 3 and not boss_active:
            boss = UFOBoss()
            boss_active = True
            boss_timer = pygame.time.get_ticks()

        if score % 10 == 0 and score > 0:
            meteor_speed += 0.2
            spawn_delay = max(300, spawn_delay - 50)
            pygame.time.set_timer(pygame.USEREVENT, spawn_delay)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_v:
                music_stop()
            elif event.key == pygame.K_UP:
                vol += 0.1
                pygame.mixer.music.set_volume(vol)
            elif event.key == pygame.K_DOWN:
                vol -= 0.1
                pygame.mixer.music.set_volume(vol)
            elif event.key == pygame.K_z:
                scary = pygame.image.load("images/putin.jpg")
                scary = pygame.transform.scale(scary,(W, H))
                sc.blit(scary, (0, 0))
                music_stop()
                pygame.display.flip()
                putin_core.play()
                pygame.time.delay(5500)
                exit()

            if pygame.time.get_ticks() - boss_timer >= 15000:
                boss_active = False
                boss = None

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

def render_game():
    sc.blit(bg, (0, 0))
    if boss_active:
        sc.blit(ufo_image, ufo_rect)
        for ball in ufo_charges:
            ball.draw(sc)
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
