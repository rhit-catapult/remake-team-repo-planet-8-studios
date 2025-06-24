import pygame
import sys
import random
import math
import os  # 添加os模块用于文件操作
from pygame.locals import *
from enemies import Badguy

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1000
FPS = 60
GRAVITY = 0.8
JUMP_POWER = -16
PLAYER_SPEED = 7
ENEMY_SPEED = 2
BOSS_BULLET_SPEED = 6

# Image dimensions
STAND_HEIGHT = 80
STAND_WIDTH = 56
LR_HEIGHT = 80
LR_WIDTH = 80
RR_HEIGHT = 80
RR_WIDTH = 80
RL_HEIGHT = 80
RL_WIDTH = 80
LL_HEIGHT = 80
LL_WIDTH = 80

# Color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
BLUE = (50, 100, 255)
PURPLE = (180, 70, 255)
YELLOW = (255, 255, 50)
BACKGROUND_COLOR = (10, 5, 30)
PLANET_COLOR = (70, 130, 180)
PLATFORM_COLOR = (120, 80, 40)
UI_BG_COLOR = (20, 10, 40, 200)

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Jedi: Alien Avenger")
clock = pygame.time.Clock()

# Load fonts
font_large = pygame.font.SysFont("arial", 72, bold=True)
font_medium = pygame.font.SysFont("arial", 48)
font_small = pygame.font.SysFont("arial", 36)
font_tiny = pygame.font.SysFont("arial", 24)
font_tinytiny = pygame.font.SysFont("arial", 12)

# 得分文件路径
SCORE_FILE = "high_score.txt"


# 读取最高分
def read_high_score():
    try:
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, 'r') as file:
                return int(file.read().strip())
        return 0
    except:
        return 0


# 保存最高分
def save_high_score(score):
    try:
        with open(SCORE_FILE, 'w') as file:
            file.write(str(score))
        return True
    except:
        return False


# Star particle class
class StarParticle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.uniform(0.5, 2.5)
        self.speed = random.uniform(0.1, 0.5)
        self.brightness = random.randint(100, 255)
        self.twinkle_speed = random.uniform(0.01, 0.05)
        self.twinkle_offset = random.uniform(0, math.pi * 2)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

        # Twinkle effect
        self.brightness = 100 + int(
            155 * abs(math.sin(pygame.time.get_ticks() * self.twinkle_speed + self.twinkle_offset)))

    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))


# Player base class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 40, 60)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.jumping = False
        self.health = 120
        self.max_health = 120
        self.direction = 1  # 1=right, -1=left
        self.attack_cooldown = 0
        self.push_cooldown = 0
        self.score = 0
        self.coins = 0
        self.damage_level = 1
        self.speed_level = 1
        self.platform_group = None
        self.enemy_group = None
        self.boss_group = None
        self.hurt_timer = 0
        self.invulnerable = 0
        self.lightsaber_active = False
        self.lightsaber_timer = 0
        self.character_type = "base"

    def set_groups(self, platform_group, enemy_group, boss_group):  # AI
        self.platform_group = platform_group
        self.enemy_group = enemy_group
        self.boss_group = boss_group

    def update(self):
        keys = pygame.key.get_pressed()

        # Horizontal movement
        self.velocity.x = 0
        if keys[K_a]:  # Move left
            self.velocity.x = -self.speed * self.speed_level
            self.direction = -1
        if keys[K_d]:  # Move right
            self.velocity.x = self.speed * self.speed_level
            self.direction = 1

        # Jump
        if keys[K_w] and not self.jumping:  # Jump
            self.velocity.y = JUMP_POWER
            self.jumping = True
            if pygame.mixer.get_init():
                jump_sound.play()

        # Apply gravity
        self.velocity.y += GRAVITY

        # Update position
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Platform collision detection     # AI
        self.jumping = True
        for platform in self.platform_group:
            if self.rect.colliderect(platform.rect):
                if self.velocity.y > 0 and self.rect.bottom > platform.rect.top and self.rect.bottom < platform.rect.top + 20:
                    self.rect.bottom = platform.rect.top
                    self.velocity.y = 0
                    self.jumping = False

        # Boundary check     # AI
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.jumping = False

        # Update cooldowns         # AI
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.push_cooldown > 0:
            self.push_cooldown -= 1

        # Invulnerability timer     # AI
        if self.invulnerable > 0:
            self.invulnerable -= 1

        # Lightsaber effect timer
        if self.lightsaber_active:
            self.lightsaber_timer -= 1
            if self.lightsaber_timer <= 0:
                self.lightsaber_active = False

        # Attack detection
        if keys[K_SPACE] and self.attack_cooldown == 0:
            self.attack()
            self.attack_cooldown = 20
            self.lightsaber_active = True
            self.lightsaber_timer = 10

        if keys[K_LSHIFT] and self.push_cooldown == 0:
            self.psychic_push()
            self.push_cooldown = 60

        # Take damage from enemies - INCREASED DAMAGE         # AI
        if self.invulnerable == 0:
            for enemy in self.enemy_group:
                if self.rect.colliderect(enemy.rect) and enemy.alive:
                    self.health -= 1.5  # Increased from 0.15 to 1.5
                    self.hurt_timer = 5
                    self.invulnerable = 15
                    if self.health < 0:
                        self.health = 0

        # Hurt effect timer
        if self.hurt_timer > 0:
            self.hurt_timer -= 1

    def attack(self):
        # Create attack area
        attack_rect = pygame.Rect(0, 0, 50, 30)
        if self.direction == 1:  # Attack right
            attack_rect.midleft = self.rect.midright
        else:  # Attack left
            attack_rect.midright = self.rect.midleft

        # Check if attack hits enemies
        for enemy in self.enemy_group:
            if attack_rect.colliderect(enemy.rect) and enemy.alive:
                enemy.take_damage(10 * self.damage_level)
                self.score += 10
                if pygame.mixer.get_init():
                    sword_sound.play()

                # Create attack particle effect
                for _ in range(5):
                    particle_group.append({
                        'x': attack_rect.centerx,
                        'y': attack_rect.centery,
                        'vx': random.uniform(-2, 2),
                        'vy': random.uniform(-2, 2),
                        'color': (100, 200, 255),
                        'size': random.randint(2, 5),
                        'life': 20
                    })

        # Check if attack hits boss
        for boss in self.boss_group:
            if attack_rect.colliderect(boss.rect) and boss.alive:
                boss.take_damage(15 * self.damage_level)
                self.score += 20
                if pygame.mixer.get_init():
                    sword_sound.play()

                # Create boss hit particle effect
                for _ in range(10):
                    particle_group.append({
                        'x': attack_rect.centerx,
                        'y': attack_rect.centery,
                        'vx': random.uniform(-3, 3),
                        'vy': random.uniform(-3, 3),
                        'color': (255, 100, 100),
                        'size': random.randint(3, 6),
                        'life': 25
                    })

        # Draw attack effect
        attack_surface = pygame.Surface((50, 30))
        pygame.draw.rect(attack_surface, (100, 200, 255, 150), (0, 0, 50, 30))
        if self.direction == -1:
            attack_surface = pygame.transform.flip(attack_surface, True, False)
        screen.blit(attack_surface, attack_rect.topleft)

    def psychic_push(self):
        # Create psychic push area
        push_rect = pygame.Rect(0, 0, 150, 100)
        push_rect.midbottom = self.rect.midtop
        push_rect.y -= 30

        # Check if push hits enemies        # AI
        for enemy in self.enemy_group:
            if push_rect.colliderect(enemy.rect) and enemy.alive:
                # Knock back enemy based on player direction
                push_direction = 1 if enemy.rect.centerx > self.rect.centerx else -1
                enemy.velocity.x = push_direction * 12
                enemy.velocity.y = -5
                enemy.take_damage(5)
                self.score += 5
                if pygame.mixer.get_init():
                    push_sound.play()

                # Create push particle effect
                for _ in range(10):
                    particle_x = random.randint(push_rect.left, push_rect.right)
                    particle_y = random.randint(push_rect.top, push_rect.bottom)
                    particle_group.append({
                        'x': particle_x,
                        'y': particle_y,
                        'vx': push_direction * random.uniform(1, 3),
                        'vy': random.uniform(-3, 0),
                        'color': (200, 100, 255),
                        'size': random.randint(3, 7),
                        'life': 30
                    })

        # Check if push hits boss              # AI
        for boss in self.boss_group:
            if push_rect.colliderect(boss.rect) and boss.alive:
                # Knock back boss
                push_direction = 1 if boss.rect.centerx > self.rect.centerx else -1
                boss.velocity.x = push_direction * 8
                boss.velocity.y = -3
                boss.take_damage(8)
                self.score += 15
                if pygame.mixer.get_init():
                    push_sound.play()

                # Create boss push particle effect
                for _ in range(15):
                    particle_x = random.randint(push_rect.left, push_rect.right)
                    particle_y = random.randint(push_rect.top, push_rect.bottom)
                    particle_group.append({
                        'x': particle_x,
                        'y': particle_y,
                        'vx': push_direction * random.uniform(2, 4),
                        'vy': random.uniform(-4, 0),
                        'color': (255, 100, 255),
                        'size': random.randint(4, 8),
                        'life': 35
                    })

        # Draw push effect      # AI
        push_surface = pygame.Surface((150, 100))
        for i in range(10):
            radius = random.randint(20, 60)
            pos = (random.randint(0, 150), random.randint(0, 100))
            pygame.draw.circle(push_surface, (200, 100, 255, 100), pos, radius, 2)
        screen.blit(push_surface, push_rect.topleft)

    def draw_health_bar(self, surface):
        # Draw health bar background
        bar_width = 200
        bar_height = 20
        fill_width = (self.health / self.max_health) * bar_width

        # Draw health bar background
        pygame.draw.rect(surface, (60, 60, 80), (10, 10, bar_width, bar_height), border_radius=5)
        # Draw health bar
        pygame.draw.rect(surface, GREEN, (10, 10, fill_width, bar_height), border_radius=5)
        # Draw border
        pygame.draw.rect(surface, (200, 200, 220), (10, 10, bar_width, bar_height), 2, border_radius=5)

        # Draw health text
        health_text = font_small.render(f"Health: {int(self.health)}/{self.max_health}", True, WHITE)
        surface.blit(health_text, (220, 10))


