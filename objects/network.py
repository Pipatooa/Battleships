import secrets
import time

import requests

import vars
import states

from objects.thread import ThreadedTask


class Network:
    """
    Handles battleships network functions
    """

    def __init__(self):
        self.session = requests.session()
        self.session.trust_env = False

        self.token = secrets.token_hex(32)
        self.connected = False

    def event_listen(self, game_id):
        """
        Listens for game events
        """

        global vars
        while self.connected == game_id:

            # Query server
            try:
                event = self.session.post(vars.options["server_address"], json={
                    "request": "get_event",
                    "token": self.token,
                    "id": vars.game.id
                }).json()
            except requests.exceptions.ConnectionError:
                if self.connected == game_id:
                    vars.state = states.GAME_OVER
                    vars.substate = states.LOST_CONNECTION

                return

            # Check if query was valid
            if not event["valid"]:
                continue

            # Handle various game events and update states appropriately
            if event["event"] == "player_joined":
                vars.state = states.SETUP
                vars.substate = states.AWAITING_READY

                vars.game.set_screen("game_screen")

            elif event["event"] == "game_started":
                if event["turn"]:
                    vars.state = states.FIRING
                    vars.substate = states.AWAITING_INPUT
                else:
                    vars.state = states.RECEIVING_FIRE
                    vars.substate = states.AWAITING_INPUT

            elif event["event"] == "received_fire":
                # Update board and player info
                if event["hit"]:
                    vars.game.local_player.board.set_hit(event["pos"])
                    vars.game.other_player.score += 1
                else:
                    vars.game.local_player.board.set_miss(event["pos"])

                # Set ship to be sunk if appropriate
                if event["sunk_ship"]:
                    id = event["sunk_ship"]["id"]

                    vars.game.local_player.board.ships[id].sunk = True

                # Update states
                if not event["hit"] or not vars.game.quickfire:
                    vars.state = states.FIRING
                    vars.substate = states.AWAITING_INPUT

                # Play sounds
                if event["hit"] and event["sunk_ship"]:
                    vars.mixer.play_sound("sunk")
                elif event["hit"]:
                    vars.mixer.play_sound("hit")
                else:
                    vars.mixer.play_sound("miss")

            elif event["event"] == "game_over":
                vars.state = states.GAME_OVER

                for index, ship in enumerate(event["revealed_ships"]):
                    vars.game.other_player.board.ships[index].set_pos(ship["pos"], ship["axis"])

                if event["disconnect"]:
                    vars.substate = states.DISCONNECT
                elif event["winner"]:
                    vars.substate = states.WON
                else:
                    vars.substate = states.LOST

                self.connected = False

    def keep_alive(self, game_id):
        """
        Keeps game connection alive
        """

        global vars
        while self.connected == game_id:

            # Query server
            try:
                self.session.post(vars.options["server_address"], json={
                    "request": "keep_alive",
                    "token": self.token,
                    "id": vars.game.id
                })
            except requests.exceptions.ConnectionError:
                vars.state = states.GAME_OVER
                vars.substate = states.LOST_CONNECTION
                return

            time.sleep(1)

    def host_game(self, board_size, ship_lengths, quickfire):
        """
        Host a new battleships game
        :param board_size: int
        :param ship_lengths: [int length, int length, ...]
        :param quickfire: bool
        """

        # Query server
        try:
            game_data = self.session.post(vars.options["server_address"], json={
                "request": "host_game",
                "token": self.token,
                "board_size": board_size,
                "ship_lengths": ship_lengths,
                "quickfire": quickfire
            }).json()
        except requests.exceptions.ConnectionError as e:
            print(e)
            vars.substate = states.CONNECTION_FAILED
            return

        # Check if query was valid
        if not game_data["valid"]:
            vars.substate = states.INVALID_GAME_SETTINGS
            return

        # Create a local game instance and wait on host_screen until user join
        vars.game.create_game(game_data["id"], board_size, ship_lengths, quickfire)
        vars.game.set_screen("host_screen")

        # Start event_listen and keep_alive threads
        self.connected = game_data["id"]

        ThreadedTask(self.event_listen, game_data["id"]).start()
        ThreadedTask(self.keep_alive, game_data["id"]).start()

    def join_game(self, id):
        """
        Join a battleships game
        :param id: int
        :return:
        """

        # Query server
        try:
            game_data = self.session.post(vars.options["server_address"], json={
                "request": "join_game",
                "token": self.token,
                "id": id
            }).json()
        except requests.exceptions.ConnectionError:
            vars.substate = states.CONNECTION_FAILED
            return

        # Check if query was valid
        if not game_data["valid"]:
            vars.substate = states.INVALID_GAME_ID
            return

        # Create a local game instance based on data sent back from server
        vars.game.create_game(
            id,
            game_data["board_size"],
            game_data["ship_lengths"],
            game_data["quickfire"]
        )

        # Set screen and states
        vars.game.set_screen("game_screen")

        vars.state = states.SETUP
        vars.substate = states.AWAITING_READY

        # Start event_listen and keep_alive threads
        self.connected = id

        ThreadedTask(self.event_listen, id).start()
        ThreadedTask(self.keep_alive, id).start()

    def disconnect(self):
        """
        Kills event_listen and keep_alive processes
        """

        self.connected = False

    def set_ready(self):
        """
        Sets the player as ready and sends ship data to server
        """

        # Query server
        try:
            response = self.session.post(vars.options["server_address"], json={
                "token": self.token,
                "request": "set_ready",
                "id": vars.game.id,
                "ship_data": [ship.get_position_info() for ship in vars.game.local_player.board.ships]
            }).json()
        except requests.exceptions.ConnectionError:
            vars.state = states.GAME_OVER
            vars.substate = states.LOST_CONNECTION
            return

        # Check if query was valid
        if not response["valid"]:
            return

        # Update state
        vars.substate = states.AWAITING_START

    def fire(self, pos):
        """
        Fires at the enemy board
        :param pos: (int x, int y)
        """

        # Query server
        try:
            response = self.session.post(vars.options["server_address"], json={
                "token": self.token,
                "request": "fire",
                "id": vars.game.id,
                "pos": pos
            }).json()
        except requests.exceptions.ConnectionError:
            vars.state = states.GAME_OVER
            vars.substate = states.LOST_CONNECTION
            return

        # Check if query was valid
        if not response["valid"]:
            return

        # Update board and player info
        if response["hit"]:
            vars.game.other_player.board.set_hit(pos)
            vars.game.local_player.score += 1
        else:
            vars.game.other_player.board.set_miss(pos)

        # Show position of sunk ship
        if response["sunk_ship"]:
            id = response["sunk_ship"]["id"]

            vars.game.other_player.board.ships[id].set_pos(tuple(response["sunk_ship"]["pos"]),
                                                           response["sunk_ship"]["axis"])

            vars.game.other_player.board.ships[id].sunk = True

        # Play sounds
        if response["hit"] and response["sunk_ship"]:
            vars.mixer.play_sound("sunk")
        elif response["hit"]:
            vars.mixer.play_sound("hit")
        else:
            vars.mixer.play_sound("miss")

        # Update states
        if all(ship.sunk for ship in vars.game.other_player.board.ships):
            return
        elif not response["hit"] or not vars.game.quickfire:
            vars.state = states.RECEIVING_FIRE
            vars.substate = None
        else:
            vars.substate = states.AWAITING_INPUT
