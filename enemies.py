import pygame
import sys


class Badguy:
    def __init__(self, screen, x, y, image_height, image_width, left_running_filename, right_running_filename):
        self.screen = screen
        self.x = x
        self.y = y
        self.speed_x = 2
        self.image_height = 100
        self.image_width = 56
        self.l_walk_frames = [pygame.image.load(f) for f in left_running_filename]
        self.l_walk_frames = [pygame.transform.scale(img, (self.image_width, self.image_height)) for img in self.l_walk_frames]
        self.r_walk_frames = [pygame.image.load(f) for f in left_running_filename]
        self.r_walk_frames = [pygame.transform.scale(img, (self.image_width, self.image_height)) for img in self.l_walk_frames]
        self.l_walk_frames = [pygame.transform.scale(pygame.image.load(f), (self.image_width, self.image_height)) for f in left_running_filename]
        self.r_walk_frames = [pygame.transform.scale(pygame.image.load(f), (self.image_width, self.image_height)) for f in right_running_filename]
        self.walk_frames = self.r_walk_frames #if self.speed_x > 0 else self.l_walk_frames
        self.current_frame = 0
        self.animation_delay = 10
        self.frame_count = 0

        #self.l_run = pygame.image.load(left_running_filename)
        #self.r_run = pygame.image.load(right_running_filename)
        #self.l_run = pygame.transform.scale(self.l_run, (self.image_width, self.image_height))
        #self.r_run = pygame.transform.scale(self.r_run, (self.image_width, self.image_height))
        #self.walk_images = [
            #pygame.image.load("First_Move_Left.png"),
            #pygame.image.load("Second_Move_Left.png"),
            #pygame.image.load("Third_Move_Left.png"),
            #pygame.image.load("Fourth_Move_Left.png")


        # Scale all walking images:
        #self.walk_images = [pygame.transform.scale(img, (self.image_width, self.image_height)) for img in
                            #self.walk_images]

        self.current_image = 0  # Current frame index
        self.animation_delay = 10  # Frames to wait before switching image
        self.frame_count = 0  # Counter to track frame changes

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.image_width, self.image_height)

    def check_collision(self):
        return pygame.Rect(self.x, self.y, self.image_width, self.image_height)

    def animate(self):
        self.frame_count += 1
        self.animation_delay = 10
        if self.frame_count >= self.animation_delay:
            self.frame_count = 0
            self.current_frame = ((self.current_frame + 1) % len(self.walk_frames))

    def move(self, obstacles):
        self.x += self.speed_x

        for obstacle in obstacles:
            if self.get_rect().colliderect(obstacle):
                self.speed_x *= -1

                if self.speed_x > 0:
                    self.walk_frames = self.r_walk_frames
                else:
                    self.walk_frames = self.l_walk_frames
                break

        self.animate()

    def draw(self):
        #l_run = pygame.transform.scale(self.l_run, (self.image_width, self.image_height))
        #self.screen.blit(l_run, (self.x, self.y))
        current_image = self.walk_frames[self.current_frame]
        self.screen.blit(current_image, (int(self.x), self.y))

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
    clock = pygame.time.Clock()

    left_frames = ["First_Move_Left.png", "Second_Move_Left.png", "Third_Move_Left.png", "Fourth_Move_Left.png"]
    right_frames = ["First_Move_Right.png", "Second_Move_Right.png", "Third_Move_Right.png", "Fourth_Move_Right.png"]

    character = Badguy(screen, 400, 400, 100, 56, left_frames, right_frames)

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
        clock.tick(60)


# Testing the classes
# click the green arrow to the left or run "Current File" in PyCharm to test this class
if __name__ == "__main__":
    test_character()
    main()