# B character
class PlayerB(Player):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load("standing_sprite.png")
        self._draw_B()
        self.character_type = "B"
        self.damage_level = 1.2  # Higher damage

    def _draw_B(self):
        if self.direction == 'neutral':
            self.screen.blit(self.stand, (self.x, self.y))


# andy character
class PlayerAndy(Player):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load("standing_sprite.png")
        self.image = pygame.transform.scale(self.image, (STAND_WIDTH, STAND_HEIGHT))
        self._draw_andy()
        self.character_type = "Andy"
        self.speed_level = 1.3  # Faster speed

    def _draw_andy(self):
        if self.direction == 'neutral':
            self.screen.blit(self.stand, (self.x, self.y))


# A character
class PlayerA(Player):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.Surface((40, 60))
        self._draw_mage()
        self.character_type = "A"
        self.push_cooldown = 40  # Shorter cooldown for psychic push

    def _draw_mage(self):
        # Draw mage body
        pygame.draw.ellipse(self.image, (100, 100, 200), (5, 10, 30, 40))  # Body
        pygame.draw.ellipse(self.image, (70, 70, 180), (5, 10, 30, 40), 2)  # Outline
        pygame.draw.circle(self.image, (100, 100, 200), (20, 8), 8)  # Head
        pygame.draw.circle(self.image, (70, 70, 180), (20, 8), 8, 2)  # Head outline

        # Draw eyes
        pygame.draw.circle(self.image, (200, 200, 100), (15, 6), 3)
        pygame.draw.circle(self.image, (200, 200, 100), (25, 6), 3)

        # Draw robe
        robe_color = (150, 50, 200)
        pygame.draw.polygon(self.image, robe_color, [(0, 50), (40, 50), (30, 60), (10, 60)])
        pygame.draw.polygon(self.image, (120, 30, 170), [(0, 50), (40, 50), (30, 60), (10, 60)], 2)

        # Draw staff
        pygame.draw.rect(self.image, (200, 200, 220), (18, 5, 4, 45))
        pygame.draw.circle(self.image, (255, 215, 0), (20, 5), 8)
        pygame.draw.circle(self.image, (200, 170, 50), (20, 5), 8, 1)


