import pygame
from random import randint
import json


paused = False

pygame.font.init()
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

spawn_delay = 1000

pygame.time.set_timer(pygame.USEREVENT, spawn_delay)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (100, 100, 255)
W, H = 900, 600

score = 0

# pygame.mixer.music.load('sounds/neukrotimoe-stremlenie-k-pobede-2341.ogg')
# pygame.mixer.music.play(-1)

col_m = pygame.mixer.Sound("sounds/inecraft_damage.ogg")

br_m = pygame.mixer.Sound("sounds/vitayuschiy-v-oblakah-mechtatel-321.ogg")
br_m.set_volume(0.3)

putin_core = pygame.mixer.Sound("sounds/vyi-rabotat-budete.ogg")
putin_core.set_volume(0.7)

met_m = pygame.mixer.Sound("sounds/inecraft_levelu.ogg")
met_m.set_volume(0)

walk_left = [
    pygame.image.load('images/left/1.png'),
    pygame.image.load('images/left/2.png'),
    pygame.image.load('images/left/3.png'),
    pygame.image.load('images/left/4.png'),
    pygame.image.load('images/left/5.png'),
    pygame.image.load('images/left/6.png'),
    pygame.image.load('images/left/7.png'),
    pygame.image.load('images/left/8.png'),
]

walk_no_movement = [
    pygame.image.load('images/no movement/1.png'),
    pygame.image.load('images/no movement/2.png'),
    pygame.image.load('images/no movement/3.png'),
    pygame.image.load('images/no movement/4.png'),
    pygame.image.load('images/no movement/5.png'),
    pygame.image.load('images/no movement/6.png'),
    pygame.image.load('images/no movement/7.png'),
    pygame.image.load('images/no movement/8.png'),
    pygame.image.load('images/no movement/9.png'),
]

walk_right = [
    pygame.image.load('images/right/1.png'),
    pygame.image.load('images/right/2.png'),
    pygame.image.load('images/right/3.png'),
    pygame.image.load('images/right/4.png'),
    pygame.image.load('images/right/5.png'),
    pygame.image.load('images/right/6.png'),
    pygame.image.load('images/right/7.png'),
    pygame.image.load('images/right/8.png'),
]

meteor_frames = [
    pygame.image.load('images/meteorit/1.png'),
    pygame.image.load('images/meteorit/2.png'),
    pygame.image.load('images/meteorit/3.png'),
    pygame.image.load('images/meteorit/4.png'),
    pygame.image.load('images/meteorit/5.png'),
    pygame.image.load('images/meteorit/6.png'),
]

sc = pygame.display.set_mode((W, H))

bg = pygame.image.load('images/фон.PNG')
bg = pygame.transform.scale(bg, (1800 / 2, 1200 / 2))

met_img = pygame.image.load('images/meteorit/1.png')
met_img = pygame.transform.scale(met_img, (120, 110))

clock = pygame.time.Clock()
FPS = 60

meteor_speed = 5
play = True
class Meteorit(pygame.sprite.Sprite):
    def __init__(self, x, surf, group):
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

def createMeteorit(group):
    x = randint(20, W - 20)
    return Meteorit(x, met_img, group)

meteors = pygame.sprite.Group()

fl_music = True

vol = 0.4

