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
FPS = 60
PLANE_WIDTH, PLANE_HEIGHT = 60, 40
ENEMY_WIDTH, ENEMY_HEIGHT = 50, 30
BULLET_WIDTH, BULLET_HEIGHT = 5, 10
POWERUP_SIZE = 20
VEL = 5
BULLET_VEL = 7
ENEMY_VEL = 2
MAX_ENEMIES = 7
MAX_HEALTH = 3
POWERUP_CHANCE = 0.01

font = pygame.font.SysFont('comicsans', 30)

plane = pygame.Rect(WIDTH // 2 - PLANE_WIDTH // 2, HEIGHT - PLANE_HEIGHT - 10, PLANE_WIDTH, PLANE_HEIGHT)
bullets = []
enemies = []
powerups = []

score = 0
health = MAX_HEALTH
background_y = 0

def draw_window():
    WIN.fill(BLUE)
    WIN.blit(pygame.transform.scale(pygame.image.load("background.jpg"), (WIDTH, HEIGHT)), (0, background_y))
    WIN.blit(pygame.transform.scale(pygame.image.load("background.jpg"), (WIDTH, HEIGHT)), (0, background_y - HEIGHT))
    
    pygame.draw.rect(WIN, RED, plane)
    for bullet in bullets:
        pygame.draw.rect(WIN, WHITE, bullet)
    for enemy in enemies:
        pygame.draw.rect(WIN, YELLOW if enemy.width > 50 else WHITE, enemy)
    for powerup in powerups:
        pygame.draw.rect(WIN, GREEN, powerup)

    score_text = font.render(f"Score: {score}", True, WHITE)
    WIN.blit(score_text, (10, 10))
    
    health_text = font.render(f"Health: {health}", True, WHITE)
    WIN.blit(health_text, (WIDTH - 130, 10))

    pygame.display.update()

def handle_bullets():
    global score
    for bullet in bullets[:]:
        bullet.y -= BULLET_VEL
        if bullet.y < 0:
            bullets.remove(bullet)
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 1
                break

def handle_enemies():
    global health
    while len(enemies) < MAX_ENEMIES:
        size = random.randint(40, 80)
        enemy = pygame.Rect(random.randint(0, WIDTH - size), random.randint(-1000, -100), size, ENEMY_HEIGHT)
        enemies.append(enemy)
    for enemy in enemies[:]:
        enemy.y += ENEMY_VEL + (80 - enemy.width) // 10
        if enemy.y > HEIGHT:
            enemies.remove(enemy)
            health -= 1
            if health <= 0:
                pygame.quit()
                return
        if enemy.colliderect(plane):
            enemies.remove(enemy)
            health -= 1
            if health <= 0:
                pygame.quit()
                return

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

clock = pygame.time.Clock()
run = True

while run:
    clock.tick(FPS)
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
    if random.random() < POWERUP_CHANCE:
        powerup = pygame.Rect(random.randint(0, WIDTH - POWERUP_SIZE), random.randint(-500, -50), POWERUP_SIZE, POWERUP_SIZE)
        powerups.append(powerup)
    handle_powerups()
    draw_window()

pygame.quit()