# Enemy class (cool alien creatures)
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="drone"):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((40, 40))
        self._draw_enemy()
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.velocity = pygame.math.Vector2(0, 0)
        self.health = 25
        self.alive = True
        self.direction = random.choice([-1, 1])
        self.move_timer = random.randint(30, 90)
        self.hurt_timer = 0
        self.platform_group = None

    def set_platform_group(self, platform_group):
        self.platform_group = platform_group

    def _draw_enemy(self):
        if self.enemy_type == "drone":
            # Draw alien drone
            pygame.draw.ellipse(self.image, (150, 100, 200), (5, 5, 30, 30))  # Body
            pygame.draw.ellipse(self.image, (100, 70, 180), (5, 5, 30, 30), 2)  # Outline

            # Draw wings
            pygame.draw.ellipse(self.image, (180, 150, 220), (0, 15, 40, 10))
            pygame.draw.ellipse(self.image, (150, 100, 200), (0, 15, 40, 10), 1)

            # Draw eyes
            pygame.draw.circle(self.image, RED, (15, 15), 4)
            pygame.draw.circle(self.image, RED, (25, 15), 4)

            # Draw energy core
            pygame.draw.circle(self.image, (100, 200, 255), (20, 25), 5)
            pygame.draw.circle(self.image, (70, 150, 220), (20, 25), 5, 1)

        else:
            # Draw alien warrior
            pygame.draw.ellipse(self.image, (200, 100, 80), (5, 5, 30, 35))  # Body
            pygame.draw.ellipse(self.image, (180, 80, 60), (5, 5, 30, 35), 2)  # Outline

            # Draw head
            pygame.draw.circle(self.image, (220, 150, 100), (20, 8), 8)
            pygame.draw.circle(self.image, (200, 120, 80), (20, 8), 8, 1)

            # Draw eyes
            pygame.draw.circle(self.image, YELLOW, (15, 6), 3)
            pygame.draw.circle(self.image, YELLOW, (25, 6), 3)

            # Draw weapon
            pygame.draw.rect(self.image, (150, 150, 180), (25, 20, 15, 5))
            pygame.draw.rect(self.image, (120, 120, 150), (25, 20, 15, 5), 1)

            # Draw legs
            pygame.draw.line(self.image, (180, 100, 70), (10, 35), (10, 45), 2)
            pygame.draw.line(self.image, (180, 100, 70), (30, 35), (30, 45), 2)

    def update(self):
        if not self.alive or not self.platform_group:
            return

        # Random movement
        self.move_timer -= 1
        if self.move_timer <= 0:
            self.direction = random.choice([-1, 1])
            self.move_timer = random.randint(30, 90)

        self.velocity.x = self.direction * ENEMY_SPEED

        # Apply gravity
        self.velocity.y += GRAVITY

        # Update position
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Platform collision detection          # AI
        on_ground = False
        for platform in self.platform_group:
            if self.rect.colliderect(platform.rect):
                if self.velocity.y > 0 and self.rect.bottom > platform.rect.top and self.rect.bottom < platform.rect.top + 20:
                    self.rect.bottom = platform.rect.top
                    self.velocity.y = 0
                    on_ground = True

        # Boundary check
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.direction = -1

        # Hurt effect
        if self.hurt_timer > 0:
            self.hurt_timer -= 1

    def take_damage(self, damage):  # AI
        self.health -= damage
        self.hurt_timer = 5  # Hurt effect duration

        if self.health <= 0:
            self.alive = False
            self.image.set_alpha(100)
            if pygame.mixer.get_init():
                death_sound.play()

            # Drop coins based on enemy type
            if self.enemy_type == "drone":
                # Drones drop 1-2 coins
                coins = random.randint(1, 2)
                for _ in range(coins):
                    coin = Coin(self.rect.centerx, self.rect.centery, coin_type=1)  # Yellow coins
                    coin_group.add(coin)
            else:
                # Warriors drop 2-4 coins
                coins = random.randint(2, 4)
                for _ in range(coins):
                    # 80% chance yellow, 20% chance red
                    coin_type = 1 if random.random() < 0.8 else 2
                    coin = Coin(self.rect.centerx, self.rect.centery, coin_type)
                    coin_group.add(coin)

            # Create death particle effect
            for _ in range(15):
                particle_group.append({
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'vx': random.uniform(-3, 3),
                    'vy': random.uniform(-3, 3),
                    'color': (150, 100, 200) if self.enemy_type == "drone" else (200, 100, 80),
                    'size': random.randint(2, 6),
                    'life': 40
                })