pygame.mixer.music.set_volume(vol)
def music_stop():
    global fl_music
    fl_music = not fl_music
    if fl_music:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.img = walk_no_movement[0]
        self.rect = self.img.get_rect(center=(x, y))
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.left = False
        self.right = False
        self.count = 0


    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > 5:
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


    def animation(self):
        if self.count + 1 > 60:
            self.count = 0
        if self.left:
            sc.blit(walk_left[self.count // 8], (self.rect.x, self.rect.y))
        elif self.right:
            sc.blit(walk_right[self.count // 8], (self.rect.x, self.rect.y))
        else:
            sc.blit(walk_no_movement[self.count // 9], (self.rect.x, self.rect.y))

        self.count += 1

    def collides(self):
        global game_over
        for meteor in meteors:
            if player.rect.inflate(-100, -20).colliderect(meteor.rect.inflate(-20, -50)):
                col_m.play()
                game_over = True


player = Player(W//2 - 50, 390, 7)

bg_2 = pygame.image.load('images/космос.jpg').convert_alpha()
bg_2 = pygame.transform.scale(bg_2, (900, 600))

game_over = False
record = 0

def main_menu():
    global play, paused

    running = True
    while running:

        bg_main = pygame.image.load('images/bg.jpg')

        sc.blit(bg_main, (0, 0))

        # Создаем шрифт для кнопок
        font = pygame.font.Font(None, 50)

        # Рендер кнопок
        play_button = font.render("Играть", True, WHITE)
        settings_button = font.render("Настройки", True, WHITE, GREEN)
        rules_button = font.render("Правила игры", True, WHITE, GREEN)

        # Позиционируем кнопки
        play_button_rect = play_button.get_rect(center=(W // 2, H // 3))
        settings_button_rect = settings_button.get_rect(center=(W // 2, H // 2))
        rules_button_rect = rules_button.get_rect(center=(W // 2, H // 1.5))

        # Отображаем кнопки на экране
        sc.blit(play_button, play_button_rect)
        sc.blit(settings_button, settings_button_rect)
        sc.blit(rules_button, rules_button_rect)

        pygame.display.flip()

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if play_button_rect.collidepoint(x, y):
                    # Начать игру
                    running = False
                elif settings_button_rect.collidepoint(x, y):
                    settings_menu()
                elif rules_button_rect.collidepoint(x, y):
                    rules_menu()

def settings_menu():
    running = True
    while running:
        sc.fill(BLACK)
        font = pygame.font.Font(None, 36)
        settings_text = font.render("Настройки (нажмите Esc для возврата)", True, WHITE)
        sc.blit(settings_text, (W // 4, H // 3))

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
        sc.fill(BLACK)
        font = pygame.font.Font(None, 36)
        rules_text = font.render("Правила игры: Избегайте метеоритов!", True, WHITE)
        sc.blit(rules_text, (W // 4, H // 3))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

def draw_score(score):
    # Задаём шрифт и размер
    font = pygame.font.Font(None, 36)

    # Создаём текст для счёта
    score_text = font.render(f"Счёт: {score}", True, WHITE)

    # Позиция текста
    score_rect = score_text.get_rect(topright=(W - 20, 20))

    # Отрисовка фона для плашки
    pygame.draw.rect(sc, BLACK, (score_rect.x - 10, score_rect.y - 5, score_rect.width + 20, score_rect.height + 10), border_radius=10)

    # Отображаем текст поверх фона
    sc.blit(score_text, score_rect)


main_menu()
while True:
    if game_over:
        music_stop()
        br_m.play()
        if score > record:
            record = score
            with open("record.json", "w") as f:
                json.dump(record, f)

        while game_over:
            sc.blit(bg_2,(0, 0))

            f1 = pygame.font.Font(None, 36)

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

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if W // 2 - 80 <= x <= W // 2 + 80 and H // 2 <= y <= H // 2 + 30:
                        meteors.empty()
                        score = 0
                        meteor_speed = 5
                        spawn_delay = 1000
                        pygame.time.set_timer(pygame.USEREVENT, spawn_delay)
                        game_over = False
                        br_m.stop()
                        music_stop()
                        break
                    if W // 2 - 50 <= x <= W // 2 + 50 and H // 2 + 50 <= y <= H // 2 + 80:
                        pygame.quit()
                        exit()
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.USEREVENT:
                if not paused:
                    createMeteorit(meteors)
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

    if paused:
        f2 = pygame.font.Font(None, 70)
        pause_text = f2.render("Пауза", True, WHITE, BLUE)
        sc.blit(pause_text, (W // 2 - 60, H // 3))
        pygame.display.update()
        continue

    sc.blit(bg, (0, 0))
    draw_score(score)
    player.collides()
    meteors.draw(sc)
    player.update()
    player.animation()
    pygame.display.update()


    clock.tick(FPS)
    meteors.update(H)