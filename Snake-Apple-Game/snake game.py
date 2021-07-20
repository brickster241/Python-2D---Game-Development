import pygame
import random
from collections import deque

pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 255, 255)
purple = (128, 0, 128)
yellow = (255, 255, 0)

display_width = 900
display_height = 600

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Snake Apple Game')
icon = pygame.image.load('images/icon.png')
pygame.display.set_icon(icon)

block_size = 30
img = pygame.image.load('images/head.png').convert_alpha()
img = pygame.transform.scale(img, (block_size, block_size))

menu = pygame.image.load('images/menu.jpg').convert_alpha()
menu = pygame.transform.scale(menu, (display_width, display_height))


clock = pygame.time.Clock()
FPS = 30


def game_intro():
    while True:
        gameDisplay.fill(black)
        gameDisplay.blit(menu, (0, 0))
        message_to_screen("   Welcome to Snake Game   ", 75, (display_width // 2, display_height // 2), green, -50)
        message_to_screen("Press Space to PLAY !", 40, (display_width // 2, display_height // 2), white, 70)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    gameLoop()


def message_to_screen(msg, font_size, center, color, y_displace=0):
    font = pygame.font.SysFont(None, font_size)
    txt = font.render(msg, True, color, black)
    txt_rect = txt.get_rect()
    txt_rect.center = (center[0], center[1] + y_displace)
    gameDisplay.blit(txt, txt_rect)


def snake_coords(snake, x, y, pos):
    if len(snake) > 0:
        xi, yi = snake.pop()
        pos[(xi, yi)] = pos.get((xi, yi), 1) - 1
    snake.appendleft((x, y))
    pos[(x, y)] = pos.get((x, y), 0) + 1


def draw_snake(snake, block_size, img, direction):
    if direction == "U":
        head = pygame.transform.rotate(img, 0)
    elif direction == "D":
        head = pygame.transform.rotate(img, 180)
    elif direction == "R":
        head = pygame.transform.rotate(img, 270)
    else:
        head = pygame.transform.rotate(img, 90)

    gameDisplay.blit(head, snake[0])
    for i in range(1, len(snake)):
        x, y = snake[i][0], snake[i][1]
        pygame.draw.rect(gameDisplay, green, [x, y, block_size, block_size])


def draw_grid():
    for i in range(block_size, display_width, block_size):
        pygame.draw.line(gameDisplay, white, (i, block_size), (i, display_height - block_size), 1)
    for i in range(block_size, display_height, block_size):
        pygame.draw.line(gameDisplay, white, (block_size, i), (display_width - block_size, i), 1)


def gameLoop():
    direction = "R"
    gameExit = False
    gameOver = False
    FPS = 15
    maxScore = 0

    lead_x = display_width // 2 - ((display_width // 2) % block_size)
    lead_y = display_height // 2 - ((display_height // 2) % block_size)

    lead_x_change = 0
    lead_y_change = 0
    pos = dict()
    pos[(lead_x, lead_y)] = 1

    apple_x = random.randrange(block_size, display_width - block_size, block_size)
    apple_y = random.randrange(block_size, display_height - block_size, block_size)

    snake = deque()
    snake.append((lead_x, lead_y))

    pygame.mixer.init()
    pygame.mixer.music.load("sounds/sound.mp3")
    pygame.mixer.music.set_volume(0.7)

    while not gameExit:

        while gameOver:
            gameDisplay.blit(menu, (0, 0))
            message_to_screen("GAME OVER :)", 40, (display_width // 2, display_height // 2), green, -100)
            message_to_screen("Your Score : {}".format(len(snake) - 1), 30,(display_width // 2, display_height // 2), white, 0)
            message_to_screen("Press C to Play Again or Q to Quit", 30, (display_width // 2, display_height // 2), blue, 100)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        gameExit = True
                        gameOver = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameExit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    direction = "L"
                    lead_x_change = -block_size
                    lead_y_change = 0
                elif event.key == pygame.K_RIGHT:
                    direction = "R"
                    lead_x_change = block_size
                    lead_y_change = 0
                elif event.key == pygame.K_UP:
                    direction = "U"
                    lead_y_change = -block_size
                    lead_x_change = 0
                elif event.key == pygame.K_DOWN:
                    direction = "D"
                    lead_y_change = block_size
                    lead_x_change = 0

        lead_x += lead_x_change
        lead_y += lead_y_change
        snake_coords(snake, lead_x, lead_y, pos)
        if pos[(lead_x, lead_y)] > 1:
            pygame.mixer.music.load("sounds/gameOver.mp3")
            pygame.mixer.music.play()
            pygame.time.wait(1000)
            gameOver = True

        if lead_x == apple_x and lead_y == apple_y:
            apple_x = random.randrange(block_size, display_width - block_size, block_size)
            apple_y = random.randrange(block_size, display_height - block_size, block_size)
            snake.append((snake[-1][0] + lead_x_change, snake[-1][1] + lead_y_change))
            maxScore = max(len(snake), maxScore)
            pygame.mixer.music.play()
            if len(snake) % 5 == 0:
                FPS += 2
            # print(len(snake))
        if lead_x > display_width - 2 * block_size or lead_x < block_size or lead_y > display_height - 2 * block_size or lead_y < block_size:
            pygame.mixer.music.load("sounds/gameOver.mp3")
            pygame.mixer.music.play()
            pygame.time.wait(1000)
            gameOver = True

        gameDisplay.blit(menu, (0, 0))
        draw_snake(snake, block_size, img, direction)
        pygame.draw.rect(gameDisplay, red, (apple_x, apple_y, block_size, block_size))
        draw_grid()
        message_to_screen("Current Score : {}".format(len(snake) - 1), block_size, (display_width // 2, display_height // 2), white, - display_height // 2 + block_size // 2)
        pygame.display.update()

        clock.tick(FPS)

    pygame.quit()
    quit()


game_intro()
