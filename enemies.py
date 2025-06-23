import pygame
import sys


class Badguy:
    def __init__(self, screen: pygame.Surface, x, y, left_running_filename, right_running_filename, image_height, image_width):
        self.screen = screen
        self.x = x
        self.y = y
        self.speed_x = 0.5
        self.l_run = pygame.image.load(left_running_filename)
        self.r_run = pygame.image.load(right_running_filename)
        self.image_height = 100
        self.image_width = 56
        self.l_run = pygame.transform.scale(self.l_run, (self.image_width, self.image_height))
        self.r_run = pygame.transform.scale(self.r_run, (self.image_width, self.image_height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.image_width, self.image_height)

    def check_collision(self):
        return pygame.Rect(self.x, self.y, self.image_width, self.image_height)

    def move(self, obstacles):
        self.x += self.speed_x

        for obstacle in obstacles:
            if self.get_rect().colliderect(obstacle):
                self.speed_x *= -1
                break

    def draw(self):
        l_run = pygame.transform.scale(self.l_run, (self.image_width, self.image_height))
        self.screen.blit(l_run, (self.x, self.y))


def main(self):
    pygame.init()
    screen = pygame.display.set_mode((720, 560))
    pygame.display.set_caption("Planet-8 Studios")
    screen.fill("white")
    clock = pygame.time.Clock()



    badguy = Badguy(screen, 400, 400, "First_Move_Left.png", "First_Move_Right.png")
    image_height = 12
    image_width = 8
    #First_Move_Left = pygame.transform.scale(First_Move_Left, (IMAGE_WIDTH, IMAGE_HEIGHT))





# This function is called when you run this file, and is used to test the Character class individually.
# When you create more files with different classes, copy the code below, then
# change it to properly test that class
def test_character():
    # TODO: change this function to test your class
    screen = pygame.display.set_mode((720, 560))
    character = Badguy(screen, 400, 400, "First_Move_Left.png", "First_Move_Right.png", 12,8 )

    obstacle1 = pygame.Rect(600, 400, 50, 50)  # x, y, width, height
    obstacle2 = pygame.Rect(100, 400, 50, 50)
    obstacles = [obstacle1, obstacle2]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()




        screen.fill("white")
        character.draw()
        character.move(obstacles)
        pygame.draw.rect(screen, "green", obstacle1)
        pygame.draw.rect(screen, "green", obstacle2)

        pygame.display.update()


# Testing the classes
# click the green arrow to the left or run "Current File" in PyCharm to test this class
if __name__ == "__main__":
    test_character()
    main()
