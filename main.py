import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plane Game")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FPS = 60
PLANE_WIDTH, PLANE_HEIGHT = 60, 40
ENEMY_WIDTH, ENEMY_HEIGHT = 50, 30
BULLET_WIDTH, BULLET_HEIGHT = 5, 10
VEL = 5
BULLET_VEL = 7
ENEMY_VEL = 2
MAX_ENEMIES = 7

plane = pygame.Rect(WIDTH // 2 - PLANE_WIDTH // 2, HEIGHT - PLANE_HEIGHT - 10, PLANE_WIDTH, PLANE_HEIGHT)

bullets = []
enemies = []

def draw_window():
    WIN.fill(BLUE)
    pygame.draw.rect(WIN, RED, plane)
    for bullet in bullets:
        pygame.draw.rect(WIN, WHITE, bullet)
    for enemy in enemies:
        pygame.draw.rect(WIN, WHITE, enemy)
    pygame.display.update()

def handle_bullets():
    for bullet in bullets[:]:
        bullet.y -= BULLET_VEL
        if bullet.y < 0:
            bullets.remove(bullet)
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                break

def handle_enemies():
    while len(enemies) < MAX_ENEMIES:
        enemy = pygame.Rect(random.randint(0, WIDTH - ENEMY_WIDTH), random.randint(-1000, -100), ENEMY_WIDTH, ENEMY_HEIGHT)
        enemies.append(enemy)
    for enemy in enemies[:]:
        enemy.y += ENEMY_VEL
        if enemy.y > HEIGHT:
            enemies.remove(enemy)
        if enemy.colliderect(plane):
            pygame.quit()
            return

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
    draw_window()

pygame.quit()
