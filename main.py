import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Plane Game")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
FPS = 60
PLANE_WIDTH, PLANE_HEIGHT = 60, 40
ENEMY_WIDTH, ENEMY_HEIGHT = 50, 30
BULLET_WIDTH, BULLET_HEIGHT = 5, 10
POWERUP_SIZE = 20
VEL = 5
BULLET_VEL = 7
ENEMY_VEL = 2
BOSS_VEL = 2
MAX_ENEMIES = 7
MAX_HEALTH = 5
POWERUP_CHANCE = 0.03
SHOP_ITEMS = {"Health": 100, "Spread Shot": 200, "Laser": 300, "Shield": 150, "Bomb": 250}

font = pygame.font.SysFont('comicsans', 30)
title_font = pygame.font.SysFont('comicsans', 60)

plane = pygame.Rect(WIDTH // 2 - PLANE_WIDTH // 2, HEIGHT - PLANE_HEIGHT - 10, PLANE_WIDTH, PLANE_HEIGHT)
bullets = []
enemies = []
powerups = []
boss = None
mini_boss = None

score = 0
health = MAX_HEALTH
background_y = 0
level = 1
game_active = False
current_weapon = "Normal"
special_ability = None
coins = 0
store_open = False

def draw_text(text, font, color, x, y):
    render = font.render(text, True, color)
    WIN.blit(render, (x, y))

def draw_window():
    WIN.fill(BLUE)
    pygame.draw.rect(WIN, RED, plane)
    for bullet in bullets:
        pygame.draw.rect(WIN, WHITE, bullet)
    for enemy in enemies:
        pygame.draw.rect(WIN, YELLOW if enemy.width > 50 else WHITE, enemy)
    for powerup in powerups:
        pygame.draw.rect(WIN, GREEN, powerup)
    if boss:
        pygame.draw.rect(WIN, PURPLE, boss)
    if mini_boss:
        pygame.draw.rect(WIN, ORANGE, mini_boss)
    
    draw_text(f"Score: {score}", font, WHITE, 10, 10)
    draw_text(f"Health: {health}", font, WHITE, WIDTH - 130, 10)
    draw_text(f"Level: {level}", font, WHITE, WIDTH // 2 - 50, 10)
    draw_text(f"Coins: {coins}", font, WHITE, WIDTH // 2 - 50, 50)

    pygame.display.update()

def handle_bullets():
    global score
    for bullet in bullets[:]:
        bullet.y -= BULLET_VEL
        if bullet.y < 0:
            bullets.remove(bullet)
        if boss and bullet.colliderect(boss):
            boss.y += BOSS_VEL
            bullets.remove(bullet)
            score += 2
        if mini_boss and bullet.colliderect(mini_boss):
            mini_boss.y += BOSS_VEL
            bullets.remove(bullet)
            score += 1
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 1
                coins += random.randint(1, 3)
                break

def handle_enemies():
    global health, boss, mini_boss
    while len(enemies) < MAX_ENEMIES and not boss and not mini_boss:
        size = random.randint(40, 80)
        enemy = pygame.Rect(random.randint(0, WIDTH - size), random.randint(-1000, -100), size, ENEMY_HEIGHT)
        enemies.append(enemy)
    for enemy in enemies[:]:
        if level % 5 == 0:
            enemy.y += ENEMY_VEL + random.choice([-2, 2])
        else:
            enemy.y += ENEMY_VEL + (80 - enemy.width) // 10
        if enemy.y > HEIGHT:
            enemies.remove(enemy)
            health -= 1
            if health <= 0:
                game_over()
        if enemy.colliderect(plane):
            enemies.remove(enemy)
            health -= 1
            if health <= 0:
                game_over()

def handle_powerups():
    global health, current_weapon, special_ability
    for powerup in powerups[:]:
        powerup.y += ENEMY_VEL
        if powerup.colliderect(plane):
            powerups.remove(powerup)
            if health < MAX_HEALTH:
                health += 1
            elif current_weapon != "Laser":
                current_weapon = "Spread Shot"
            else:
                special_ability = "Shield"
        elif powerup.y > HEIGHT:
            powerups.remove(powerup)

def handle_movement(keys):
    if keys[pygame.K_LEFT] and plane.x - VEL > 0:
        plane.x -= VEL
    if keys[pygame.K_RIGHT] and plane.x + VEL + PLANE_WIDTH < WIDTH:
        plane.x += VEL
    if keys[pygame.K_UP] and plane.y - VEL > 0:
        plane.y -= VEL
    if keys[pygame.K_DOWN] and plane.y + VEL + PLANE_HEIGHT < HEIGHT:
        plane.y += VEL

def game_over():
    global game_active
    draw_text(f"Game Over! Final Score: {score}", title_font, RED, WIDTH // 2 - 250, HEIGHT // 2 - 50)
    pygame.display.update()
    pygame.time.delay(3000)
    game_active = False

def boss_fight():
    global boss, mini_boss
    if boss is None and score >= level * 20:
        boss = pygame.Rect(WIDTH // 2 - ENEMY_WIDTH, -ENEMY_HEIGHT * 2, ENEMY_WIDTH * 2, ENEMY_HEIGHT * 2)
    if mini_boss is None and score >= level * 10 and score < level * 20:
        mini_boss = pygame.Rect(WIDTH // 3 - ENEMY_WIDTH, -ENEMY_HEIGHT * 2, ENEMY_WIDTH, ENEMY_HEIGHT)

def handle_boss():
    global boss, health, level
    if boss:
        boss.y += BOSS_VEL
        if boss.y > HEIGHT:
            health -= 1
            boss = None
            level += 1
        if boss.colliderect(plane):
            health -= 2
            boss = None
            if health <= 0:
                game_over()

def handle_mini_boss():
    global mini_boss, health
    if mini_boss:
        mini_boss.y += BOSS_VEL + 1
        if mini_boss.y > HEIGHT:
            health -= 1
            mini_boss = None
        if mini_boss.colliderect(plane):
            health -= 1
            mini_boss = None
            if health <= 0:
                game_over()

def title_screen():
    WIN.fill(BLUE)
    draw_text("Plane Game", title_font, WHITE, WIDTH // 2 - 150, HEIGHT // 2 - 100)
    draw_text("Press Enter to Start", font, WHITE, WIDTH // 2 - 120, HEIGHT // 2)
    pygame.display.update()
    wait_for_key()

def wait_for_key():
    global game_active, level, health, score, coins, current_weapon, special_ability
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    game_active = True
                    level = 1
                    health = MAX_HEALTH
                    score = 0
                    coins = 0
                    current_weapon = "Normal"
                    special_ability = None

def open_shop():
    global store_open
    WIN.fill(BLUE)
    draw_text("Shop", title_font, WHITE, WIDTH // 2 - 50, HEIGHT // 2 - 200)
    y = 200
    for item, cost in SHOP_ITEMS.items():
        draw_text(f"{item}: {cost} Coins", font, WHITE, WIDTH // 2 - 150, y)
        y += 40
    draw_text("Press S to exit", font, WHITE, WIDTH // 2 - 100, HEIGHT - 50)
    pygame.display.update()
    store_open = True
    while store_open:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    store_open = False

clock = pygame.time.Clock()
run = True

while run:
    clock.tick(FPS)
    
    if not game_active:
        title_screen()
        continue
    
    background_y += 2
    if background_y >= HEIGHT:
        background_y = 0
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if current_weapon == "Spread Shot":
                    bullets.append(pygame.Rect(plane.x + PLANE_WIDTH // 2 - BULLET_WIDTH // 2 - 10, plane.y, BULLET_WIDTH, BULLET_HEIGHT))
                    bullets.append(pygame.Rect(plane.x + PLANE_WIDTH // 2 - BULLET_WIDTH // 2 + 10, plane.y, BULLET_WIDTH, BULLET_HEIGHT))
                else:
                    bullets.append(pygame.Rect(plane.x + PLANE_WIDTH // 2 - BULLET_WIDTH // 2, plane.y, BULLET_WIDTH, BULLET_HEIGHT))
            if event.key == pygame.K_e and coins >= 100:
                open_shop()
                coins -= 100

    keys = pygame.key.get_pressed()
    handle_movement(keys)
    handle_bullets()
    handle_enemies()
    handle_boss()
    handle_mini_boss()
    if random.random() < POWERUP_CHANCE:
        powerup = pygame.Rect(random.randint(0, WIDTH - POWERUP_SIZE), random.randint(-500, -50), POWERUP_SIZE, POWERUP_SIZE)
        powerups.append(powerup)
    handle_powerups()
    boss_fight()
    draw_window()

pygame.quit()
