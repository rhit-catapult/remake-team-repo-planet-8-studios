import pygame
import sys


class Badguy:
    def __init__(self, screen, x, y, image_height, image_width, left_running_filenames, right_running_filenames):
        # left = ['enemy_left1', 'enemy_left2']
        # right = ["enemy_right1', 'enemy_right2']
        self.screen = screen
        self.x = x
        self.y = y
        self.speed_x = 2
        self.speed_y = 2
        self.gravity = 1
        self.image_height = image_height
        self.image_width = image_width

        self.l_walk_frames = [
            pygame.transform.scale(pygame.image.load(f), (self.image_width, self.image_height))
            for f in left_running_filenames
        ]
        self.r_walk_frames = [
            pygame.transform.scale(pygame.image.load(f), (self.image_width, self.image_height))
            for f in right_running_filenames
        ]

        self.walk_frames = self.r_walk_frames
        self.current_frame = 0
        self.animation_delay = 10
        self.frame_count = 0

    def get_rect(self):
        return pygame.Rect(int(self.x), self.y, self.image_width, self.image_height)

    def animate(self):
        self.frame_count += 1
        if self.frame_count >= self.animation_delay:
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1) % len(self.walk_frames)

    def move(self, obstacles):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity

        for platform in obstacles:
            if self.get_rect().colliderect(platform.rect):
                if (self.speed_y > 0 and self.get_rect().bottom > platform.rect.top and
                        self.get_rect().bottom < platform.rect.top + 20):
                    self.get_rect().bottom = platform.rect.top - 20
                    self.speed_y = 0
                    on_ground = True

        for obstacle in obstacles:
            if (self.get_rect().colliderect(obstacle.get_rect()) and
                    abs(self.get_rect().bottom - obstacle.get_rect().top)) > 20:
                self.speed_x *= -1
                if self.speed_x > 0:
                    self.walk_frames = self.r_walk_frames
                else:
                    self.walk_frames = self.l_walk_frames
                break

        self.animate()
        if 0 > self.x  or self.x > self.screen.get_width() - self.image_width:
            self.speed_x *= -1

    def draw(self):
        if self.speed_x > 0:
            self.walk_frames = self.r_walk_frames
        if self.speed_x < 0:
            self.walk_frames = self.l_walk_frames
        current_image = self.walk_frames[self.current_frame]
        self.screen.blit(current_image, (int(self.x), self.y))

    def frames(self):
        left_frames = self.l_walk_frames[self.current_frame]
        right_frames = self.r_walk_frames[self.current_frame]

def astronaut():
    pygame.init()
    screen = pygame.display.set_mode((720, 560))
    clock = pygame.time.Clock()

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

    character = Badguy(screen, 400, 400, 100, 56, left_frames, right_frames)

    obstacle1 = pygame.Rect(600, 400, 50, 50)
    obstacle2 = pygame.Rect(100, 400, 50, 50)
    obstacles = [obstacle1, obstacle2]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill("white")
        character.move(obstacles)
        character.draw()
        pygame.draw.rect(screen, "green", obstacle1)
        pygame.draw.rect(screen, "green", obstacle2)

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    astronaut()
