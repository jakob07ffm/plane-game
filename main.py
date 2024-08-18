import pygame
import random
import json

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
GRAY = (169, 169, 169)
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
GOLD_COIN_VALUE = 10
GEM_VALUE = 50
SHOP_ITEMS = {
    "Health": 100,
    "Spread Shot": 200,
    "Laser": 300,
    "Shield": 150,
    "Bomb": 250,
    "Plane Color": 100,
    "Weapon Upgrade": 500,
    "Special Ability": 750
}
ACHIEVEMENTS = {"First Blood": 10, "Survivor": 50, "Boss Slayer": 100}

font = pygame.font.SysFont('comicsans', 30)
title_font = pygame.font.SysFont('comicsans', 60)

plane = pygame.Rect(WIDTH // 2 - PLANE_WIDTH // 2, HEIGHT - PLANE_HEIGHT - 10, PLANE_WIDTH, PLANE_HEIGHT)
bullets = []
enemies = []
powerups = []
boss = None
mini_boss = None
hazards = []

score = 0
health = MAX_HEALTH
background_y = 0
level = 1
game_active = False
current_weapon = "Normal"
special_ability = None
coins = 0
gems = 0
store_open = False
achievements_unlocked = set()
day_night_cycle = 0  # 0: Day, 1: Night
weather_effects = None
player_color = BLUE
plane_speed_upgrade = 0
weapon_power_upgrade = 0
special_ability = None
ranking = "Novice"

def draw_text(text, font, color, x, y):
    render = font.render(text, True, color)
    WIN.blit(render, (x, y))

def draw_window():
    global day_night_cycle
    WIN.fill(BLUE if day_night_cycle == 0 else GRAY)
    pygame.draw.rect(WIN, player_color, plane)
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
    for hazard in hazards:
        pygame.draw.rect(WIN, GRAY, hazard)
    
    draw_text(f"Score: {score}", font, WHITE, 10, 10)
    draw_text(f"Health: {health}", font, WHITE, WIDTH - 130, 10)
    draw_text(f"Level: {level}", font, WHITE, WIDTH // 2 - 50, 10)
    draw_text(f"Coins: {coins}", font, WHITE, WIDTH // 2 - 50, 50)
    draw_text(f"Gems: {gems}", font, WHITE, WIDTH // 2 - 50, 90)
    draw_text(f"Rank: {ranking}", font, WHITE, WIDTH // 2 - 50, 130)

    pygame.display.update()

def handle_bullets():
    global score
    for bullet in bullets[:]:
        bullet.y -= BULLET_VEL + weapon_power_upgrade
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
                coins += random.randint(1, 3) * GOLD_COIN_VALUE
                gems += random.randint(0, 1) * GEM_VALUE
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
    speed = VEL + plane_speed_upgrade
    if keys[pygame.K_LEFT] and plane.x - speed > 0:
        plane.x -= speed
    if keys[pygame.K_RIGHT] and plane.x + speed + PLANE_WIDTH < WIDTH:
        plane.x += speed
    if keys[pygame.K_UP] and plane.y - speed > 0:
        plane.y -= speed
    if keys[pygame.K_DOWN] and plane.y + speed + PLANE_HEIGHT < HEIGHT:
        plane.y += speed

def game_over():
    global game_active
    draw_text(f"Game Over! Final Score: {score}", title_font, RED, WIDTH // 2 - 250, HEIGHT // 2 - 50)
    pygame.display.update()
    pygame.time.delay(3000)
    game_active = False
    save_game()

def boss_fight():
    global boss, mini_boss
    if boss is None and score >= level * 20:
        boss = pygame.Rect(WIDTH // 2 - ENEMY_WIDTH, -ENEMY_HEIGHT * 2, ENEMY_WIDTH * 2, ENEMY_HEIGHT * 2)
    if mini_boss is None and score >= level * 10 and score < level * 20:
        mini_boss = pygame.Rect(WIDTH // 2 - ENEMY_WIDTH // 2, -ENEMY_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT)
    if boss:
        boss.y += BOSS_VEL
        if boss.y >= HEIGHT:
            boss.y = -ENEMY_HEIGHT * 2
        if boss.colliderect(plane):
            health -= 2
            if health <= 0:
                game_over()
    if mini_boss:
        mini_boss.y += BOSS_VEL
        if mini_boss.y >= HEIGHT:
            mini_boss.y = -ENEMY_HEIGHT
        if mini_boss.colliderect(plane):
            health -= 1
            if health <= 0:
                game_over()

def title_screen():
    global game_active
    WIN.fill(BLUE)
    draw_text("Ultimate Plane Game", title_font, WHITE, WIDTH // 2 - 250, HEIGHT // 2 - 50)
    draw_text("Press Enter to Start", font, WHITE, WIDTH // 2 - 150, HEIGHT // 2 + 50)
    pygame.display.update()
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

def open_shop():
    global store_open, current_weapon, special_ability, coins, gems, player_color, plane_speed_upgrade, weapon_power_upgrade
    WIN.fill(BLUE)
    draw_text("Shop", title_font, WHITE, WIDTH // 2 - 100, HEIGHT // 2 - 200)
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
                elif event.key == pygame.K_1 and coins >= 100:
                    health = MAX_HEALTH
                    coins -= 100
                elif event.key == pygame.K_2 and coins >= 200:
                    current_weapon = "Spread Shot"
                    coins -= 200
                elif event.key == pygame.K_3 and coins >= 300:
                    current_weapon = "Laser"
                    coins -= 300
                elif event.key == pygame.K_4 and coins >= 150:
                    special_ability = "Shield"
                    coins -= 150
                elif event.key == pygame.K_5 and coins >= 250:
                    special_ability = "Bomb"
                    coins -= 250
                elif event.key == pygame.K_6 and coins >= 100:
                    player_color = random.choice([BLUE, GREEN, RED, YELLOW, ORANGE, PURPLE])
                    coins -= 100
                elif event.key == pygame.K_7 and coins >= 500:
                    weapon_power_upgrade += 1
                    coins -= 500
                elif event.key == pygame.K_8 and gems >= 750:
                    special_ability = "Hyper Beam"
                    gems -= 750

def check_achievements():
    global ranking
    for achievement, threshold in ACHIEVEMENTS.items():
        if score >= threshold and achievement not in achievements_unlocked:
            achievements_unlocked.add(achievement)
            coins += 20
            draw_text(f"Achievement Unlocked: {achievement}", font, YELLOW, WIDTH // 2 - 200, HEIGHT // 2)
            pygame.display.update()
            pygame.time.delay(1000)
    if score >= 100:
        ranking = "Ace Pilot"

def save_game():
    save_data = {
        "score": score,
        "health": health,
        "level": level,
        "coins": coins,
        "gems": gems,
        "achievements_unlocked": list(achievements_unlocked),
        "player_color": player_color,
        "plane_speed_upgrade": plane_speed_upgrade,
        "weapon_power_upgrade": weapon_power_upgrade,
        "special_ability": special_ability,
        "ranking": ranking
    }
    with open("savegame.json", "w") as save_file:
        json.dump(save_data, save_file)

def load_game():
    global score, health, level, coins, gems, achievements_unlocked, player_color, plane_speed_upgrade, weapon_power_upgrade, special_ability, ranking
    try:
        with open("savegame.json", "r") as save_file:
            save_data = json.load(save_file)
            score = save_data["score"]
            health = save_data["health"]
            level = save_data["level"]
            coins = save_data["coins"]
            gems = save_data["gems"]
            achievements_unlocked = set(save_data["achievements_unlocked"])
            player_color = save_data["player_color"]
            plane_speed_upgrade = save_data["plane_speed_upgrade"]
            weapon_power_upgrade = save_data["weapon_power_upgrade"]
            special_ability = save_data["special_ability"]
            ranking = save_data["ranking"]
    except FileNotFoundError:
        pass

load_game()

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
    
    day_night_cycle = (day_night_cycle + 1) % (FPS * 30)
    
    if random.random() < 0.01:
        weather_effects = "Rain"
    elif random.random() < 0.01:
        weather_effects = "Wind"
    
    if weather_effects == "Rain":
        hazards.append(pygame.Rect(random.randint(0, WIDTH - POWERUP_SIZE), random.randint(-500, -50), POWERUP_SIZE, POWERUP_SIZE))
    if weather_effects == "Wind":
        for bullet in bullets:
            bullet.x += random.choice([-2, 2])
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if current_weapon == "Spread Shot":
                    bullets.append(pygame.Rect(plane.x + PLANE_WIDTH // 2 - BULLET_WIDTH // 2 - 10, plane.y, BULLET_WIDTH, BULLET_HEIGHT))
                    bullets.append(pygame.Rect(plane.x + PLANE_WIDTH // 2 - BULLET_WIDTH // 2 + 10, plane.y, BULLET_WIDTH, BULLET_HEIGHT))
                elif current_weapon == "Laser":
                    bullets.append(pygame.Rect(plane.x + PLANE_WIDTH // 2 - BULLET_WIDTH // 2, plane.y, BULLET_WIDTH * 2, BULLET_HEIGHT))
                else:
                    bullets.append(pygame.Rect(plane.x + PLANE_WIDTH // 2 - BULLET_WIDTH // 2, plane.y, BULLET_WIDTH, BULLET_HEIGHT))
            if event.key == pygame.K_e:
                open_shop()

    keys = pygame.key.get_pressed()
    handle_movement(keys)
    handle_bullets()
    handle_enemies()
    handle_boss()
    boss_fight()
    if random.random() < POWERUP_CHANCE:
        powerup = pygame.Rect(random.randint(0, WIDTH - POWERUP_SIZE), random.randint(-500, -50), POWERUP_SIZE, POWERUP_SIZE)
        powerups.append(powerup)
    handle_powerups()
    check_achievements()
    draw_window()

pygame.quit()
