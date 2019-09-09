import ctypes
import platform
import pygame

from functools import lru_cache


class Screen:
    """Object containing information about the current display

    Used by draw functions"""

    def __init__(self):
        # Constants
        self.FULLSCREEN = True
        self.FRAMERATE = 30

        if self.FULLSCREEN:
            self.SIZE = pygame.display.list_modes()[0]
        else:
            self.SIZE = (1500, 1500)

        self.WIDTH, self.HEIGHT = self.SIZE

        self.MID = (self.WIDTH / 2, self.HEIGHT / 2)

        # Units for drawing to the screen
        self.UNIT = min(self.SIZE)
        self.BORDER_SIZE = self.UNIT / 20
        self.MARGIN_SIZE = int(self.UNIT / 300)

        # Font settings
        self.FONT_SCALE = self.UNIT / 1000

        # Theme to be used for screen drawing
        self.theme = None

        # Units for drawing the board to the screen
        self.CELL_SIZE = None
        self.CELL_DOT_SIZE = None
        self.BOARD_SIZE = None

        # Pygame
        self.clock = pygame.time.Clock()

        # If running Windows, disable high DPI scaling
        if platform.system() == "Windows":
            ctypes.windll.user32.SetProcessDPIAware()

        if self.FULLSCREEN:
            self.screen = pygame.display.set_mode(self.SIZE, pygame.FULLSCREEN|pygame.HWACCEL)
        else:
            self.screen = pygame.display.set_mode(self.SIZE)

        pygame.display.set_caption("Battleships")
        pygame.display.set_icon(pygame.image.load("assets/icon.ico"))

        pygame.font.init()

    def rescale_window(self, size):
        """
        Rescale the window to size
        :param size: (int width, int height)
        """

    def calc_board_spacing(self, board_size):
        """
        Calculates spacing for boards on screen
        :param board_size: int
        """

        self.CELL_SIZE = int(((self.UNIT - self.BORDER_SIZE * 3) / 2 - (board_size + 1) * self.MARGIN_SIZE) / board_size)
        self.CELL_DOT_SIZE = int(self.CELL_SIZE / 4)

        self.BOARD_SIZE = self.CELL_SIZE * board_size + self.MARGIN_SIZE * (board_size + 1)

    def set_theme(self, theme):
        """Sets the theme"""

        self.theme = theme

    @lru_cache(maxsize=32)
    def get_font(self, name, size):
        """Returns a font object given a name and size"""

        return pygame.font.Font(name, size)

    @lru_cache(maxsize=32)
    def render_text(self, size, text, text_color):
        """Returns a text object given a name, size and text to render"""

        # Adjust size of font for screen size
        size = int(self.FONT_SCALE * size)

        # Get font
        font = self.get_font(self.theme.FONT, size)

        # Render text
        text = font.render(text, True, text_color)

        return text

    def draw(self):
        """Draws to the screen"""

        self.clock.tick(self.FRAMERATE)
        pygame.display.flip()

        # print(self.clock.get_fps())
