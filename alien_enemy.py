import pygame
import sys
import random
import time
from alien import Alien
from enemies import Badguy  # assuming Badguy class is defined here

def main():
    # Initialize pygame
    pygame.init()

    # Create a screen
    pygame.display.set_caption("Planet-8 Studios")
    screen = pygame.display.set_mode((720, 560))

    # Image dimensions
    STAND_HEIGHT = 80
    STAND_WIDTH = 56
    LR_HEIGHT = 80
    LR_WIDTH = 80
    RR_HEIGHT = 80
    RR_WIDTH = 80

    # Try loading the alien
    try:
        my_alien = Alien(
            screen,
            20,
            400,
            "standing_sprite.png",
            "left_running.png",
            "left_lunging.png",
            "right_running.png",
            "right_lunging.png"
        )
    except pygame.error as e:
        print("Image load error:", e)
        pygame.quit()
        sys.exit()

    # Optionally scale the standing image
    my_alien.stand = pygame.transform.scale(my_alien.stand, (STAND_WIDTH, STAND_HEIGHT))
    my_alien.l_run = pygame.transform.scale(my_alien.l_run, (LR_WIDTH, LR_HEIGHT))
    my_alien.r_run = pygame.transform.scale(my_alien.r_run, (RR_WIDTH, RR_HEIGHT))

    # Create astronaut (enemy)
    left_frames = [
        "First_Move_Left.png",
        "Second_Move_Left.png",
        "Third_Move_Left.png",
        "Fourth_Move_Left.png"
    ]
    right_frames = [
        "First_Move_Right.png",
        "Second_Move_Right.png",
        "Third_Move_Right.png",
        "Fourth_Move_Right.png"
    ]
    astronaut = Badguy(screen, 400, 400, 100, 56, left_frames, right_frames)

    # Framerate
    clock = pygame.time.Clock()

    # Jumping and gravity
    gravity = 0.8
    jump_speed = -14
    velocity_y = 0
    is_jumping = False
    ground_y = 475

    # Obstacles
    obstacles = [
        pygame.Rect(50, 490, 50, 4),
        pygame.Rect(100, 530, 50, 4),
        pygame.Rect(600, 400, 50, 50),  # From astronaut code
        pygame.Rect(100, 400, 50, 50)
    ]

    # Game loop
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Movement and jump
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT]:
            my_alien.x -= 2
            my_alien.direction = 'left'
        if pressed_keys[pygame.K_RIGHT]:
            my_alien.x += 2
            my_alien.direction = 'right'
        if pressed_keys[pygame.K_UP] and not is_jumping:
            velocity_y = jump_speed
            is_jumping = True
        if not any(pressed_keys):
            my_alien.direction = 'neutral'

        # Apply gravity
        velocity_y += gravity
        my_alien.y += velocity_y

        # Collision check
        on_obstacle = False
        alien_rect = pygame.Rect(my_alien.x, my_alien.y, STAND_WIDTH, STAND_HEIGHT)
        for obstacle in obstacles:
            if alien_rect.colliderect(obstacle) and velocity_y >= 0:
                if alien_rect.bottom >= obstacle.top and alien_rect.bottom - velocity_y < obstacle.top + 5:
                    my_alien.y = obstacle.top - STAND_HEIGHT
                    velocity_y = 0
                    is_jumping = False
                    on_obstacle = True
                    break

        # Ground check
        if my_alien.y >= ground_y and not on_obstacle:
            my_alien.y = ground_y
            velocity_y = 0
            is_jumping = False

        # Drawing
        screen.fill((255, 255, 255))  # Clear screen with white
        for obs in obstacles:
            pygame.draw.rect(screen, "magenta", obs)

        # Update and draw alien
        my_alien.draw()

        # Move and draw astronaut
        astronaut.move(obstacles)
        astronaut.draw()

        pygame.display.update()

# Only run the game if this file is executed directly
if __name__ == "__main__":
    main()
