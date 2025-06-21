from Alien import Alien
import pygame
import sys
import my_character
import random
import time

def main():
    # turn on pygame
    pygame.init()

    # create a screen
    pygame.display.set_caption("Planet-8 Studios")
    # TODO: Change the size of the screen as you see fit!
    screen = pygame.display.set_mode((640, 480))
    # creates a Character from the my_character.py file
    character = my_character.Character(screen, 100, 100)

    # let's set the framerate
    clock = pygame.time.Clock()

    alien = Alien(screen, 20, 400, "standing_sprite.png", "left_running.png", "left_lunging.png", "right_running.png", "right_lunging.png")
    IMAGE_HEIGHT = 80
    IMAGE_WIDTH = 56

    alien.stand = pygame.transform.scale(alien.stand, (IMAGE_WIDTH, IMAGE_HEIGHT))

    while True:
        clock.tick(60)  # this sets the framerate of your game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # TODO: Add you events code
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT]:
            alien.x = alien.x-2
        if pressed_keys[pygame.K_RIGHT]:
            alien.x = alien.x+2
        if pressed_keys[pygame.K_UP]:
            alien.y = alien.y-2
        if pressed_keys[pygame.K_DOWN]:
            alien.y = alien.y+2
        # TODO: Fill the screen with whatever background color you like!
        screen.fill((255, 255, 255))

        # draws the character every frame
        alien.draw()

        # TODO: Add your project code

        # don't forget the update, otherwise nothing will show up!
        pygame.display.update()


main()