import pygame
import random
import math
from pygame import mixer

# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 600))

# Add a background
background = pygame.image.load("background.jpg")

# Background sound
mixer.music.load("openingTheme.mp3")
mixer.music.play(-1)

## Defining fonts
# Score
score_value = 0
font = pygame.font.Font("freesansbold.ttf", 24)

textX = 10
textY = 10

# Game over text
over_font = pygame.font.Font("freesansbold.ttf", 64)
# Top font
top_font = pygame.font.Font("freesansbold.ttf", 20)

# Default mode
def default_mode():
    mixer.music.load("openingTheme.mp3")
    mixer.music.play(-1)
    default_mode_text("Normal Mode")
    pygame.display.update()

# Gadhulacha Paani Mode
def gadhulacha_mode():
    mixer.music.load("kallulache_pani.mp3")
    mixer.music.play(-1)
    gadhulacha_text("Gadhulacha Paani!")
    pygame.display.update()

# Shantabai Mode
def shantabai_mode():
    mixer.music.load("shantabai.mp3")
    mixer.music.play(-1)
    shantabai_text("Shantabai!")
    pygame.display.update()

# Shiti vajali gadi sutali Mode
def shiti_mode():
    mixer.music.load("shiti.mp3")
    mixer.music.play(-1)
    shiti_text("Shiti vajali!")
    pygame.display.update()

# Astronomia Mode
def astronomia_mode():
    mixer.music.load("Coffin dance.mp3")
    mixer.music.play(-1)
    shiti_text("Astronomia!")
    pygame.display.update()

# Title and icon
pygame.display.set_caption("Meme Invaders")
icon = pygame.image.load("logo.png")
pygame.display.set_icon((icon))

# Player
playerImg = pygame.image.load("ship.png")
playerX = 370
playerY = 480
playerXchange = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyXchange = []
enemyYchange = []
num_of_enemies = 7

for i in range(num_of_enemies):
    enemy = "vadapav.png" 
    enemyImg.append(pygame.image.load(enemy))
    enemyX.append(random.randint(0, 736))
    enemyY.append(random.randint(50, 150))
    enemyXchange.append(4)
    enemyYchange.append(40)

# Bullet
# Ready- You can't see the bullet on the screen
# Fire- The bullet is currently moving
bulletImg = pygame.image.load("bullet.png")
bulletX = 0
bulletY = 480
bulletXchange = 0
bulletYchange = 10
bulletState = "ready"


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (0, 255, 0))
    screen.blit(score, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (0, 255, 0))
    screen.blit(over_text, (200, 250))

def gadhulacha_text(textentry):
    over_text = over_font.render(textentry, True, (150, 255, 100))
    screen.blit(over_text, (100, 250))

def shantabai_text(textentry):
    over_text = over_font.render(textentry, True, (150, 255, 100))
    screen.blit(over_text, (230, 250))

def shiti_text(textentry):
    over_text = over_font.render(textentry, True, (150, 255, 100))
    screen.blit(over_text, (220, 250))

def astronomia_text(textentry):
    over_text = over_font.render(textentry, True, (255, 255, 255))
    screen.blit(over_text, (280, 250))

def default_mode_text(textentry):
    over_text = over_font.render(textentry, True, (150, 255, 100))
    screen.blit(over_text, (190, 250))

def top_text(textentry):
    top_text = top_font.render(textentry, True, (0, 255, 0))
    screen.blit(top_text, (200, 10))

def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fireBullet(x, y):
    global bulletState
    bulletState = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((math.pow(enemyX - bulletX, 2)) + (math.pow(enemyY - bulletY, 2)))
    if distance < 27:
        return True
    else:
        return False

# Game Loop
running = True
while running:
    # RGB = Red green Blue
    screen.fill((0, 0, 0))

    # Background image
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # If keystroke is pressed check whether left or right
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            playerXchange = -5
        if event.key == pygame.K_RIGHT:
            playerXchange = 5
        if event.key == pygame.K_SPACE:
            if bulletState == "ready":
                bulletSound = mixer.Sound("laser.wav")
                bulletSound.play()
                # Get the current x co-ordinate of the spaceship
                bulletX = playerX
                fireBullet(bulletX, bulletY)
        if event.key == pygame.K_F1:
            background = pygame.image.load("gadhulacha_bg.jpg")
            playerImg = pygame.image.load("penguin.png")
            bulletImg = pygame.image.load("snake.png")
            gadhulacha_mode()

        if event.key == pygame.K_F2:
            shantabai_mode()

        if event.key == pygame.K_F3:
            shiti_mode()

        if event.key == pygame.K_F4:
            background = pygame.image.load("coffin_bg.jpg")
            playerImg = pygame.image.load("bow.png")
            bulletImg = pygame.image.load("arrow.png")
            astronomia_mode()

        if event.key == pygame.K_F12:
            background = pygame.image.load("background.jpg")
            playerImg = pygame.image.load("ship.png")
            bulletImg = pygame.image.load("bullet.png")
            default_mode()


    if event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            playerXchange = 0

    # Checking for boundaries of spaceship so it doesn't go out of bounds
    playerX += playerXchange

    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:
        playerX = 736

    # Enemy movement
    for i in range(num_of_enemies):
        # Game Over
        if enemyY[i] > 440:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            game_over_text()
            break

        enemyX[i] += enemyXchange[i]
        if enemyX[i] <= 0:
            enemyXchange[i] = 3
            enemyY[i] += enemyYchange[i]
        elif enemyX[i] >= 736:
            enemyXchange[i] = -3
            enemyY[i] += enemyYchange[i]

        # Collision
        collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
        if collision:
            explosionSound = mixer.Sound("explosion.wav")
            explosionSound.play()
            bulletY = 480
            bulletState = "ready"
            score_value += 1
            enemyX[i] = random.randint(0, 736)
            enemyY[i] = random.randint(50, 150)

        enemy(enemyX[i], enemyY[i], i)

    # Bullet movement
    if bulletY <= 0:
        bulletY = 500
        bulletState = "ready"

    if bulletState == "fire":
        fireBullet(bulletX, bulletY)
        bulletY -= bulletYchange

    player(playerX, playerY)
    show_score(textX, textY)
    top_text("Keep the vadapavs away from baby penguin!")
    pygame.display.update()
