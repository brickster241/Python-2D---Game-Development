import math, os, random
from collections import deque
import pygame
from pygame.locals import *

FPS = 60
ANIMATION_SPEED = 0.24
WIN_WIDTH = 284 * 2
WIN_HEIGHT = 512


class Bird(pygame.sprite.Sprite):
    """
    Represents the Bird controlled by the player

    Attributes:
        X, Y : Bird's x, y coordinates.
        ms_to_climb: The number of ms left to climb, where a complete climb lasts Bird.CLIMB_DURATION ms.

    Constants:
    WIDTH, HEIGHT : The width and height, in pixels, of the bird's image.
    SINK_SPEED : With which speed, in pixels per ms, the bird falls down freely.
    CLIMB_SPEED: With which speed, in pixels per millisecond, the bird ascends in one second while climbing, on average.
      See also the Bird.update docstring.
    CLIMB_DURATION: The number of milliseconds it takes the bird to execute a complete climb.

    """
    WIDTH = HEIGHT = 50
    SINK_SPEED = 0.18
    CLIMB_SPEED = 0.3
    CLIMB_DURATION = 333.3

    def __init__(self, x, y, ms_to_climb, images):
        super(Bird, self).__init__()
        self.X, self.Y = x, y
        self.ms_to_climb = ms_to_climb
        self._wing_up, self._wing_down = images
        self._mask_wing_up = pygame.mask.from_surface(self._wing_up)
        self._mask_wing_down = pygame.mask.from_surface(self._wing_down)

    @property
    def image(self):
        """Get a Surface containing this bird's image."""
        if pygame.time.get_ticks() % 500 <= 250:
            return self._wing_up
        else:
            return self._wing_down

    @property
    def mask(self):
        """
        Get a bitmask for use in collision detection.

        The bitmask excludes all pixels in self.image with a
        transparency greater than 127.
        """
        if pygame.time.get_ticks() % 500 <= 250:
            return self._mask_wing_up
        else:
            return self._mask_wing_down

    @property
    def rect(self):
        """Get the bird's position , width , height, as a pygame.Rect """
        return Rect(self.X, self.Y, Bird.WIDTH, Bird.HEIGHT)

    def update(self, delta_frames=1):
        """
        Update the bird's position
        One complete climb is CLIMB_DURATION ms, during which the bird ascends with an average of CLIMB_SPEED px/ms
        This Bird's ms_to_climb attribute will automatically decrease if > 0.
        delta_frames : The no. of frames elapsed since this method was last called.
        """
        if self.ms_to_climb > 0:
            frac_climb_done = 1 - self.ms_to_climb / Bird.CLIMB_DURATION
            self.Y -= (Bird.CLIMB_SPEED * frames_to_ms(delta_frames) * (1 - math.cos(frac_climb_done * math.pi)))
            self.ms_to_climb -= frames_to_ms(delta_frames)
        else:
            self.Y += Bird.SINK_SPEED * frames_to_ms(delta_frames)


class PipePair(pygame.sprite.Sprite):
    """
    Represents an obstacle.
    2 parts : Top Pipe, Bottom Pipe
    
    Attributes:
        X : X-coordinate of the pipe
        img : A pygame.Surface image which can be blit to display surface to display the PipePair
        mask : A bitmask which excludes all pixels in self.image with a transparency greater than 127.  
                This can be used for collision detection.
        top_pieces, bottom_pieces : No. of pieces , including the end piece, in top/bottom pipe
        
    Constants:
    WIDTH: The width, in pixels, of a pipe piece.  Because a pipe is only one piece wide, this is also the width
     of a PipePair's image.
    PIECE_HEIGHT: The height, in pixels, of a pipe piece.
    ADD_INTERVAL: The interval, in milliseconds, in between adding new pipes.
    """
    WIDTH = 80
    PIECE_HEIGHT = 32
    ADD_INTERVAL = 2000
    
    def __init__(self, pipe_end_img, pipe_body_img):
        super(PipePair, self).__init__()
        self.X = float(WIN_WIDTH - 1)
        self.score_counted = False
        
        # Very Important
        self.image = pygame.Surface((PipePair.WIDTH, WIN_HEIGHT), SRCALPHA)
        self.image.convert()
        # The 4th zero is for transparency
        self.image.fill((0, 0, 0, 0))
        # randomises the no. of body pieces of top and bottom
        total_pipe_body_pieces = int((WIN_HEIGHT - 3 * Bird.HEIGHT - 3 * PipePair.PIECE_HEIGHT) / PipePair.PIECE_HEIGHT)
        self.bottom_pieces = random.randint(1, total_pipe_body_pieces)
        self.top_pieces = total_pipe_body_pieces - self.bottom_pieces

        # bottom pipe
        for i in range(1, self.bottom_pieces + 1):
            piece_pos = (0, WIN_HEIGHT - i * PipePair.PIECE_HEIGHT)
            self.image.blit(pipe_body_img, piece_pos)
        bottom_pipe_end_y = WIN_HEIGHT - (self.bottom_pieces * PipePair.PIECE_HEIGHT)
        bottom_end_piece_pos = (0, bottom_pipe_end_y - PipePair.PIECE_HEIGHT)
        self.image.blit(pipe_end_img, bottom_end_piece_pos)

        # top pipe
        for i in range(self.top_pieces):
            self.image.blit(pipe_body_img, (0, i * PipePair.PIECE_HEIGHT))
        top_pipe_end_y = self.top_pieces * PipePair.PIECE_HEIGHT
        self.image.blit(pipe_end_img, (0, top_pipe_end_y))

        # compensate for added end pieces
        self.top_pieces += 1
        self.bottom_pieces += 1

        # for collision detection
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, delta_frames=1):
        """
        Update the PipePair's position.
        delta_frames: The number of frames elapsed since this method was last called.
        """
        self.X -= ANIMATION_SPEED * frames_to_ms(delta_frames)

    @property
    def rect(self):
        """ Get the rect which contains this PipePair."""
        return Rect(self.X, 0, PipePair.WIDTH, PipePair.PIECE_HEIGHT)

    @property
    def visible(self):
        return -PipePair.WIDTH < self.X < WIN_WIDTH

    def collides_with(self, bird):
        """
        Get whether the bird collides with a pipe in this PipePair.
        Arguments:
        bird: The Bird which should be tested for collision with this PipePair.
        """
        return pygame.sprite.collide_mask(self, bird)


