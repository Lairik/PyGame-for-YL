import pygame
import random
import time

pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Уклонение от метеоритов")

background_image = pygame.image.load('фон42.PNG')
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Персонаж
player_size = 50
player_x = WIDTH // 2 - player_size // 2
player_y = HEIGHT - 125
player_speed = 7

# Метеориты
meteor_size = 40
meteors = []
meteor_speed = 3
meteor_spawn_time = 700  # В миллисекундах

# Счет
score = 0
font = pygame.font.Font(None, 36)

# Таймер игры
start_time = time.time()

# Игровой цикл
clock = pygame.time.Clock()
running = True
game_over = False
last_spawn_time = pygame.time.get_ticks()

while running:
    screen.blit(background_image, (0, 0))

    if not game_over:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Управление игроком
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed

        # Спавн метеоритов
        if pygame.time.get_ticks() - last_spawn_time > meteor_spawn_time:
            meteor_x = random.randint(0, WIDTH - meteor_size)
            meteors.append([meteor_x, 0])
            last_spawn_time = pygame.time.get_ticks()

        # Движение метеоритов
        for meteor in meteors[:]:
            meteor[1] += meteor_speed
            if meteor[1] > HEIGHT:
                meteors.remove(meteor)
                score += 1
                # Увеличение скорости метеоритов
                if score % 10 == 0:
                    meteor_speed += 1

        # Проверка столкновений
        for meteor in meteors:
            if (
                player_x < meteor[0] < player_x + player_size or
                player_x < meteor[0] + meteor_size < player_x + player_size
            ) and player_y < meteor[1] + meteor_size < player_y + player_size:
                game_over = True
                end_time = time.time()
                game_duration = round(end_time - start_time, 2)

        # Отрисовка игрока и метеоритов
        pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
        for meteor in meteors:
            pygame.draw.rect(screen, RED, (meteor[0], meteor[1], meteor_size, meteor_size))

        # Отображение счета
        score_text = font.render(f"Счет: {score}", True, BLACK)
        screen.blit(score_text, (WIDTH - 120, 10))

    else:
        # Экран окончания
        game_over_text = font.render(f"Игра окончена!", True, BLACK)
        score_text = font.render(f"Счет: {score}", True, BLACK)
        time_text = font.render(f"Время: {game_duration} сек", True, BLACK)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2))
        screen.blit(time_text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))


    pygame.display.flip()
    clock.tick(30)

pygame.quit()
