import random
import queue

import states
import vars

from network.client import ClientNetwork
from network.host import HostNetwork

from objects.thread import ThreadedTask


class Network:
    def __init__(self):
        self.network = None

        self.ready = queue.Queue()

    def join_game(self, host_ip):
        """Joins a game and sends name to host and retrieves game information"""

        # Create network object and connect
        try:
            self.network = ClientNetwork(host_ip)
            self.network.connect()
        except:
            vars.substate = states.FAILED
            return

        # Receive game data and name from host
        board_size, ship_lengths, allow_extra_turn_on_hit = self.network.recv(self.network.hostsocket)

        # Create local game instance
        vars.game.create_game(board_size, ship_lengths, allow_extra_turn_on_hit, self.network.hostsocket)

        vars.state = states.SETUP
        vars.substate = states.AWAITING_READY

        vars.game.set_screen("game_screen")

        # Wait for local player to be ready
        self.ready.get()
        self.network.send(self.network.hostsocket, True)

        # Wait for other player to be ready
        self.network.recv(self.network.hostsocket)

        # Get who is starting from the host
        starting = self.network.recv(self.network.hostsocket)

        # Determine whether to fire or receive fire
        if starting == "client":
            vars.state = states.FIRING
            vars.substate = states.AWAITING_INPUT
        else:
            vars.state = states.RECEIVING_FIRE
            vars.substate = None
            ThreadedTask(self.receive_fire).start()

    def host_game(self, board_size, ship_lengths, allow_extra_turn_on_hit):
        """
        Hosts a game and sends game information to the connecting client
        """

        # Create network object and connect
        try:
            self.network = HostNetwork()
            self.network.connect()
        except:
            vars.substate = states.FAILED

        vars.game.set_screen("host_screen")

        # Wait for a connection from client
        client_socket, address = self.network.accept()

        # Send game data to client
        self.network.send(client_socket, (
            board_size,
            ship_lengths,
            allow_extra_turn_on_hit
        ))

        # Create local game instance
        vars.game.create_game(board_size, ship_lengths, allow_extra_turn_on_hit, client_socket)

        vars.state = states.SETUP
        vars.substate = states.AWAITING_READY

        vars.game.set_screen("game_screen")

        # Wait for other player to be ready
        self.network.recv(client_socket)

        # Wait for local player to be ready
        self.ready.get()
        self.network.send(client_socket, True)

        # Decide who is starting the game and send to client
        starting = random.choice(["host", "client"])
        self.network.send(client_socket, starting)

        # Determine whether to fire or receive fire
        if starting == "host":
            vars.state = states.FIRING
            vars.substate = states.AWAITING_INPUT
        else:
            vars.state = states.RECEIVING_FIRE
            vars.substate = None
            ThreadedTask(self.receive_fire).start()

    def set_ready(self):
        """
        Set the player as being ready
        """

        self.ready.put(True)

    def fire(self, pos):
        """
        Fire at enemy board at pos
        :param pos: (int, int)
        """

        # Send data to other player
        self.network.send(vars.game.other_player.socket, {
            "event": "fire",
            "value": pos
        })

        # Receive response from other player
        hit_data = self.network.recv(vars.game.other_player.socket)

        """Example Response
            {
                "hit": 2,
                "ship_id": 3,
                "ship": Ship()
            }
            """

        hit = hit_data["hit"]

        # Set enemy board to reflect outcome
        if hit:
            vars.game.other_player.board.set_hit(pos)
        else:
            vars.game.other_player.board.set_miss(pos)

        # If ship has been sunken, update enemy ship data
        if hit == 2:
            index = hit_data["ship_id"]
            vars.game.other_player.board.ships[index] = hit_data["ship"]

        # Update player score and play sounds
        if hit:
            vars.game.local_player.score += 1

            if hit == 2:
                vars.mixer.play_sound("sunk")
            else:
                vars.mixer.play_sound("hit")
        else:
            vars.mixer.play_sound("miss")

        # Check for loss
        if all(ship.sunk for ship in vars.game.other_player.board.ships):
            vars.state = states.GAME_OVER
            vars.substate = states.WON

            self.reveal_ships()

        # If extra turn is allowed, fire again
        elif vars.game.ALLOW_EXTRA_TURN_ON_HIT and hit:
            vars.substate = states.AWAITING_INPUT

        # Otherwise, wait for enemy fire
        else:
            vars.state = states.RECEIVING_FIRE
            vars.substate = None
            ThreadedTask(self.receive_fire).start()

    def receive_fire(self):
        """Wait for enemy to fire and return relevant information to enemy

            Also updates relevant objects"""

        # Wait for data from other player
        data = self.network.recv(vars.game.other_player.socket)

        """Example Data
            {
                "event": "fire",
                "value": (3, 4)
            }
        """

        # Unpack pos
        pos = data["value"]

        # Check whether a ship has been hit
        for index, ship in enumerate(vars.game.local_player.board.ships):

            hit = ship.check_hit(pos)

            if not hit:
                continue

            # Otherwise, set as hit
            vars.game.local_player.board.set_hit(pos)

            # If ship has been sunk, return index of sunken ship
            if ship.sunk:
                hit_data = {
                    "hit": 2,
                    "ship_id": index,
                    "ship": ship
                }
            else:
                hit_data = {
                    "hit": 1
                }

            break  # Break out of loop if hit

        # If not a hit save to board as a miss
        else:
            vars.game.local_player.board.set_miss(pos)

            hit_data = {
                "hit": 0
            }

        # Send hit_data to enemy
        self.network.send(vars.game.other_player.socket, hit_data)

        hit = hit_data["hit"]

        # Update player score and play sounds
        if hit:
            vars.game.other_player.score += 1

            if hit == 2:
                vars.mixer.play_sound("sunk")
            else:
                vars.mixer.play_sound("hit")
        else:
            vars.mixer.play_sound("miss")

        # Check for loss
        if all(ship.sunk for ship in vars.game.local_player.board.ships):
            vars.state = states.GAME_OVER
            vars.substate = states.LOST

            self.receive_revealed_ships()

        # If extra turn is allowed, wait for fire
        elif vars.game.ALLOW_EXTRA_TURN_ON_HIT and hit:
            ThreadedTask(self.receive_fire).start()

        # Otherwise, fire
        else:
            vars.state = states.FIRING
            vars.substate = states.AWAITING_INPUT

    def reveal_ships(self):
        """
        Sends all ships to the other player in the event of a win
        """

        self.network.send(vars.game.other_player.socket, vars.game.local_player.board.ships)

    def receive_revealed_ships(self):
        """
        Receive all ships from the other player in the event of a loss
        """

        ships = self.network.recv(vars.game.other_player.socket)
        vars.game.other_player.board.ships = ships
