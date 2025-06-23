import pygame

class Platform:
    def __init__(self, screen, x, y, width, height, thickness):
        self.screen = screen
        self.x = x
        self.y = y

    def draw(self):
        """ Draws this sprite onto the screen. """
        #inserts platoform at its position
        def draw(self):
            """ Draws this sprite onto the screen. """
            # draws a platform
            pygame.draw.rect(self.screen, (255,0,0), (self.x, self.y, self.width, self.height), self.thickness)
