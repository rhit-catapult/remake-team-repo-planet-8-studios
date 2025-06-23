import pygame

class Alien:
    def __init__(self, screen, x, y, standing_filename, left_running_filename, left_lunging_filename, right_running_filename, right_lunging_filename):
        self.screen = screen
        self.x = x
        self.y = y
        self.direction = 'neutral'
        self.stand = pygame.image.load(standing_filename)
        self.l_run = pygame.image.load(left_running_filename)
        self.l_lung = pygame.image.load(left_lunging_filename)
        self.r_run = pygame.image.load(right_running_filename)
        self.l_lun = pygame.image.load(right_lunging_filename)

    def draw(self):
        """ Draws this sprite onto the screen. """
        #inserts hero at its position
        if self.direction == 'neutral':
            self.screen.blit(self.stand, (self.x, self.y))
        elif self.direction == 'left':
            self.screen.blit(self.l_run, (self.x, self.y))
        elif self.direction == 'right':
            self.screen.blit(self.r_run, (self.x, self.y))