# Boss class (evil astronaut)
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 110), pygame.SRCALPHA)
        self._draw_boss()
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.velocity = pygame.math.Vector2(0, 0)
        self.health = 300
        self.max_health = 300
        self.attack_timer = 0
        self.phase = 1
        self.move_direction = 1
        self.move_timer = 0
        self.hurt_timer = 0
        self.alive = True
        self.player = None
        self.bullet_group = None

    def set_references(self, player, bullet_group):  # AI
        self.player = player
        self.bullet_group = bullet_group

    def _draw_boss(self):
        # Draw improved astronaut body
        pygame.draw.rect(self.image, (220, 220, 220), (20, 40, 40, 50))  # Body
        pygame.draw.rect(self.image, (180, 180, 180), (20, 40, 40, 50), 2)  # Outline

        # Draw armor plates
        pygame.draw.rect(self.image, (100, 100, 150), (15, 30, 50, 15))
        pygame.draw.rect(self.image, (80, 80, 130), (15, 30, 50, 15), 1)

        # Draw helmet with visor
        pygame.draw.circle(self.image, (230, 230, 250), (40, 25), 22)  # Helmet
        pygame.draw.circle(self.image, (200, 200, 220), (40, 25), 22, 2)  # Helmet outline

        # Visor with reflection
        pygame.draw.rect(self.image, (100, 150, 220), (20, 10, 40, 20))
        pygame.draw.rect(self.image, (70, 120, 200), (20, 10, 40, 20), 1)
        pygame.draw.ellipse(self.image, (180, 220, 255), (45, 12, 10, 8))

        # Evil glowing eyes
        pygame.draw.circle(self.image, (255, 80, 80), (30, 20), 6)
        pygame.draw.circle(self.image, (255, 180, 100), (30, 20), 3)
        pygame.draw.circle(self.image, (255, 80, 80), (50, 20), 6)
        pygame.draw.circle(self.image, (255, 180, 100), (50, 20), 3)

        # Backpack with thrusters
        pygame.draw.rect(self.image, (80, 80, 100), (10, 45, 20, 35))
        pygame.draw.rect(self.image, (60, 60, 80), (10, 45, 20, 35), 1)

        # Thrusters
        pygame.draw.rect(self.image, (180, 100, 80), (12, 75, 6, 15))
        pygame.draw.rect(self.image, (180, 100, 80), (22, 75, 6, 15))

        # Energy weapon
        pygame.draw.rect(self.image, (180, 80, 220), (55, 50, 20, 10))
        pygame.draw.rect(self.image, (150, 60, 200), (55, 50, 20, 10), 1)

    def update(self):
        if not self.alive or not self.player or not self.bullet_group:
            return

        # Change phase based on health
        if self.health < 200 and self.phase == 1:
            self.phase = 2
            # Phase change effect
            for _ in range(30):
                particle_group.append({
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'vx': random.uniform(-3, 3),
                    'vy': random.uniform(-3, 3),
                    'color': (255, 100, 100),
                    'size': random.randint(3, 7),
                    'life': 40
                })
        if self.health < 100 and self.phase == 2:
            self.phase = 3
            # Phase change effect
            for _ in range(50):
                particle_group.append({
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'vx': random.uniform(-4, 4),
                    'vy': random.uniform(-4, 4),
                    'color': (255, 50, 50),
                    'size': random.randint(4, 8),
                    'life': 50
                })

        # Movement pattern - FIXED MOVEMENT
        self.move_timer -= 1
        if self.move_timer <= 0:
            self.move_direction = random.choice([-1, 1])
            self.move_timer = random.randint(30, 90)

        self.velocity.x = self.move_direction * 3.0  # Increased speed

        # Apply gravity
        self.velocity.y += GRAVITY * 0.3

        # Update position
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Boundary check - keep boss on screen        # AI
        if self.rect.left < 50:
            self.rect.left = 50
            self.move_direction = 1
        if self.rect.right > SCREEN_WIDTH - 50:
            self.rect.right = SCREEN_WIDTH - 50
            self.move_direction = -1

        # Prevent boss from falling off platforms          # AI
        on_ground = False
        for platform in platform_group:
            if self.rect.colliderect(platform.rect):
                if self.velocity.y > 0 and self.rect.bottom > platform.rect.top and self.rect.bottom < platform.rect.top + 20:
                    self.rect.bottom = platform.rect.top
                    self.velocity.y = 0
                    on_ground = True

        # Attack
        self.attack_timer -= 1
        if self.attack_timer <= 0:
            self.attack()
            self.attack_timer = 50 - (self.phase * 10)  # Faster attacks in later phases

        # Hurt effect
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            # Visual feedback - flash red when hurt
            if self.hurt_timer % 3 == 0:
                self.image.fill((255, 100, 100, 50), special_flags=pygame.BLEND_RGBA_ADD)
            else:
                self._draw_boss()  # AI

    def take_damage(self, damage):
        self.health -= damage
        self.hurt_timer = 10  # Longer hurt effect

        if self.health <= 0:
            self.alive = False
            self.image.set_alpha(100)
            if pygame.mixer.get_init():
                boss_death_sound.play()

            # Drop high-value coins
            for _ in range(20):
                # 60% yellow, 30% red, 10% black
                rand = random.random()
                if rand < 0.6:
                    coin_type = 1  # Yellow
                elif rand < 0.9:
                    coin_type = 2  # Red
                else:
                    coin_type = 3  # Black

                coin = Coin(self.rect.centerx, self.rect.centery, coin_type)
                coin_group.add(coin)

            # Create death particle effect
            for _ in range(70):
                particle_group.append({
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'vx': random.uniform(-5, 5),
                    'vy': random.uniform(-5, 5),
                    'color': (255, 50, 50),
                    'size': random.randint(3, 8),
                    'life': 70
                })

    def draw_health_bar(self, surface):
        # Draw Boss health bar
        bar_width = 400
        bar_height = 30
        fill_width = (self.health / self.max_health) * bar_width

        # Health bar background
        pygame.draw.rect(surface, (70, 70, 90), (SCREEN_WIDTH // 2 - bar_width // 2, 20, bar_width, bar_height),
                         border_radius=5)
        # Health bar
        pygame.draw.rect(surface, RED, (SCREEN_WIDTH // 2 - bar_width // 2, 20, fill_width, bar_height),
                         border_radius=5)
        # Border
        pygame.draw.rect(surface, WHITE, (SCREEN_WIDTH // 2 - bar_width // 2, 20, bar_width, bar_height), 3,
                         border_radius=5)

        # Draw health text
        health_text = font_medium.render(f"Health bar: {int(self.health)}/{self.max_health}", True, WHITE)
        surface.blit(health_text, (SCREEN_WIDTH // 2 - health_text.get_width() // 2, 50))


# Boss bullet class
class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, angle_offset=0):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 80, 80), (7, 7), 7)
        pygame.draw.circle(self.image, (255, 220, 120), (7, 7), 4)
        self.rect = self.image.get_rect(center=(x, y))

        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        distance = max(1, math.sqrt(dx * dx + dy * dy))

        # Apply angle offset
        angle = math.atan2(dy, dx)
        angle += math.radians(angle_offset)

        # Set velocity
        self.velocity = pygame.math.Vector2(
            math.cos(angle) * BOSS_BULLET_SPEED,
            math.sin(angle) * BOSS_BULLET_SPEED
        )

        # Create bullet particles
        for _ in range(3):
            particle_group.append({
                'x': x,
                'y': y,
                'vx': self.velocity.x * 0.5 + random.uniform(-0.5, 0.5),
                'vy': self.velocity.y * 0.5 + random.uniform(-0.5, 0.5),
                'color': (255, 180, 80),
                'size': random.randint(2, 4),
                'life': 15
            })

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Create trail particles
        if random.random() < 0.5:
            particle_group.append({
                'x': self.rect.centerx,
                'y': self.rect.centery,
                'vx': self.velocity.x * -0.2 + random.uniform(-0.5, 0.5),
                'vy': self.velocity.y * -0.2 + random.uniform(-0.5, 0.5),
                'color': (255, 200, 100),
                'size': random.randint(1, 3),
                'life': 10
            })

        # Remove when off-screen
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()


# Homing bullet class
class HomingBullet(BossBullet):
    def __init__(self, x, y, target):
        super().__init__(x, y, x, y)  # Initial target is self position
        self.target = target
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 2.5
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 80, 255), (7, 7), 7)
        pygame.draw.circle(self.image, (230, 150, 255), (7, 7), 4)

    def update(self):
        # Track target
        if self.target:
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            distance = max(1, math.sqrt(dx * dx + dy * dy))

            # Normalize and set velocity
            self.velocity.x = (dx / distance) * self.speed
            self.velocity.y = (dy / distance) * self.speed

        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Create trail particles
        if random.random() < 0.7:
            particle_group.append({
                'x': self.rect.centerx,
                'y': self.rect.centery,
                'vx': self.velocity.x * -0.3 + random.uniform(-0.5, 0.5),
                'vy': self.velocity.y * -0.3 + random.uniform(-0.5, 0.5),
                'color': (180, 100, 255),
                'size': random.randint(1, 3),
                'life': 12
            })

        # Remove when off-screen
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
                self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=PLATFORM_COLOR):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)

        # Add platform texture
        for i in range(0, width, 10):
            pygame.draw.line(self.image, (color[0] - 20, color[1] - 20, color[2] - 20),
                             (i, 0), (i, height), 2)

        # Add platform top highlight
        pygame.draw.line(self.image, (color[0] + 30, color[1] + 30, color[2] + 30),
                         (0, 0), (width, 0), 2)

        self.rect = self.image.get_rect(topleft=(x, y))

    def get_rect(self):
        return self.rect