def load_images():
    """
    Load all images required by the game and return a dict of them.
    """

    def load_image(img_file_name):
        """
        Return the loaded pygame image with the specified file name.

        This function looks for images in the game's images folder
        (./images/).  All images are converted before being returned to
        speed up blitting.

        Arguments:
        img_file_name: The file name (including its extension, e.g.
            '.png') of the required image, without a file path.
        """
        file_name = os.path.join('.', 'images', img_file_name)
        img = pygame.image.load(file_name)
        img.convert()
        return img

    return {'background': load_image('background.png'),
            'pipe-end': load_image('pipe_end.png'),
            'pipe-body': load_image('pipe_body.png'),
            # images for animating the flapping bird -- animated GIFs are
            # not supported in pygame
            'bird-wing-up': load_image('bird_wing_up.png'),
            'bird-wing-down': load_image('bird_wing_down.png')
            }


def frames_to_ms(frames, fps=FPS):
    """
    Convert frames to ms at the specified frame rate.
    """
    return (1000 * frames) / fps


def ms_to_frames(ms, fps=FPS):
    """
    Convert ms to frames at the specified frame rate.
    """
    return (fps * ms) / 1000


def main():

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("sounds/sound.mp3")
    pygame.mixer.music.set_volume(0.8)

    display_surface = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Pygame 2D - Flappy Bird")
    clock = pygame.time.Clock()
    score_font = pygame.font.SysFont(None, 32, bold=True)
    images = load_images()

    bird = Bird(WIN_WIDTH // 4, int(WIN_HEIGHT / 2 - Bird.HEIGHT / 2), 2,
                (images["bird-wing-up"], images["bird-wing-down"]))

    Pipes = deque()
    frame_clock = 0
    score = 0
    gameOver = False
    Pause = False
    while not gameOver:
        clock.tick(FPS)

        if not (Pause or frame_clock % ms_to_frames(PipePair.ADD_INTERVAL)):
            pipe_pair = PipePair(images["pipe-end"], images["pipe-body"])
            Pipes.append(pipe_pair)

        for event in pygame.event.get():
            if event.type == QUIT:
                gameOver = True
                break
            elif event.type == KEYUP and event.key in (K_PAUSE, K_p):
                Pause = not Pause
            elif event.type == KEYUP and event.key in (K_UP, K_RETURN, K_SPACE):
                bird.ms_to_climb = Bird.CLIMB_DURATION

        if Pause:
            continue

        # check collisions
        pipe_collision = any(pipe.collides_with(bird) for pipe in Pipes)
        if pipe_collision or 0 >= bird.Y or bird.Y >= WIN_HEIGHT - Bird.HEIGHT:
            pygame.mixer.music.load("sounds/gameOver.mp3")
            pygame.mixer.music.play()
            pygame.time.wait(1500)
            gameOver = True
        display_surface.blit(images["background"], (0, 0))
        display_surface.blit(images["background"], (WIN_WIDTH // 2, 0))

        while Pipes and not Pipes[0].visible:
            Pipes.popleft()

        for pipe in Pipes:
            pipe.update()
            display_surface.blit(pipe.image, pipe.rect)

        bird.update()
        display_surface.blit(bird.image, bird.rect)

        for pipe in Pipes:
            if pipe.X + PipePair.WIDTH < bird.X and not pipe.score_counted:
                pipe.score_counted = True
                score += 1
                pygame.mixer.music.play()
                if score % 5 == 0:
                    PipePair.ADD_INTERVAL = max(1750, PipePair.ADD_INTERVAL - 200)

        score_surface = score_font.render(str(score), True, (255, 255, 255))
        score_x = WIN_WIDTH / 2 - score_surface.get_width() / 2
        display_surface.blit(score_surface, (score_x, PipePair.PIECE_HEIGHT))

        pygame.display.flip()
        frame_clock += 1
    print('Game over! Score: %i' % score)
    pygame.quit()


if __name__ == '__main__':
    main()
