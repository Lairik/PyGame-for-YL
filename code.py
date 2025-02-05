from random import random, randint

import pygame


class Bot(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position

    def update(self):
        x_move = randint(-3, 3)
        y_move = randint(0, 10)
        self.rect.x += x_move
        self.rect.y += y_move


class Player:
    def __init__(self, image, position):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= 5
        if keys[pygame.K_s]:
            self.rect.y += 5
        if keys[pygame.K_d]:
            self.rect.x += 5
        if keys[pygame.K_a]:
            self.rect.x -= 5
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > width - self.rect.width:
            self.rect.x = width - self.rect.width
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > height - self.rect.height:
            self.rect.y = height - self.rect.height


if __name__ == '__main__':
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)

    player_image = pygame.image.load('player.png')
    player_image = pygame.transform.scale(player_image, (900/7, 831/7))

    bd_image = pygame.image.load('bd.jpg')
    bd_image = pygame.transform.scale(bd_image, (1800 / 2, 1200 / 2))

    meteorit_image = pygame.image.load('meteorit.png')
    meteorit_image = pygame.transform.scale(meteorit_image, (80, 50))

    pygame.init()
    pygame.display.set_caption('Стетхом на ЗОНЕ')

    bot_group = pygame.sprite.Group()

    spawn_bot_event = pygame.USEREVENT
    pygame.time.set_timer(spawn_bot_event, 2000)

    running = True
    clock = pygame.time.Clock()

    player = Player(player_image, (width / 2, height / 2))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == spawn_bot_event:
                bot = Bot(meteorit_image, (randint(0, width), 0))
                bot_group.add(bot)

        screen.fill((255, 255, 255))
        screen.blit(bd_image, (0, 0))
        player.draw(screen)
        player.move()
        bot_group.draw(screen)
        bot_group.update()
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