# Coin class with multiple values
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, coin_type=1):
        super().__init__()
        self.coin_type = coin_type  # 1=yellow, 2=red, 3=black
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)

        # Set coin value and colors based on type
        if coin_type == 1:  # Yellow coin (value 1)
            self.value = 1
            color1 = (255, 215, 0)  # Gold
            color2 = (255, 255, 100)  # Light yellow
            color3 = (255, 240, 50)  # Bright yellow
        elif coin_type == 2:  # Red coin (value 5)
            self.value = 5
            color1 = (255, 50, 50)  # Red
            color2 = (255, 150, 150)  # Light red
            color3 = (255, 100, 100)  # Bright red
        else:  # Black coin (value 10)
            self.value = 10
            color1 = (50, 50, 50)  # Black
            color2 = (100, 100, 100)  # Dark gray
            color3 = (150, 150, 150)  # Gray

        # Draw coin
        pygame.draw.circle(self.image, color1, (10, 10), 10)
        pygame.draw.circle(self.image, color2, (10, 10), 8)
        pygame.draw.circle(self.image, color3, (10, 10), 5)

        self.rect = self.image.get_rect(center=(x, y))
        self.float_timer = random.randint(0, 100)

    def update(self):
        # Floating effect
        self.float_timer += 0.1
        self.rect.y += math.sin(self.float_timer) * 0.5

        # Rotation effect
        rotated = pygame.transform.rotate(self.image, math.sin(self.float_timer) * 5)
        new_rect = rotated.get_rect(center=self.rect.center)
        self.image = rotated
        self.rect = new_rect


