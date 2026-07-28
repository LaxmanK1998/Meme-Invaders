import pygame
import random
import math
import sys
import os
import json
from pygame import mixer

# Handle asset paths for PyInstaller executable
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 600))

# Add a background
background = pygame.image.load("background.jpg")

# Background sound
mixer.music.load("openingTheme.mp3")
mixer.music.play(-1)

# Leaderboard & High Score Persistence
HIGH_SCORES_FILE = "highscores.json"

def load_high_scores():
    if os.path.exists(HIGH_SCORES_FILE):
        try:
            with open(HIGH_SCORES_FILE, "r") as f:
                scores = json.load(f)
                if isinstance(scores, list):
                    return sorted(scores, key=lambda x: x.get("score", 0), reverse=True)[:5]
        except Exception:
            return []
    return []

def save_high_scores(scores_list):
    try:
        sorted_scores = sorted(scores_list, key=lambda x: x.get("score", 0), reverse=True)[:5]
        with open(HIGH_SCORES_FILE, "w") as f:
            json.dump(sorted_scores, f, indent=2)
    except Exception:
        pass

def add_high_score(name, score):
    scores = load_high_scores()
    player_name = name.strip().upper() if name.strip() else "PLAYER"
    scores.append({"name": player_name[:10], "score": score})
    save_high_scores(scores)

high_scores_list = load_high_scores()
high_score = high_scores_list[0]["score"] if high_scores_list else 0

## Defining fonts
score_value = 0
lives = 3
font = pygame.font.Font("freesansbold.ttf", 22)
over_font = pygame.font.Font("freesansbold.ttf", 64)
title_font = pygame.font.Font("freesansbold.ttf", 54)
top_font = pygame.font.Font("freesansbold.ttf", 20)
control_info_font = pygame.font.Font("freesansbold.ttf", 18)

# Game states: "START", "LEADERBOARD", "PLAYING", "GAME_OVER_NAME", "GAME_OVER"
game_state = "START"
is_muted = False
player_name_input = ""

# Default mode
def default_mode():
    if not is_muted:
        try:
            mixer.music.load("openingTheme.mp3")
            mixer.music.play(-1)
        except Exception:
            pass
    default_mode_text("Normal Mode")
    pygame.display.update()

# Gadhulacha Paani Mode
def gadhulacha_mode():
    if not is_muted:
        try:
            mixer.music.load("kallulache_pani.mp3")
            mixer.music.play(-1)
        except Exception:
            pass
    gadhulacha_text("Gadhulacha Paani!")
    pygame.display.update()

# Shantabai Mode
def shantabai_mode():
    if not is_muted:
        try:
            mixer.music.load("shantabai.mp3")
            mixer.music.play(-1)
        except Exception:
            pass
    shantabai_text("Shantabai!")
    pygame.display.update()

# Shiti vajali gadi sutali Mode
def shiti_mode():
    if not is_muted:
        mixer.music.load("shiti.mp3")
        mixer.music.play(-1)
    shiti_text("Shiti vajali!")
    pygame.display.update()

# Astronomia Mode
def astronomia_mode():
    if not is_muted:
        mixer.music.load("Coffin dance.mp3")
        mixer.music.play(-1)
    shiti_text("Astronomia!")
    pygame.display.update()

# Title and icon
pygame.display.set_caption("Meme Invaders")
icon = pygame.image.load("logo.png")
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load("ship.png")
playerX = 370
playerY = 480
playerXchange = 0

# Enemy Setup
enemyImg = []
enemyX = []
enemyY = []
enemyXchange = []
enemyYchange = []
num_of_enemies = 6

def init_enemies():
    global enemyImg, enemyX, enemyY, enemyXchange, enemyYchange
    enemyImg = []
    enemyX = []
    enemyY = []
    enemyXchange = []
    enemyYchange = []
    try:
        v_img = pygame.transform.scale(pygame.image.load("vadapav.png"), (64, 64))
        m_img = pygame.transform.scale(pygame.image.load("momos.png"), (64, 64))
    except Exception:
        v_img = pygame.transform.scale(pygame.image.load("vadapav.png"), (64, 64))
        m_img = v_img

    for i in range(num_of_enemies):
        img = v_img if (i % 2 == 0) else m_img
        enemyImg.append(img)
        enemyX.append(random.randint(0, 736))
        enemyY.append(random.randint(50, 150))
        enemyXchange.append(1)
        enemyYchange.append(40)

