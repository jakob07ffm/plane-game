import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Plane Game")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
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
MAX_HEALTH = 3
POWERUP_CHANCE = 0.02

font = pygame.font.SysFont('comicsans', 30)
title_font = pygame.font.SysFont('comicsans', 60)

plane = pygame.Rect(WIDTH // 2 - PLANE_WIDTH // 2, HEIGHT - PLANE_HEIGHT - 10, PLANE_WIDTH, PLANE_HEIGHT)
bullets = []
enemies = []
powerups = []
boss = None

score = 0
health = MAX_HEALTH
background_y = 0
level = 1
game_active = False

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
    
    draw_text(f"Score: {score}", font, WHITE, 10, 10)
    draw_text(f"Health: {health}", font, WHITE, WIDTH - 130, 10)
    draw_text(f"Level: {level}", font, WHITE, WIDTH // 2 - 50, 10)

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
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 1
                break

def handle_enemies():
    global health, boss
    while len(enemies) < MAX_ENEMIES and not boss:
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
    global health
    for powerup in powerups[:]:
        powerup.y += ENEMY_VEL
        if powerup.colliderect(plane):
            powerups.remove(powerup)
            if health < MAX_HEALTH:
                health += 1
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
    global boss
    if boss is None and score >= level * 10:
        boss = pygame.Rect(WIDTH // 2 - ENEMY_WIDTH, -ENEMY_HEIGHT * 2, ENEMY_WIDTH * 2, ENEMY_HEIGHT * 2)
        
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

def title_screen():
    WIN.fill(BLUE)
    draw_text("Plane Game", title_font, WHITE, WIDTH // 2 - 150, HEIGHT // 2 - 100)
    draw_text("Press Enter to Start", font, WHITE, WIDTH // 2 - 120, HEIGHT // 2)
    pygame.display.update()
    wait_for_key()

def wait_for_key():
    global game_active, level, health, score
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
                bullet = pygame.Rect(plane.x + PLANE_WIDTH // 2 - BULLET_WIDTH // 2, plane.y, BULLET_WIDTH, BULLET_HEIGHT)
                bullets.append(bullet)

    keys = pygame.key.get_pressed()
    handle_movement(keys)
    handle_bullets()
    handle_enemies()
    handle_boss()
    if random.random() < POWERUP_CHANCE:
        powerup = pygame.Rect(random.randint(0, WIDTH - POWERUP_SIZE), random.randint(-500, -50), POWERUP_SIZE, POWERUP_SIZE)
        powerups.append(powerup)
    handle_powerups()
    boss_fight()
    draw_window()

pygame.quit()
