import queue
import json
import os
import sys

# Enables importing of packages from local folder
sys.path.append(os.path.join(".", "packages"))

import pygame

import vars

from network.network import Network

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

        # Game info
        self.BOARD_SIZE = None
        self.SHIP_LENGTHS = None

        self.ALLOW_EXTRA_TURN_ON_HIT = None

        # Users
        self.local_player = None
        self.other_player = None

    def create_game(self, board_size, ship_lengths, allow_extra_turn_on_hit, other_socket):
        """
        Create a new game
        :param board_size: int
        :param ship_lengths: [int length, int length, ...]
        :param allow_extra_turn_on_hit: bool
        :param other_socket: socket - other user
        """

        self.BOARD_SIZE = board_size
        self.SHIP_LENGTHS = ship_lengths
        self.ALLOW_EXTRA_TURN_ON_HIT = allow_extra_turn_on_hit

        self.local_player = User(Board(self.BOARD_SIZE, self.SHIP_LENGTHS))
        self.other_player = User(Board(self.BOARD_SIZE, self.SHIP_LENGTHS), other_socket)

        vars.screen.calc_board_spacing(self.BOARD_SIZE)

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

vars.game = Game()
vars.network = Network()
vars.mixer = Mixer()

with open("theme.json") as file:
    theme = Theme(**json.load(file))

    vars.screen = Screen()
    vars.screen.set_theme(theme)

vars.game.current_menu = MainMenu()
vars.game.run()
