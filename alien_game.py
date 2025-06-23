from alien import Alien
import pygame
import sys
import alien
import random
import time

def main():
    # turn on pygame
    pygame.init()

    # create a screen
    pygame.display.set_caption("Planet-8 Studios")
    # TODO: Change the size of the screen as you see fit!
    screen = pygame.display.set_mode((720, 560))
    # creates a Character from the alien.py file
    alien = Alien(screen, 20, 400, "standing_sprite.png", "left_running.png", "left_lunging.png", "right_running.png", "right_lunging.png")

    # let's set the framerate
    clock = pygame.time.Clock()

    IMAGE_HEIGHT = 80
    IMAGE_WIDTH = 56

    alien.stand = pygame.transform.scale(alien.stand, (IMAGE_WIDTH, IMAGE_HEIGHT))

    gravity = 0.8
    jump_speed = -14
    velocity_y = 0
    is_jumping = False
    ground_y = 400

    obstacle1 = pygame.Rect(600, 400, 50, 50)  # x, y, width, height
    obstacle2 = pygame.Rect(100, 400, 50, 50)
    obstacles = [obstacle1, obstacle2]

    while True:
        clock.tick(60)  # set framerate

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT]:
            alien.x -= 2
        if pressed_keys[pygame.K_RIGHT]:
            alien.x += 2
        if pressed_keys[pygame.K_UP]:
            if not is_jumping:
                velocity_y = jump_speed
                is_jumping = True

        # apply gravity
        velocity_y += gravity
        alien.y += velocity_y

        # Alien rectangle for collision detection
        on_obstacle = False
        for obstacle in obstacles:
            alien_rect = pygame.Rect(alien.x, alien.y, IMAGE_WIDTH, IMAGE_HEIGHT)
            if alien_rect.colliderect(obstacle) and velocity_y >= 0:
                # check if landing from above
                if alien_rect.bottom >= obstacle.top and alien_rect.bottom - velocity_y < obstacle.top + 5:
                    alien.y = obstacle.top - IMAGE_HEIGHT
                    velocity_y = 0
                    is_jumping = False
                    on_obstacle = True
                    break

        # check if on the ground
        if alien.y >= ground_y and not on_obstacle:
            alien.y = ground_y
            velocity_y = 0
            is_jumping = False

        # draw everything
        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, "green", obstacle1)
        pygame.draw.rect(screen, "green", obstacle2)
        alien.draw()
        pygame.display.update()


main()