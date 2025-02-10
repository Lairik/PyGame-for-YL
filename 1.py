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

pygame.mixer.music.load('sounds/neukrotimoe-stremlenie-k-pobede-2341.ogg')
pygame.mixer.music.play(-1)

col_m = pygame.mixer.Sound("sounds/inecraft_damage.ogg")

br_m = pygame.mixer.Sound("sounds/vitayuschiy-v-oblakah-mechtatel-321.ogg")
met_m = pygame.mixer.Sound("sounds/inecraft_levelu.ogg")
met_m.set_volume(0.1)

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
        self.image = surf
        self.rect = self.image.get_rect(center=(x, 0))
        self.speed = meteor_speed
        self.add(group)

    def update(self, *args):
        global score
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

class Hero(pygame.sprite.Sprite):
    def __init__(self, player_img, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.img = player_img
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.left = False
        self.right = False
        self.count = 0

class Player(Hero):
    def collides(self):
        global game_over
        for meteor in meteors:
            if player.rect.inflate(-50, -20).colliderect(meteor.rect.inflate(-20, -50)):
                col_m.play()
                game_over = True
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
            self.count = 0

    def animation(self):
        if self.count + 1 > 40:
            self.count = 0
        if self.left == True:
            sc.blit(walk_left[self.count // 8], (self.rect.x, self.rect.y))
            self.count += 1
        elif self.right == True:
            sc.blit(walk_right[self.count // 8], (self.rect.x, self.rect.y))
            self.count += 1
        else:
            sc.blit(walk_no_movement[self.count // 9], (self.rect.x, self.rect.y))
            self.count += 1

player_img = pygame.image.load('images/no movement/1.png')

player = Player(player_img, W//2 - 50, 390, 7)

bg_2 = pygame.image.load('images/космос.jpg').convert_alpha()
bg_2 = pygame.transform.scale(bg_2, (900, 600))

game_over = False
record = 0



while True:
    if game_over:
        br_m.play()
        music_stop()
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


    if paused:
        f2 = pygame.font.Font(None, 70)
        pause_text = f2.render("Пауза", True, WHITE, BLUE)
        sc.blit(pause_text, (W // 2 - 60, H // 3))
        pygame.display.update()
        continue

    sc.blit(bg, (0, 0))
    player.collides()
    meteors.draw(sc)
    player.update()
    player.animation()
    pygame.display.update()


    clock.tick(FPS)
    meteors.update(H)


