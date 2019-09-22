import ctypes
import platform

from functools import lru_cache

import pygame

import vars


class Screen:
    """Object containing information about the current display

    Used by draw functions"""

    def __init__(self):
        # Constants
        self.FULLSCREEN = vars.options["fullscreen"]
        self.FRAMERATE = vars.options["framerate"]
        self.DEFAULT_SIZE = (vars.options["resolution_x"], vars.options["resolution_y"])

        # If running Windows, disable high DPI scaling
        if platform.system() == "Windows":
            ctypes.windll.user32.SetProcessDPIAware()

        # Units for drawing the board to the screen
        self.LAST_BOARD_SIZE = None

        self.rescale_window(self.DEFAULT_SIZE, self.FULLSCREEN)

        # Theme to be used for screen drawing
        self.theme = None

        # Pygame
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("Battleships")
        pygame.display.set_icon(pygame.image.load("assets/icon.ico"))

        pygame.font.init()

    def rescale_window(self, size, fullscreen):
        """
        Rescale the window to size
        :param size: (int width, int height)
        """

        if fullscreen is None:
            fullscreen = self.FULLSCREEN

        self.FULLSCREEN = fullscreen

        if self.FULLSCREEN:
            size = pygame.display.list_modes()[0]
            self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.HWACCEL)
        else:
            self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)

        self.SIZE = size
        self.WIDTH, self.HEIGHT = self.SIZE
        self.MID = (self.WIDTH / 2, self.HEIGHT / 2)

        # Units for drawing to the screen
        self.UNIT = min(self.SIZE)
        self.BORDER_SIZE = self.UNIT / 20
        self.MARGIN_SIZE = int(self.UNIT / 300)

        # Font settings
        self.FONT_SCALE = self.UNIT / 1000

        # Force text to be rescaled
        self.render_text.cache_clear()

        if self.LAST_BOARD_SIZE:
            self.calc_board_spacing(self.LAST_BOARD_SIZE)

    def toggle_fullscreen(self):
        """
        Toggles fullscreen mode
        """

        if self.FULLSCREEN:
            self.rescale_window(self.DEFAULT_SIZE, False)
        else:
            self.rescale_window(self.DEFAULT_SIZE, True)

    def calc_board_spacing(self, board_size):
        """
        Calculates spacing for boards on screen
        :param board_size: int
        """

        self.LAST_BOARD_SIZE = board_size

        self.CELL_SIZE = int(((vars.screen.UNIT - vars.screen.BORDER_SIZE * 3) / 2 - (board_size + 1) * self.MARGIN_SIZE) / board_size)
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