# Shop class
class Shop:
    def __init__(self):
        self.visible = False
        self.items = [
            {"name": "Health Potion", "cost": 10, "type": "health", "desc": "Restore 30 HP"},
            {"name": "Damage Upgrade", "cost": 20, "type": "damage", "desc": "Permanently increase damage by 50%"},
            {"name": "Speed Upgrade", "cost": 30, "type": "speed", "desc": "Permanently increase speed by 30%"}
        ]
        self.selected_index = 0

    def draw(self, surface, player):
        if not self.visible:
            return

        # Draw shop background
        shop_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 200, 500, 400)
        pygame.draw.rect(surface, (40, 20, 60, 220), shop_rect, border_radius=15)
        pygame.draw.rect(surface, (180, 70, 255), shop_rect, 4, border_radius=15)

        # Draw title
        title = font_medium.render("Alien Shop", True, (255, 215, 0))
        surface.blit(title, (shop_rect.centerx - title.get_width() // 2, shop_rect.top + 30))

        # Draw coin info
        coins_text = font_small.render(f"Coins: {player.coins}", True, (255, 215, 0))
        surface.blit(coins_text, (shop_rect.centerx - coins_text.get_width() // 2, shop_rect.top + 80))

        # Draw items list
        for i, item in enumerate(self.items):
            # Background
            item_rect = pygame.Rect(shop_rect.left + 50, shop_rect.top + 130 + i * 70, 400, 60)
            if i == self.selected_index:
                pygame.draw.rect(surface, (80, 40, 100, 220), item_rect, border_radius=10)
                pygame.draw.rect(surface, (200, 150, 255), item_rect, 3, border_radius=10)
            else:
                pygame.draw.rect(surface, (60, 30, 80, 180), item_rect, border_radius=10)

            # Item name and price
            color = (200, 200, 255) if i == self.selected_index else (180, 180, 220)
            item_text = font_small.render(f"{item['name']} - {item['cost']} coins", True, color)
            surface.blit(item_text, (item_rect.centerx - item_text.get_width() // 2, item_rect.top + 10))

            # Item description
            desc_text = font_tiny.render(item['desc'], True, (200, 200, 200))
            surface.blit(desc_text, (item_rect.centerx - desc_text.get_width() // 2, item_rect.top + 35))

        # Draw purchase instructions
        info_text = font_small.render("W/S: Select | SPACE: Buy | TAB: Close Shop", True, (150, 200, 255))
        surface.blit(info_text, (shop_rect.centerx - info_text.get_width() // 2, shop_rect.bottom - 50))

    def purchase(self, player):
        if not self.visible:
            return False

        item = self.items[self.selected_index]
        if player.coins >= item["cost"]:
            player.coins -= item["cost"]

            if item["type"] == "health":
                player.health = min(player.max_health, player.health + 30)
            elif item["type"] == "damage":
                player.damage_level += 0.5
            elif item["type"] == "speed":
                player.speed_level += 0.3

            if pygame.mixer.get_init():
                purchase_sound.play()
            return True

        return False


# Draw start menu with game rules
def draw_start_menu(high_score):
    # Draw star background
    screen.fill(BACKGROUND_COLOR)
    for star in stars:
        star.draw(screen)

    # Draw title with glow effect
    title = font_large.render("Planet-8-studio", True, (100, 200, 255))

    # Title glow
    for i in range(5, 0, -1):
        glow_color = (100, 200, 255, 100 - i * 20)
        glow_surf = pygame.Surface((title.get_width() + i * 10, title.get_height() + i * 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, glow_color, (0, 0, glow_surf.get_width(), glow_surf.get_height()), border_radius=15)
        screen.blit(glow_surf, (SCREEN_WIDTH // 2 - glow_surf.get_width() // 2, 80 - i * 2))

    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

    # Draw high score
    high_score_text = font_medium.render(f"High Score: {high_score}", True, (255, 215, 0))
    screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 180))

    # Draw story panel
    panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 450, 250, 900, 300)
    pygame.draw.rect(screen, (20, 10, 40, 220), panel_rect, border_radius=15)
    pygame.draw.rect(screen, (100, 70, 200), panel_rect, 3, border_radius=15)

    # Story text
    story_title = font_medium.render("The Story (Background)", True, (255, 215, 0))
    screen.blit(story_title, (panel_rect.centerx - story_title.get_width() // 2, panel_rect.top + 20))

    story_lines = [
        "In the distant future, after humans have conquered the solar system that we live in, they moved on to other solar systems",
        "and eventually the entire universe. They began to set their sights on planets further and further away from Earth, and found the planet Othryn.",
        "Once the humans came, the took over Othryn like a virus, spreading in the blink of an eye.",
        "The aliens were unhappy with their new rulers, and revolted, and after a civil war that spanned 17 years, the few surviving rebels were forced into hiding",
        "The humans left after the planet was thrashed, leaving behind a few squads of their army to keep the planet under their control.",
        "Now, multiple years later, its up to Plibo to free Othryn from the human's rule.",
    ]

    for i, line in enumerate(story_lines):
        text = font_tinytiny.render(line, True, (200, 200, 255))
        screen.blit(text, (panel_rect.centerx - text.get_width() // 2, panel_rect.top + 85 + i * 35))


    # Draw controls panel
    ctrl_rect = pygame.Rect(SCREEN_WIDTH // 2 - 350, 570, 700, 275)
    pygame.draw.rect(screen, (20, 10, 40, 220), ctrl_rect, border_radius=15)
    pygame.draw.rect(screen, (100, 70, 200), ctrl_rect, 3, border_radius=15)

    controls_title = font_medium.render("Controls", True, (255, 215, 0))
    screen.blit(controls_title, (ctrl_rect.centerx - controls_title.get_width() // 2, ctrl_rect.top + 20))

    controls = [
        "WASD: Move & Jump",
        "SPACE: Lightsaber Attack",
        "SHIFT: Psychic Push",
        "TAB: Open/Close Shop"
    ]

    for i, control in enumerate(controls):
        text = font_tiny.render(control, True, (200, 200, 255))
        screen.blit(text, (ctrl_rect.centerx - text.get_width() // 2, ctrl_rect.top + 90 + i * 40))

    # Start prompt
    start_text = font_medium.render("Press SPACE to Start", True, (100, 255, 100))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT - 100))

    # Blink effect
    if pygame.time.get_ticks() % 1000 < 500:
        pygame.draw.rect(screen, (100, 255, 100),
                         (SCREEN_WIDTH // 2 - start_text.get_width() // 2 - 10,
                          SCREEN_HEIGHT - 100 - 5,
                          start_text.get_width() + 20,
                          start_text.get_height() + 10),
                         3, border_radius=5)


# Draw character selection screen
def draw_character_selection(high_score):
    # Draw star background
    screen.fill(BACKGROUND_COLOR)
    for star in stars:
        star.draw(screen)

    # Draw title
    title = font_large.render("SELECT YOUR HERO", True, (100, 200, 255))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

    # Draw high score
    high_score_text = font_medium.render(f"High Score: {high_score}", True, (255, 215, 0))
    screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 700))

    # Draw character panels
    char_width = 280
    char_height = 380
    spacing = 40

    # B panel
    warrior_rect = pygame.Rect(SCREEN_WIDTH // 2 - char_width * 1.5 - spacing, 150, char_width, char_height)
    pygame.draw.rect(screen, (40, 20, 60, 220), warrior_rect, border_radius=15)
    pygame.draw.rect(screen, (200, 50, 50), warrior_rect, 4, border_radius=15)

    # Draw B character
    warrior_img = pygame.Surface((120, 180), pygame.SRCALPHA)
    pygame.draw.ellipse(warrior_img, (200, 50, 50), (10, 30, 100, 120))
    pygame.draw.ellipse(warrior_img, (180, 30, 30), (10, 30, 100, 120), 2)
    screen.blit(warrior_img, (warrior_rect.centerx - 60, warrior_rect.top + 30))

    # B info
    warrior_title = font_medium.render("B", True, (255, 150, 150))
    screen.blit(warrior_title, (warrior_rect.centerx - warrior_title.get_width() // 2, warrior_rect.top + 20))

    warrior_desc = [
        "High Damage",
        "Strong Attacks",
        "Press 1 to select"
    ]

    for i, line in enumerate(warrior_desc):
        text = font_small.render(line, True, (255, 200, 200))
        screen.blit(text, (warrior_rect.centerx - text.get_width() // 2, warrior_rect.top + 220 + i * 40))

    # andy panel
    rogue_rect = pygame.Rect(SCREEN_WIDTH // 2 - char_width // 2, 150, char_width, char_height)
    pygame.draw.rect(screen, (40, 20, 60, 220), rogue_rect, border_radius=15)
    pygame.draw.rect(screen, (50, 200, 80), rogue_rect, 4, border_radius=15)

    # Draw andy character
    rogue_img = pygame.Surface((120, 180), pygame.SRCALPHA)
    pygame.draw.ellipse(rogue_img, (50, 200, 80), (10, 30, 100, 120))
    pygame.draw.ellipse(rogue_img, (30, 150, 50), (10, 30, 100, 120), 2)
    screen.blit(rogue_img, (rogue_rect.centerx - 60, rogue_rect.top + 30))

    # andy info
    rogue_title = font_medium.render("Andy", True, (150, 255, 200))
    screen.blit(rogue_title, (rogue_rect.centerx - rogue_title.get_width() // 2, rogue_rect.top + 20))

    rogue_desc = [
        "High Speed",
        "Quick Movement",
        "Press 2 to select"
    ]

    for i, line in enumerate(rogue_desc):
        text = font_small.render(line, True, (200, 255, 200))
        screen.blit(text, (rogue_rect.centerx - text.get_width() // 2, rogue_rect.top + 220 + i * 40))

    # A panel
    mage_rect = pygame.Rect(SCREEN_WIDTH // 2 + char_width // 2 + spacing, 150, char_width, char_height)
    pygame.draw.rect(screen, (40, 20, 60, 220), mage_rect, border_radius=15)
    pygame.draw.rect(screen, (100, 100, 200), mage_rect, 4, border_radius=15)

    # Draw A character
    mage_img = pygame.Surface((120, 180), pygame.SRCALPHA)
    pygame.draw.ellipse(mage_img, (100, 100, 200), (10, 30, 100, 120))
    pygame.draw.ellipse(mage_img, (70, 70, 180), (10, 30, 100, 120), 2)
    screen.blit(mage_img, (mage_rect.centerx - 60, mage_rect.top + 30))

    # A info
    mage_title = font_medium.render("A", True, (180, 180, 255))
    screen.blit(mage_title, (mage_rect.centerx - mage_title.get_width() // 2, mage_rect.top + 20))

    mage_desc = [
        "Psychic Mastery",
        "Strong Push Ability",
        "Press 3 to select"
    ]

    for i, line in enumerate(mage_desc):
        text = font_small.render(line, True, (220, 220, 255))
        screen.blit(text, (mage_rect.centerx - text.get_width() // 2, mage_rect.top + 220 + i * 40))

    # Start prompt
    start_text = font_medium.render("Press SPACE to Start", True, (100, 255, 100))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT - 100))

    # Blink effect
    if pygame.time.get_ticks() % 1000 < 500:
        pygame.draw.rect(screen, (100, 255, 100),
                         (SCREEN_WIDTH // 2 - start_text.get_width() // 2 - 10,
                          SCREEN_HEIGHT - 100 - 5,
                          start_text.get_width() + 20,
                          start_text.get_height() + 10),
                         3, border_radius=5)


# Create sound effects
def create_beep_sound(frequency=440, duration=100):
    sample_rate = 44100
    n_samples = int(round(duration * 0.001 * sample_rate))

    # Create buffer for sound
    buf = bytearray(n_samples * 2 * 2)  # 16-bit stereo

    # Fill buffer with sine wave
    max_amplitude = 32767 * 0.3  # 30% volume
    for i in range(n_samples):
        t = float(i) / sample_rate
        value = int(round(max_amplitude * math.sin(2 * math.pi * frequency * t)))
        # Left and right channels
        buf[4 * i] = value & 0xff
        buf[4 * i + 1] = (value >> 8) & 0xff
        buf[4 * i + 2] = value & 0xff
        buf[4 * i + 3] = (value >> 8) & 0xff

    return pygame.mixer.Sound(buffer=bytes(buf))


# Create sounds
try:
    jump_sound = create_beep_sound(523, 100)  # C5
    sword_sound = create_beep_sound(784, 50)  # G5
    push_sound = create_beep_sound(262, 200)  # C4
    gun_sound = create_beep_sound(392, 30)  # G4
    shotgun_sound = create_beep_sound(196, 100)  # G3
    laser_sound = create_beep_sound(1047, 20)  # C6
    death_sound = create_beep_sound(110, 500)  # A2
    boss_death_sound = create_beep_sound(55, 800)  # A1
    purchase_sound = create_beep_sound(659, 100)  # E5
    coin_sound = create_beep_sound(330, 50)  # E4
    select_sound = create_beep_sound(330, 50)  # E4
except:
    # If sound creation fails, set all to None
    jump_sound = sword_sound = push_sound = gun_sound = shotgun_sound = laser_sound = None
    death_sound = boss_death_sound = purchase_sound = coin_sound = select_sound = None

# Create game sprite groups
all_sprites = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

# Create platforms (planet surface)
platforms = [
    # Ground
    Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),

    # Platforms
    Platform(200, SCREEN_HEIGHT - 150, 200, 25),
    Platform(500, SCREEN_HEIGHT - 200, 150, 20),
    Platform(800, SCREEN_HEIGHT - 250, 200, 20),
    Platform(100, SCREEN_HEIGHT - 300, 200, 15),
    Platform(500, SCREEN_HEIGHT - 350, 150, 30),
    Platform(900, SCREEN_HEIGHT - 600, 400, 10),
    Platform(1000, SCREEN_HEIGHT - 500, 300, 20),
    Platform(700, SCREEN_HEIGHT - 300, 150, 20),
    Platform(600, SCREEN_HEIGHT - 400, 150, 20),
    Platform(100, SCREEN_HEIGHT - 650, 200, 20),
    Platform(1100, SCREEN_HEIGHT - 100, 100, 20),
    Platform(1050, SCREEN_HEIGHT - 250, 150, 20),
    Platform(500, SCREEN_HEIGHT - 800, 200, 20),

    # High platforms
    Platform(400, SCREEN_HEIGHT - 450, 100, 20),
    Platform(1000, SCREEN_HEIGHT - 20, 150, 30),

    # Extra platforms
    Platform(300, SCREEN_HEIGHT - 500, 150, 20),
    Platform(700, SCREEN_HEIGHT - 550, 100, 20),
]

# Add platforms to group
for platform in platforms:
    platform_group.add(platform)
    all_sprites.add(platform)

left_filename = ["First_Move_Left.png", "Second_Move_Left.png", "Third_Move_Left.png", "Fourth_Move_Left.png"]
right_filename = ["First_Move_Right.png", "Second_Move_Right.png", "Third_Move_Right.png", "Fourth_Move_Right.png"]


# Create enemies (initial set)
enemies = [
    Badguy(screen, 290, 170, 100, 56, left_filename, right_filename),
    Badguy(screen, 490, 220, 100, 56, left_filename, right_filename),
    Badguy(screen, 840, 270, 100, 56, left_filename, right_filename),
    Badguy(screen, 140, 320, 100, 56, left_filename, right_filename),
    Badguy(screen, 640, 370, 100, 56, left_filename, right_filename),
    Badguy(screen, 340, 520, 100, 56, left_filename, right_filename),
    Badguy(screen, 750, 570, 100, 56, left_filename, right_filename),
]

# Add enemies to group
# for enemy in enemies:
#     enemy.set_platform_group(platform_group)
#     enemy_group.add(enemy)
#     all_sprites.add(enemy)

# Create Boss
boss = Boss(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 400)
# all_sprites.add(boss)
# boss_group.add(boss)

# Create shop
shop = Shop()

# Create star background
stars = [StarParticle() for _ in range(200)]

# Particle system
particle_group = []

# Game state
game_state = "start_menu"  # "start_menu", "character_selection", "playing", "game_over", "victory"
game_start_time = pygame.time.get_ticks()

# Enemy spawn variables
spawn_timer = 0
max_enemies = 150
enemy_types = ["drone", "warrior"]

# Character selection
selected_character = None
player = None

# High score management
high_score = read_high_score()
score_saved = False  # 标记分数是否已保存

# Game main loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_TAB and game_state == "playing":
                shop.visible = not shop.visible
            elif event.key == K_w and shop.visible:
                shop.selected_index = (shop.selected_index - 1) % len(shop.items)
            elif event.key == K_s and shop.visible:
                shop.selected_index = (shop.selected_index + 1) % len(shop.items)
            elif event.key == K_SPACE:
                if game_state == "start_menu":
                    game_state = "character_selection"
                elif game_state == "character_selection" and selected_character:
                    game_state = "playing"
                elif shop.visible:
                    shop.purchase(player)
            elif event.key == K_r and (game_state == "game_over" or game_state == "victory"):
                # Restart game
                game_state = "character_selection"
                selected_character = None
                player = None
                score_saved = False

                # Clear all groups
                all_sprites.empty()
                platform_group.empty()
                enemy_group.empty()
                boss_group.empty()
                bullet_group.empty()
                coin_group.empty()

                # Recreate platforms
                for platform in platforms:
                    platform_group.add(platform)
                    all_sprites.add(platform)

                # Recreate enemies
                for enemy in enemies:
                    enemy.set_platform_group(platform_group)
                    enemy_group.add(enemy)
                    all_sprites.add(enemy)

                # Recreate Boss
                boss = Boss(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 400)
                all_sprites.add(boss)
                boss_group.add(boss)

                # Reset spawn timer
                spawn_timer = 0

                game_start_time = pygame.time.get_ticks()
            elif game_state == "character_selection":
                if event.key == K_1:
                    selected_character = "B"
                    if pygame.mixer.get_init() and select_sound:
                        select_sound.play()
                elif event.key == K_2:
                    selected_character = "andy"
                    if pygame.mixer.get_init() and select_sound:
                        select_sound.play()
                elif event.key == K_3:
                    selected_character = "A"
                    if pygame.mixer.get_init() and select_sound:
                        select_sound.play()
            elif game_state == "victory" and not score_saved:
                # 在胜利状态下处理保存分数
                if event.key == K_y:  # 按Y键保存分数
                    save_high_score(player.score)
                    high_score = read_high_score()  # 更新最高分
                    score_saved = True
                    if pygame.mixer.get_init() and purchase_sound:
                        purchase_sound.play()
                elif event.key == K_n:  # 按N键不保存
                    score_saved = True
                    if pygame.mixer.get_init() and select_sound:
                        select_sound.play()

    # Update star background
    for star in stars:
        star.update()

    # Update particles
    for particle in particle_group[:]:
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        particle['life'] -= 1
        if particle['life'] <= 0:
            particle_group.remove(particle)

    # Draw background
    screen.fill(BACKGROUND_COLOR)

    # Draw star background
    for star in stars:
        star.draw(screen)



    # Draw particles
    for particle in particle_group:
        size = particle['size']
        pygame.draw.circle(screen, particle['color'],
                           (int(particle['x']), int(particle['y'])),
                           int(size))

    # Game state handling
    if game_state == "start_menu":
        draw_start_menu(high_score)

    elif game_state == "character_selection":
        draw_character_selection(high_score)

        # Highlight selected character
        if selected_character:
            text = font_medium.render(f"Selected: {selected_character.upper()}", True, (255, 215, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 160))

        # Create player if not created
        if selected_character and not player:
            if selected_character == "B":
                player = PlayerB(100, SCREEN_HEIGHT - 100)
            elif selected_character == "andy":
                player = PlayerAndy(100, SCREEN_HEIGHT - 100)
            elif selected_character == "A":
                player = PlayerA(100, SCREEN_HEIGHT - 100)

            if player:
                player.set_groups(platform_group, enemy_group, boss_group)
                all_sprites.add(player)

    elif game_state == "playing" and player:
        # Draw all sprites
        all_sprites.draw(screen)
        bullet_group.draw(screen)
        coin_group.draw(screen)

        for enemy in enemies:
            enemy.move(platform_group.sprites())
            enemy.animate()
            enemy.draw()
            print(f"{enemy.get_rect().x} {enemy.get_rect().y}")

        boss.update()

        # Draw player
        if player.hurt_timer > 0 and pygame.time.get_ticks() % 100 < 50:
            # Hurt blink effect
            pass
        else:
            screen.blit(player.image, player.rect)

        # Draw Boss
        screen.blit(boss.image, boss.rect)

        # Draw player health bar
        player.draw_health_bar(screen)

        # Draw Boss health bar
        if boss.alive:
            boss.draw_health_bar(screen)

        # Semi-transparent background
        pygame.draw.rect(screen, (20, 10, 40, 180),
                         (SCREEN_WIDTH - 230, 5, 200, 95), border_radius=10)
        pygame.draw.rect(screen, (100, 70, 200),
                         (SCREEN_WIDTH - 230, 5, 200, 95), 2, border_radius=10)

        score_text = font_small.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 50, 15))

        coins_text = font_small.render(f"Coins: {player.coins}", True, (255, 215, 0))
        screen.blit(coins_text, (SCREEN_WIDTH - coins_text.get_width() - 50, 50))

        # Draw upgrade status
        upgrades_text = font_tiny.render(f"Dmg: {player.damage_level:.1f}x | Spd: {player.speed_level:.1f}x", True,
                                         (150, 255, 150))
        screen.blit(upgrades_text, (SCREEN_WIDTH - upgrades_text.get_width() - 15, 100))

        # Draw shop
        shop.draw(screen, player)

        # Draw controls hint
        controls_text = font_small.render("A/D: Move | W: Jump | SPACE: Attack | SHIFT: Push | TAB: Shop", True,
                                          (200, 200, 200))
        screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 40))

        # Update game state
        all_sprites.update()
        bullet_group.update()
        coin_group.update()

        # Enemy spawn logic
        spawn_timer -= 1
        if spawn_timer <= 0 and len(enemy_group) < max_enemies and boss.alive:
            # Spawn new enemy
            enemy_type = random.choice(enemy_types)
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(-100, -40)  # Spawn above screen

            new_enemy = Enemy(x, y, enemy_type)
            new_enemy.set_platform_group(platform_group)
            enemy_group.add(new_enemy)
            all_sprites.add(new_enemy)

            # Reset spawn timer (1-3 seconds)
            spawn_timer = random.randint(60, 180)

        # Detect coin collection
        coins_collected = pygame.sprite.spritecollide(player, coin_group, True)
        for coin in coins_collected:
            player.coins += coin.value
            player.score += 5
            if pygame.mixer.get_init() and coin_sound:
                coin_sound.play()

            # Create coin collection particles
            for _ in range(5):
                particle_group.append({
                    'x': coin.rect.centerx,
                    'y': coin.rect.centery,
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-2, 2),
                    'color': (255, 215, 0),
                    'size': random.randint(2, 4),
                    'life': 20
                })

        # Detect bullets hitting player - INCREASED DAMAGE
        if pygame.sprite.spritecollide(player, bullet_group, True):
            player.health -= 8  # Increased from 4 to 8
            player.hurt_timer = 10
            if player.health < 0:
                player.health = 0

            # Create hurt particles
            for _ in range(10):
                particle_group.append({
                    'x': player.rect.centerx,
                    'y': player.rect.centery,
                    'vx': random.uniform(-3, 3),
                    'vy': random.uniform(-3, 3),
                    'color': (255, 50, 50),
                    'size': random.randint(2, 5),
                    'life': 15
                })

        # Check game over conditions
        if player.health <= 0:
            game_state = "game_over"
        elif not boss.alive:
            game_state = "victory"

    elif game_state == "game_over":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        game_over_text = font_large.render("Mission Failed", True, (255, 80, 80))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                     SCREEN_HEIGHT // 2 - 100))

        score_text = font_medium.render(f"Final Score: {player.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                                 SCREEN_HEIGHT // 2))

        high_score_text = font_medium.render(f"High Score: {high_score}", True, (255, 215, 0))
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2 + 50))

        restart_text = font_small.render("Press R to restart", True, (100, 255, 100))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                   SCREEN_HEIGHT // 2 + 120))

    elif game_state == "victory":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 30, 0, 180))
        screen.blit(overlay, (0, 0))

        victory_text = font_large.render("Mission Complete!", True, (100, 255, 100))
        screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2,
                                   SCREEN_HEIGHT // 2 - 150))

        score_text = font_medium.render(f"Final Score: {player.score}", True, (255, 215, 0))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                                 SCREEN_HEIGHT // 2 - 80))

        # 显示最高分
        high_score_text = font_medium.render(f"High Score: {high_score}", True, (255, 215, 0))
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2 - 20))

        if not score_saved:
            # 询问是否保存分数
            save_text = font_medium.render("Save this score as high score?", True, (100, 200, 255))
            screen.blit(save_text, (SCREEN_WIDTH // 2 - save_text.get_width() // 2,
                                    SCREEN_HEIGHT // 2 + 40))

            yes_text = font_small.render("Y for YES", True, (100, 255, 100))
            screen.blit(yes_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100))

            no_text = font_small.render("N for NO", True, (255, 100, 100))
            screen.blit(no_text, (SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 100))
        else:
            # 显示分数已保存
            saved_text = font_medium.render("Score saved successfully!", True, (100, 255, 100))
            screen.blit(saved_text, (SCREEN_WIDTH // 2 - saved_text.get_width() // 2,
                                     SCREEN_HEIGHT // 2 + 40))

            # 显示重启提示
            restart_text = font_small.render("Press R to restart", True, (100, 255, 100))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                       SCREEN_HEIGHT // 2 + 100))

    # Update screen
    pygame.display.flip()
    clock.tick(FPS)

# Quit game
pygame.quit()
sys.exit()