init_enemies()

# Boss Vadapav Setup
raw_vadapav = pygame.image.load("vadapav.png")
bossImg = pygame.transform.scale(raw_vadapav, (150, 150))
boss_active = False
boss_hp = 20
boss_max_hp = 20
bossX = 325.0
bossY = 60.0
bossXchange = 1.0
last_boss_wave = 0
boss_attack_timer = 0
boss_secondary_timer = 0
boss_projectiles = []

# Bullets System
bulletImg = pygame.image.load("bullet.png")
bullets = []  # List of active dicts: {'x': float, 'y': float, 'dx': float}
bulletYchange = 5

# Power-ups & Timers
triple_shot_timer = 0
shield_timer = 0
laser_timer = 0
speed_timer = 0

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(["triple", "shield", "nuke", "laser", "speed", "life"])
        self.speed = 2.0
        self.active = True

    def update(self):
        self.y += self.speed
        if self.y > 600:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return
        colors = {
            "triple": (255, 215, 0),
            "shield": (0, 200, 255),
            "nuke": (255, 60, 60),
            "laser": (255, 0, 255),
            "speed": (50, 255, 50),
            "life": (255, 105, 180)
        }
        labels = {
            "triple": "3X",
            "shield": "SHD",
            "nuke": "BOMB",
            "laser": "BEAM",
            "speed": "SPD",
            "life": "+1 HP"
        }
        rect = pygame.Rect(self.x, self.y, 68, 32)
        pygame.draw.rect(surface, colors[self.type], rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), rect, width=3, border_radius=8)
        
        p_font = pygame.font.Font("freesansbold.ttf", 14)
        p_text = p_font.render(labels[self.type], True, (0, 0, 0))
        surface.blit(p_text, p_text.get_rect(center=rect.center))

powerups = []

# Particles System
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3.5, 3.5)
        self.vy = random.uniform(-3.5, 3.5)
        self.radius = random.randint(3, 7)
        self.color = random.choice([(255, 215, 0), (255, 80, 0), (0, 255, 120), (255, 255, 255)])
        self.lifetime = random.randint(15, 30)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.radius = max(0, self.radius - 0.18)
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0 and self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

particles = []

def create_explosion(x, y):
    for _ in range(20):
        particles.append(Particle(x, y))

def reset_game():
    global score_value, lives, playerX, playerY, playerXchange, bullets, powerups, particles
    global triple_shot_timer, shield_timer, laser_timer, speed_timer, game_state, high_score, high_scores_list
    global boss_active, boss_hp, boss_max_hp, bossX, bossY, last_boss_wave
    global boss_projectiles, boss_attack_timer, boss_secondary_timer
    score_value = 0
    lives = 3
    playerX = 370
    playerY = 480
    playerXchange = 0
    bullets = []
    powerups = []
    particles = []
    triple_shot_timer = 0
    shield_timer = 0
    laser_timer = 0
    speed_timer = 0
    boss_active = False
    boss_hp = 20
    boss_max_hp = 20
    bossX = 325.0
    bossY = 60.0
    bossXchange = 1.0
    last_boss_wave = 0
    boss_projectiles = []
    boss_attack_timer = 0
    boss_secondary_timer = 0
    high_scores_list = load_high_scores()
    high_score = high_scores_list[0]["score"] if high_scores_list else 0
    init_enemies()
    game_state = "PLAYING"

def draw_button(text, x, y, width, height, normal_color, hover_color, text_color, font_size=28):
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, width, height)
    is_hover = rect.collidepoint(mouse_pos)
    
    color = hover_color if is_hover else normal_color
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, (255, 255, 255), rect, width=2, border_radius=12)
    
    btn_font = pygame.font.Font("freesansbold.ttf", font_size)
    btn_text = btn_font.render(text, True, text_color)
    text_rect = btn_text.get_rect(center=rect.center)
    screen.blit(btn_text, text_rect)
    
    return rect

