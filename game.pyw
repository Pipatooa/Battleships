import json
import os
import queue
import sys

# Enables importing of packages from local folder
# Slower, but allows running without install
sys.path.append(os.path.abspath(os.path.join(".", "packages")))

import pygame

import vars

from objects.network import Network

from objects.board import Board
from objects.user import User

from objects.mixer import Mixer
from objects.screen import Screen
from objects.theme import Theme

from screens.create_game_menu import CreateGameMenu
from screens.game_screen import GameScreen
from screens.host_screen import HostScreen
from screens.join_menu import JoinMenu
from screens.main_menu import MainMenu


class Game:
    def __init__(self):
        self.running = True
        self.event_queue = queue.Queue()

        self.current_menu = None

        # Game ID
        self.id = None

        # Game info
        self.board_size = None
        self.ship_lengths = None

        self.quickfire = None

        # Users
        self.local_player = None
        self.other_player = None

    def create_game(self, id, board_size, ship_lengths, quickfire):
        """
        Create a new game
        :param id: int
        :param board_size: int
        :param ship_lengths: [int length, int length, ...]
        :param quickfire: bool
        """

        # Game ID
        self.id = id

        # Game info
        self.board_size = board_size
        self.ship_lengths = ship_lengths
        self.quickfire = quickfire

        self.local_player = User(Board(self.board_size, self.ship_lengths))
        self.other_player = User(Board(self.board_size, self.ship_lengths))

        vars.screen.calc_board_spacing(self.board_size)

    def run(self):
        """
        Run the game
        """

        while True:
            self.current_menu.run()

    def set_screen(self, name):
        """
        Sets the current screen to be displayed
        :param name: str
        """

        if name == "main_menu":
            self.current_menu = MainMenu()
        elif name == "create_game_menu":
            self.current_menu = CreateGameMenu()
        elif name == "host_screen":
            self.current_menu = HostScreen()
        elif name == "join_menu":
            self.current_menu = JoinMenu()
        elif name == "game_screen":
            self.current_menu = GameScreen()


# Main
pygame.init()

with open(os.path.join(".", "options.json")) as file:
    vars.options = json.load(file)

vars.game = Game()
vars.network = Network()
vars.mixer = Mixer()

with open(os.path.join(".", "themes", vars.options["theme"])) as file:
    theme = Theme(**json.load(file))

    vars.screen = Screen()
    vars.screen.set_theme(theme)

vars.game.current_menu = MainMenu()
vars.game.run()