def draw_heart(surface, x, y, size=16, color=(255, 60, 80)):
    pygame.draw.circle(surface, color, (int(x - size // 4), int(y - size // 4)), size // 3)
    pygame.draw.circle(surface, color, (int(x + size // 4), int(y - size // 4)), size // 3)
    points = [
        (int(x - size // 2 + 1), int(y - size // 6)),
        (int(x + size // 2 - 1), int(y - size // 6)),
        (int(x), int(y + size // 2))
    ]
    pygame.draw.polygon(surface, color, points)

def show_hud():
    # Score
    score_text = font.render("Score: " + str(score_value), True, (0, 255, 0))
    screen.blit(score_text, (10, 10))
    
    # High Score
    hs_text = font.render("High Score: " + str(high_score), True, (255, 215, 0))
    screen.blit(hs_text, (10, 35))

    # Lives
    lives_text = font.render("Lives:", True, (255, 80, 80))
    screen.blit(lives_text, (200, 10))
    for i in range(lives):
        draw_heart(screen, 275 + i * 22, 22, size=16)

    # Wave / Level
    wave = 1 + (score_value // 5)
    wave_text = font.render("Wave: " + str(wave), True, (0, 220, 255))
    screen.blit(wave_text, (200, 35))

    # Active Power-up indicators
    active_y = 10
    if triple_shot_timer > 0:
        t_text = font.render("[3X] TRIPLE SHOT", True, (255, 215, 0))
        screen.blit(t_text, (420, active_y))
        active_y += 22
    if shield_timer > 0:
        s_text = font.render("[SHIELD] ACTIVE", True, (0, 200, 255))
        screen.blit(s_text, (420, active_y))
        active_y += 22
    if laser_timer > 0:
        l_text = font.render("[BEAM] MEGA LASER", True, (255, 0, 255))
        screen.blit(l_text, (420, active_y))
        active_y += 22
    if speed_timer > 0:
        sp_text = font.render("[SPD] SPEED BOOST", True, (50, 255, 50))
        screen.blit(sp_text, (420, active_y))
        active_y += 22

def draw_boss_health_bar(hp, max_hp):
    bar_width = 320
    bar_height = 22
    x = 240
    y = 12
    pct = max(0, hp) / max_hp
    pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height), border_radius=6)
    pygame.draw.rect(screen, (255, 40, 40), (x, y, int(bar_width * pct), bar_height), border_radius=6)
    pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), width=2, border_radius=6)
    
    hp_text = font.render(f"MINIBOSS VADAPAV: {hp}/{max_hp} HP", True, (255, 255, 255))
    screen.blit(hp_text, (x + 30, y + 25))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 50, 50))
    screen.blit(over_text, (200, 150))
    
    final_score = font.render("Final Score: " + str(score_value), True, (255, 255, 255))
    screen.blit(final_score, (330, 235))

    hs_display = font.render("High Score: " + str(high_score), True, (255, 215, 0))
    screen.blit(hs_display, (330, 270))

def gadhulacha_text(textentry):
    over_text = over_font.render(textentry, True, (150, 255, 100))
    screen.blit(over_text, (100, 250))

def shantabai_text(textentry):
    over_text = over_font.render(textentry, True, (150, 255, 100))
    screen.blit(over_text, (230, 250))

def shiti_text(textentry):
    over_text = over_font.render(textentry, True, (150, 255, 100))
    screen.blit(over_text, (220, 250))

def default_mode_text(textentry):
    over_text = over_font.render(textentry, True, (150, 255, 100))
    screen.blit(over_text, (190, 250))

def player(x, y):
    screen.blit(playerImg, (x, y))
    if shield_timer > 0:
        pygame.draw.circle(screen, (0, 220, 255), (int(x + 32), int(y + 32)), 38, width=3)

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((math.pow(enemyX - bulletX, 2)) + (math.pow(enemyY - bulletY, 2)))
    return distance < 27

# Game Loop
running = True
while running:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    start_btn_rect = None
    hs_btn_rect = None
    ctrl_btn_rect = None
    replay_btn_rect = None
    back_btn_rect = None
    submit_btn_rect = None
    mute_btn_rect = None

    # Always render Mute Button at top-right
    mute_text = "MUSIC: OFF" if is_muted else "MUSIC: ON"
    mute_color = (150, 50, 50) if is_muted else (0, 150, 80)
    mute_hover = (200, 70, 70) if is_muted else (0, 200, 100)
    mute_btn_rect = draw_button(mute_text, 660, 10, 130, 35, mute_color, mute_hover, (255, 255, 255), font_size=14)

    if game_state == "START":
        title_surface = title_font.render("MEME INVADERS", True, (0, 255, 0))
        screen.blit(title_surface, (190, 100))

        sub_surface = control_info_font.render("Save the world from Vadapavs & Miniboss Vadapav!", True, (255, 255, 255))
        screen.blit(sub_surface, (200, 170))

        hs_start = font.render("All-Time High Score: " + str(high_score), True, (255, 215, 0))
        screen.blit(hs_start, (270, 205))

        start_btn_rect = draw_button("START GAME", 280, 250, 240, 50, (0, 180, 0), (0, 230, 0), (255, 255, 255), font_size=22)
        hs_btn_rect = draw_button("HIGH SCORES", 280, 315, 240, 50, (200, 150, 0), (250, 190, 0), (255, 255, 255), font_size=22)
        ctrl_btn_rect = draw_button("CONTROLS & HELP", 280, 380, 240, 50, (0, 140, 200), (0, 180, 240), (255, 255, 255), font_size=22)

    elif game_state == "CONTROLS":
        c_title = title_font.render("CONTROLS & HELP", True, (0, 220, 255))
        screen.blit(c_title, (165, 55))

        panel = pygame.Rect(90, 130, 620, 350)
        pygame.draw.rect(screen, (15, 20, 35), panel, border_radius=15)
        pygame.draw.rect(screen, (0, 220, 255), panel, width=2, border_radius=15)

        lines = [
            ("MOVEMENT", "LEFT / RIGHT Arrow Keys"),
            ("SHOOT", "SPACEBAR"),
            ("MODES", "F1: Gadhulacha | F2: Shantabai"),
            ("      ", "F3: Shiti Vajali  | F4: Astronomia"),
            ("      ", "F12: Default Normal Mode"),
            ("POWER-UPS", "[3X] Triple | [SHD] Shield | [BOMB] Nuke"),
            ("         ", "[BEAM] Laser | [SPD] Speed | [+1 HP] Life")
        ]

        for idx, (label, text) in enumerate(lines):
            if label.strip():
                lbl_surf = font.render(f"{label}:", True, (255, 215, 0))
                screen.blit(lbl_surf, (115, 145 + idx * 44))
                val_surf = font.render(text, True, (255, 255, 255))
                screen.blit(val_surf, (270, 145 + idx * 44))
            else:
                val_surf = font.render(text, True, (200, 200, 200))
                screen.blit(val_surf, (270, 145 + idx * 44))

        back_btn_rect = draw_button("BACK", 300, 500, 200, 48, (100, 100, 100), (150, 150, 150), (255, 255, 255), font_size=22)

    elif game_state == "LEADERBOARD":
        lb_title = title_font.render("HIGH SCORES", True, (255, 215, 0))
        screen.blit(lb_title, (230, 100))

        scores = load_high_scores()
        if not scores:
            no_scores = font.render("No High Scores Yet!", True, (200, 200, 200))
            screen.blit(no_scores, (300, 220))
        else:
            for idx, entry in enumerate(scores):
                rank_str = f"#{idx + 1}"
                name_str = entry.get("name", "PLAYER")
                score_str = str(entry.get("score", 0))

                color = (255, 215, 0) if idx == 0 else (220, 220, 220)
                rank_surf = font.render(f"{rank_str:<4} {name_str:<12} {score_str}", True, color)
                screen.blit(rank_surf, (270, 180 + idx * 45))

        back_btn_rect = draw_button("BACK", 300, 430, 200, 50, (100, 100, 100), (150, 150, 150), (255, 255, 255), font_size=24)

    elif game_state == "GAME_OVER_NAME":
        go_title = over_font.render("GAME OVER", True, (255, 50, 50))
        screen.blit(go_title, (200, 120))

        score_disp = font.render(f"Your Score: {score_value}", True, (255, 255, 255))
        screen.blit(score_disp, (330, 210))

        prompt_text = font.render("ENTER YOUR NAME:", True, (255, 215, 0))
        screen.blit(prompt_text, (290, 250))

        # Text input box
        box_rect = pygame.Rect(250, 290, 300, 50)
        pygame.draw.rect(screen, (30, 30, 30), box_rect, border_radius=8)
        pygame.draw.rect(screen, (0, 255, 0), box_rect, width=2, border_radius=8)

        name_surf = font.render(player_name_input + "_", True, (255, 255, 255))
        screen.blit(name_surf, (box_rect.x + 20, box_rect.y + 12))

        submit_btn_rect = draw_button("SUBMIT", 300, 360, 200, 50, (0, 180, 0), (0, 230, 0), (255, 255, 255), font_size=22)

    elif game_state == "GAME_OVER":
        game_over_text()
        replay_btn_rect = draw_button("REPLAY", 280, 320, 240, 50, (0, 180, 0), (0, 230, 0), (255, 255, 255), font_size=22)
        hs_btn_rect = draw_button("HIGH SCORES", 280, 385, 240, 50, (200, 150, 0), (250, 190, 0), (255, 255, 255), font_size=22)

    elif game_state == "PLAYING":
        # Update Timers
        if triple_shot_timer > 0:
            triple_shot_timer -= 1
        if shield_timer > 0:
            shield_timer -= 1
        if laser_timer > 0:
            laser_timer -= 1
        if speed_timer > 0:
            speed_timer -= 1

        # Calculate wave & speed scaling
        wave = 1 + (score_value // 5)
        speed_multiplier = 1.0 + (wave - 1) * 0.08

        # Miniboss Trigger: Wave 10 onwards (every 10 waves)
        if wave >= 10 and (wave // 10 > last_boss_wave // 10) and not boss_active:
            boss_active = True
            boss_hp = 20
            boss_max_hp = 20
            bossX = 325.0
            bossY = 60.0
            bossXchange = 1.0
            last_boss_wave = wave

        # Player Movement
        speed_mult = 2.0 if speed_timer > 0 else 1.0
        playerX += playerXchange * speed_mult
        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        # Update & Render Particles
        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.lifetime <= 0 or p.radius <= 0:
                particles.remove(p)

        # Mega Laser Beam Execution
        if laser_timer > 0:
            beam_x = playerX + 22
            beam_w = 20
            pygame.draw.rect(screen, (255, 0, 255), (beam_x, 0, beam_w, playerY))
            pygame.draw.rect(screen, (255, 255, 255), (beam_x + 6, 0, 8, playerY))
            for _ in range(3):
                particles.append(Particle(playerX + 32 + random.randint(-10, 10), random.randint(0, int(playerY))))

            # Laser hit regular enemies
            if not boss_active:
                for i in range(num_of_enemies):
                    if (beam_x - 20) <= enemyX[i] <= (beam_x + beam_w):
                        create_explosion(enemyX[i] + 32, enemyY[i] + 32)
                        score_value += 1
                        if random.random() < 0.15:
                            powerups.append(PowerUp(enemyX[i] + 16, enemyY[i] + 16))
                        enemyX[i] = random.randint(0, 736)
                        enemyY[i] = random.randint(50, 150)

            # Laser hit Boss Vadapav
            if boss_active and bossX <= (playerX + 32) <= (bossX + 150):
                boss_hp -= 0.15
                create_explosion(playerX + 32, bossY + 75)
                if boss_hp <= 0:
                    boss_active = False
                    boss_projectiles = []
                    score_value += 15
                    for _ in range(6):
                        create_explosion(bossX + random.randint(10, 140), bossY + random.randint(10, 140))

        # Update & Render Power-ups
        for pu in powerups[:]:
            pu.update()
            pu.draw(screen)
            if pu.active and math.sqrt((pu.x + 34 - (playerX + 32))**2 + (pu.y + 16 - (playerY + 32))**2) < 55:
                pu.active = False
                if pu.type == "triple":
                    triple_shot_timer = 450
                elif pu.type == "shield":
                    shield_timer = 450
                elif pu.type == "laser":
                    laser_timer = 350
                elif pu.type == "speed":
                    speed_timer = 450
                elif pu.type == "life":
                    lives = min(5, lives + 1)
                    if not is_muted:
                        try:
                            mixer.Sound("laser.wav").play()
                        except Exception:
                            pass
                elif pu.type == "nuke":
                    if boss_active:
                        boss_hp = max(0, boss_hp - 15)
                        create_explosion(bossX + 75, bossY + 75)
                    else:
                        for j in range(num_of_enemies):
                            create_explosion(enemyX[j] + 32, enemyY[j] + 32)
                            score_value += 1
                            enemyX[j] = random.randint(0, 736)
                            enemyY[j] = random.randint(50, 150)
                    if not is_muted:
                        try:
                            mixer.Sound("explosion.wav").play()
                        except Exception:
                            pass
            if not pu.active:
                powerups.remove(pu)

        # BOSS VADAPAV LOGIC (Strictly active alone when boss_active is True)
        if boss_active:
            bossX += bossXchange
            if bossX <= 0 or bossX >= 650:
                bossXchange = -bossXchange

            screen.blit(bossImg, (int(bossX), int(bossY)))
            draw_boss_health_bar(boss_hp, boss_max_hp)

            # Primary Attack: Aimed Red Chili Missile (~every 2.7s)
            boss_attack_timer += 1
            if boss_attack_timer >= 160:
                boss_attack_timer = 0
                dx = (playerX + 32) - (bossX + 75)
                dy = (playerY + 32) - (bossY + 140)
                dist = max(1.0, math.sqrt(dx * dx + dy * dy))
                speed = 2.4
                vx = (dx / dist) * speed
                vy = (dy / dist) * speed
                boss_projectiles.append({
                    'x': bossX + 75,
                    'y': bossY + 140,
                    'vx': vx,
                    'vy': vy,
                    'type': 'primary',
                    'color': (255, 50, 30),
                    'radius': 7
                })
                if not is_muted:
                    try:
                        mixer.Sound("laser.wav").play()
                    except Exception:
                        pass

            # Secondary Attack: 3-Way Spicy Chutney Spread Burst (~every 6.3s)
            boss_secondary_timer += 1
            if boss_secondary_timer >= 380:
                boss_secondary_timer = 0
                for vx in [-1.5, 0.0, 1.5]:
                    boss_projectiles.append({
                        'x': bossX + 75,
                        'y': bossY + 140,
                        'vx': vx,
                        'vy': 2.2,
                        'type': 'secondary',
                        'color': (50, 230, 80),
                        'radius': 8
                    })

            # Bullet collision with Boss
            for b in bullets[:]:
                if bossX <= (b['x'] + 16) <= (bossX + 150) and bossY <= (b['y'] + 10) <= (bossY + 150):
                    boss_hp -= 1
                    create_explosion(b['x'] + 16, b['y'] + 10)
                    if b in bullets:
                        bullets.remove(b)
                    if not is_muted:
                        try:
                            mixer.Sound("explosion.wav").play()
                        except Exception:
                            pass

                    if boss_hp <= 0:
                        boss_active = False
                        boss_projectiles = []
                        score_value += 20  # Miniboss defeat bonus!
                        powerups.append(PowerUp(bossX + 40, bossY + 80))
                        powerups.append(PowerUp(bossX + 90, bossY + 80))
                        for _ in range(8):
                            create_explosion(bossX + random.randint(10, 140), bossY + random.randint(10, 140))
                        break

            # Update & Render Boss Projectiles
            for bp in boss_projectiles[:]:
                bp['x'] += bp['vx']
                bp['y'] += bp['vy']

                px, py = int(bp['x']), int(bp['y'])
                r = bp['radius']
                pygame.draw.circle(screen, bp['color'], (px, py), r)
                pygame.draw.circle(screen, (255, 255, 255), (px, py), r, width=2)

                if random.random() < 0.5:
                    particles.append(Particle(px, py))

                if bp['y'] > 620 or bp['x'] < -30 or bp['x'] > 830:
                    if bp in boss_projectiles:
                        boss_projectiles.remove(bp)
                    continue

                # Collision check with player ship
                p_center_x = playerX + 32
                p_center_y = playerY + 32
                hit_dist = math.sqrt((bp['x'] - p_center_x)**2 + (bp['y'] - p_center_y)**2)
                if hit_dist < (r + 18):
                    create_explosion(p_center_x, p_center_y)
                    if bp in boss_projectiles:
                        boss_projectiles.remove(bp)
                    
                    if shield_timer > 0:
                        shield_timer = max(0, shield_timer - 100)
                    else:
                        lives -= 1
                        if not is_muted:
                            try:
                                mixer.Sound("explosion.wav").play()
                            except Exception:
                                pass
                        if lives <= 0:
                            player_name_input = ""
                            game_state = "GAME_OVER_NAME"
                            break

        else:
            # REGULAR ENEMIES LOGIC (Renders ONLY when Boss is NOT active!)
            for i in range(num_of_enemies):
                if enemyY[i] > 440:
                    create_explosion(enemyX[i] + 32, enemyY[i] + 32)
                    if not is_muted:
                        try:
                            mixer.Sound("explosion.wav").play()
                        except Exception:
                            pass
                    
                    if shield_timer > 0:
                        shield_timer = 0
                    else:
                        lives -= 1
                    
                    enemyX[i] = random.randint(0, 736)
                    enemyY[i] = random.randint(50, 150)

                    if lives <= 0:
                        player_name_input = ""
                        game_state = "GAME_OVER_NAME"
                        break

                enemyX[i] += enemyXchange[i] * speed_multiplier
                if enemyX[i] <= 0:
                    enemyXchange[i] = 0.8
                    enemyY[i] += enemyYchange[i]
                elif enemyX[i] >= 736:
                    enemyXchange[i] = -0.8
                    enemyY[i] += enemyYchange[i]

                # Bullet collision with regular enemy
                for b in bullets[:]:
                    if isCollision(enemyX[i], enemyY[i], b['x'], b['y']):
                        create_explosion(enemyX[i] + 32, enemyY[i] + 32)
                        if not is_muted:
                            try:
                                mixer.Sound("explosion.wav").play()
                            except Exception:
                                pass
                        
                        if b in bullets:
                            bullets.remove(b)
                        
                        score_value += 1

                        if random.random() < 0.18:
                            powerups.append(PowerUp(enemyX[i] + 16, enemyY[i] + 16))

                        enemyX[i] = random.randint(0, 736)
                        enemyY[i] = random.randint(50, 150)

                enemy(enemyX[i], enemyY[i], i)

        # Bullets Movement & Render
        for b in bullets[:]:
            b['y'] -= bulletYchange
            b['x'] += b['dx']
            screen.blit(bulletImg, (b['x'] + 16, b['y'] + 10))
            if b['y'] <= 0 or b['x'] < 0 or b['x'] > 800:
                bullets.remove(b)

        player(playerX, playerY)
        show_hud()

    # Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if mute_btn_rect and mute_btn_rect.collidepoint(event.pos):
                is_muted = not is_muted
                mixer.music.set_volume(0.0 if is_muted else 1.0)

            if game_state == "START":
                if start_btn_rect and start_btn_rect.collidepoint(event.pos):
                    reset_game()
                elif hs_btn_rect and hs_btn_rect.collidepoint(event.pos):
                    game_state = "LEADERBOARD"
                elif ctrl_btn_rect and ctrl_btn_rect.collidepoint(event.pos):
                    game_state = "CONTROLS"

            elif game_state in ["LEADERBOARD", "CONTROLS"] and back_btn_rect and back_btn_rect.collidepoint(event.pos):
                game_state = "START"

            elif game_state == "GAME_OVER_NAME" and submit_btn_rect and submit_btn_rect.collidepoint(event.pos):
                add_high_score(player_name_input, score_value)
                high_scores_list = load_high_scores()
                high_score = high_scores_list[0]["score"] if high_scores_list else 0
                game_state = "GAME_OVER"

            elif game_state == "GAME_OVER":
                if replay_btn_rect and replay_btn_rect.collidepoint(event.pos):
                    reset_game()
                elif hs_btn_rect and hs_btn_rect.collidepoint(event.pos):
                    game_state = "LEADERBOARD"

        if event.type == pygame.KEYDOWN:
            if game_state == "GAME_OVER_NAME":
                if event.key == pygame.K_RETURN:
                    add_high_score(player_name_input, score_value)
                    high_scores_list = load_high_scores()
                    high_score = high_scores_list[0]["score"] if high_scores_list else 0
                    game_state = "GAME_OVER"
                elif event.key == pygame.K_BACKSPACE:
                    player_name_input = player_name_input[:-1]
                else:
                    if len(player_name_input) < 10 and (event.unicode.isalnum() or event.unicode == ' '):
                        player_name_input += event.unicode.upper()

            elif game_state == "START":
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    reset_game()

            elif game_state == "GAME_OVER":
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    reset_game()

            elif game_state in ["LEADERBOARD", "CONTROLS"]:
                if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
                    game_state = "START"

            if game_state == "PLAYING":
                if event.key == pygame.K_LEFT:
                    playerXchange = -4
                if event.key == pygame.K_RIGHT:
                    playerXchange = 4
                if event.key == pygame.K_SPACE:
                    if not is_muted:
                        try:
                            mixer.Sound("laser.wav").play()
                        except Exception:
                            pass
                    
                    if triple_shot_timer > 0:
                        bullets.append({'x': playerX, 'y': playerY, 'dx': 0})
                        bullets.append({'x': playerX - 15, 'y': playerY, 'dx': -1.2})
                        bullets.append({'x': playerX + 15, 'y': playerY, 'dx': 1.2})
                    else:
                        bullets.append({'x': playerX, 'y': playerY, 'dx': 0})

            # Theme shortcut keys
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
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                playerXchange = 0

    pygame.display.update()
