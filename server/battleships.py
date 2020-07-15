import queue
import random
import multiprocessing
import time
import threading
import types

# List of active games
games = {}

# Threading lock
lock = threading.Lock()


class Board:
    """Board object containing hit information

    Values:
    0 - Empty
    1 - Miss
    2 - Hit"""

    def __init__(self, size, ship_lengths):
        # Size of the board
        self.SIZE = size

        # Ships that are on the board
        self.ships = [Ship(index, length) for index, length in enumerate(ship_lengths)]

        # Reset the board
        self.board = [[0 for i in range(self.SIZE)] for i in range(self.SIZE)]

    def check_fired_at(self, pos):
        """
        Returns whether a board cell has already been fired at
        :param pos: (int x, int y)
        :return: bool
        """

        # Unpack pos
        x, y = pos

        return bool(self.board[x][y])

    def set_hit(self, pos):
        """Set board 'pos' on board to a hit"""

        # Unpack hit position
        x, y = pos

        # Update board location
        self.board[x][y] = 2

    def set_miss(self, pos):
        """Set board 'pos' on board to a miss"""

        # Unpack hit position
        x, y = pos

        # Update board location
        self.board[x][y] = 1

    def get_ships(self, show_not_sunk):
        """
        Returns JSON data for all ships on the board
        :param show_not_sunk: bool
        :return: [dict, dict, dict, ...]
        """

        return [ship.get_json(show_not_sunk) for ship in self.ships]


class Ship:
    """Ship object with length, position and hit information"""

    def __init__(self, id, length):
        # ID of ship
        self.id = id

        # Ship location validity
        self.collisions = []

        # Whether the ship has been sunk or not
        self.sunk = False

        # Length of the ship
        self.length = length

        self.x_length = None  # Ship must have axis
        self.y_length = None

        # Position Information
        self.pos = None
        self.axis = None

        # Where the ship has been hit
        # Left to right (+x), or top to bottom (+y)
        self.hits = [False for i in range(length)]

    def get_coords(self, pos=None):
        """Returns a list of tuples containing coordinates of every cell occupied by the ship"""

        if not pos:
            pos = self.pos

        # Return list of tuples
        if self.axis == "x":
            return [(pos[0] + i, pos[1]) for i in range(self.length)]

        else:
            return [(pos[0], pos[1] + i) for i in range(self.length)]

    def check_hit(self, pos):
        """
        Checks whether the ship has been hit when given hit position as a tuple and updates ship data accordingly
        """

        # Get coordinates of all cells occupied by ship
        cells = self.get_coords()

        # Check if pos is a part of the ship
        if pos not in cells:
            return {
                "hit": False,
                "sunk": False,
                "sunk_ship": None
            }

        # If part of ship, get index of hit location
        index = cells.index(pos)

        # Set hit location to be True
        self.hits[index] = True

        # If all ship locations are hit, set sunk and return sunken ship
        if all(self.hits):
            self.sunk = True

            return {
                "hit": True,
                "sunk_ship": self.get_json(True)
            }

        # Otherwise, return just hit
        return {
            "hit": True,
            "sunk_ship": None
        }

    def check_collisions(self, ships):
        """
        Checks if the ship is intersecting with another ship

        :param ships: [Ship(), Ship(), ...]
        :return: bool
        """

        for ship in ships:
            if ship == self:
                continue

            if any(pos in ship.get_coords() for pos in self.get_coords()):
                if ship not in self.collisions:
                    self.collisions.append(ship)
                    ship.collisions.append(self)
            else:
                if ship in self.collisions:
                    self.collisions.remove(ship)
                    ship.collisions.remove(self)

        return not self.collisions

    def set_pos(self, pos, axis):
        """
        Set the position of the ship
        :param pos: (int, int)
        :param axis: "x" / "y"
        """

        self.pos = pos
        self.axis = axis

        if self.axis == "x":
            self.x_length = self.length
            self.y_length = 1
        else:
            self.x_length = 1
            self.y_length = self.length

    def get_json(self, show_not_sunk):
        """
        Returns a JSON version of the ship object
        :param show_not_sunk: bool
        :return: dict
        """

        if show_not_sunk:
            return {
                "id": self.id,
                "sunk": self.sunk,
                "pos": self.pos,
                "axis": self.axis,
                "length": self.length
            }
        else:
            return {
                "id": self.id,
                "sunk": self.sunk,
                "pos": None,
                "axis": None,
                "length": None
            }


class SpecialQueue:
    """
    Special queue class
    """

    def __init__(self):
        self.queue = queue.Queue()

        self.closed = False

        self.lock = threading.Lock()

    def put(self, item):
        self.queue.put(item)

    def get(self):
        if self.lock.locked():
            return False

        self.lock.acquire()

        if self.closed:
            self.lock.release()
            return False

        event = self.queue.get()

        self.lock.release()
        return event

    def close(self):
        self.closed = True
        self.queue.put(None)


class User:
    """
    A user in a game
    """

    def __init__(self, board):
        # Token to validate user requests
        self.token = None

        # Last time that keep_alive request was sent
        self.keep_alive = time.time()

        # Game info
        self.ready = False
        self.board = board
        self.score = 0

        # Events that need to be passed to client
        self.event_queue = SpecialQueue()


class Game:
    """
    A battleships game instance
    """

    def __init__(self, id, board_size, ship_lengths, quickfire, host_token):
        # Game ID
        self.id = id

        # Game settings
        self.board_size = board_size
        self.ship_lengths = ship_lengths
        self.quickfire = quickfire

        # Whether this game is alive
        self.alive = True

        # Current game states
        self.joining = True
        self.readying = False
        self.in_game = False
        self.game_over = False

        self.winner = None

        # Who's turn it is
        self.current_turn = random.choice(["a", "b"])

        # Users
        self.user_a = User(Board(board_size, ship_lengths))
        self.user_b = User(Board(board_size, ship_lengths))

        # List of valid user tokens
        self.tokens = [host_token]

        # Set host token
        self.user_a.token = host_token

    def set_ready(self, token, ship_data):
        """
        Sets user with token as ready
        """

        if not self.readying:
            return {
                "valid": False
            }

        # Match token to user
        if self.user_a.token == token and not self.user_a.ready:
            user = self.user_a
            other_user = self.user_b
        elif self.user_b.token == token and not self.user_b.ready:
            user = self.user_b
            other_user = self.user_a
        else:
            return {
                "valid": False
            }

        # If number of ships differs
        if len(ship_data) != len(self.ship_lengths):
            return {
                "valid": False
            }

        for ship in ship_data:
            if type(ship) is not list:
                return {
                    "valid": False
                }

            if type(ship[0]) is not int or type(ship[1]) is not int or not (ship[2] == "x" or ship[2] == "y"):
                return {
                    "valid": False
                }

        # Set position of each ship
        for index, ship in enumerate(user.board.ships):
            ship.set_pos(ship_data[index][0:2], ship_data[index][2])

        # Make sure that ships are in valid positions
        for ship in user.board.ships:
            ship.check_collisions(user.board.ships)

            if ship.collisions:
                return {
                    "valid": False
                }

            if ship.pos[0] + ship.x_length - 1 >= self.board_size:
                return {
                    "valid": False
                }

            elif ship.pos[1] + ship.y_length - 1 >= self.board_size:
                return {
                    "valid": False
                }

            user.ready = True

        if user.ready and other_user.ready:
            self.readying = False
            self.in_game = True

            self.user_a.event_queue.put({
                "event": "game_started",
                "turn": self.current_turn == "a"
            })

            self.user_b.event_queue.put({
                "event": "game_started",
                "turn": self.current_turn == "b"
            })

        return {
            "valid": True
        }

    def process_fire(self, token, pos):
        """
        Process a fire request from a user
        """

        # Convert pos to a tuple
        pos = tuple(pos[0:2])

        if self.user_a.token == token and self.current_turn == "a":
            user = self.user_a
            other_user = self.user_b

            next_turn = "b"
        elif self.user_b.token == token and self.current_turn == "b":
            user = self.user_b
            other_user = self.user_a

            next_turn = "a"
        else:
            return {
                "valid": False
            }

        # Check if board cell is already occupied
        if other_user.board.check_fired_at(pos):
            return {
                "valid": False
            }

        # Check if any ships have been hit
        for ship in other_user.board.ships:
            hit_data = ship.check_hit(pos)

            if hit_data["hit"]:
                break

        # If hit, update score and board
        if hit_data["hit"]:
            user.score += 1
            other_user.board.set_hit(pos)

            if not self.quickfire:
                self.current_turn = next_turn
        else:
            self.current_turn = next_turn
            other_user.board.set_miss(pos)

        # Pass event to other user
        other_user.event_queue.put({
            "event": "received_fire",
            "pos": pos,
            "hit": hit_data["hit"],
            "sunk_ship": hit_data["sunk_ship"]
        })

        # If ship sunk check if somebody has won
        if hit_data["sunk_ship"]:
            if all(ship.sunk for ship in other_user.board.ships):
                self.current_turn = None

                user.event_queue.put({
                    "event": "game_over",
                    "disconnect": False,
                    "winner": True,
                    "revealed_ships": []
                })

                other_user.event_queue.put({
                    "event": "game_over",
                    "disconnect": False,
                    "winner": False,
                    "revealed_ships": user.board.get_ships(True)
                })

        # Return data
        return {
            "valid": True,
            "hit": hit_data["hit"],
            "sunk_ship": hit_data["sunk_ship"]
        }

    def check_alive(self):
        """
        Check whether this game should still be kept alive
        """

        if not self.alive:
            return

        if time.time() - self.user_a.keep_alive > 10:
            self.user_b.event_queue.put({
                "event": "game_over",
                "disconnect": True,
                "winner": None,
                "revealed_ships": self.user_a.board.get_ships(True)
            })

        if time.time() - self.user_a.keep_alive > 30:
            self.alive = False
            return

        if not self.joining:
            if time.time() - self.user_b.keep_alive > 10:
                self.user_a.event_queue.put({
                    "event": "game_over",
                    "disconnect": True,
                    "winner": None,
                    "revealed_ships": self.user_b.board.get_ships(True)
                })

            if time.time() - self.user_b.keep_alive > 30:
                self.alive = False
                return


def compare_dicts(a, b):
    """
    Compares 2 dictionaries to see if they follow the same format
    :param a: dict to reference
    :param b: dict to compare
    :return: True if all keys match and types of values match, otherwise False
    """

    if type(b) is not dict:
        return False

    if a.keys() != b.keys():
        return False

    for k, v in a.items():
        if type(v) is types.LambdaType:
            try:
                if not v(b[k]):
                    return False
            except:
                return False

        elif type(b[k]) is not v:
            return False

    return True


def handle_request(request):
    """
    Handle the request sent to the API
    """

    # Unpack request
    try:
        data = request.json
    except:
        return {
            "valid": False
        }

    if not data:
        return {
            "valid": False
        }

    if "token" not in data:
        return {
            "valid": False
        }

    token = data["token"]

    if "request" not in data:
        return {
            "valid": False
        }

    if data["request"] == "host_game":
        # Make sure that request format is valid
        if not compare_dicts({
            "request": str,
            "token": str,
            "board_size": lambda x: 0 < x,
            "ship_lengths": list,
            "quickfire": bool
        }, data):
            return {
                "valid": False
            }

        # Check number of ships
        if len(data["ship_lengths"]) > data["board_size"]:
            return {
                "valid": False
            }

        # Check if ship lengths are valid
        if any(type(length) is not int for length in data["ship_lengths"]):
            return {
                "valid": False
            }

        if not all(1 <= length <= data["board_size"] for length in data["ship_lengths"]):
            return {
                "valid": False
            }

        lock.acquire()

        # Create a random 4 digit game ID
        id = random.randint(1000, 9999)
        while id in games:
            id = random.randint(1000, 9999)

        # Create game
        games[id] = Game(id,
                         data["board_size"],
                         data["ship_lengths"],
                         data["quickfire"],
                         token)

        lock.release()
        return {
            "valid": True,
            "id": id
        }

    elif data["request"] == "join_game":

        lock.acquire()

        # Make sure that request format is valid
        if not compare_dicts({
            "request": str,
            "token": str,
            "id": lambda x: x in games
        }, data):
            lock.release()
            return {
                "valid": False
            }

        # Get game from id
        game = games[data["id"]]

        # Check if game is still alive
        if not game.alive:
            return {
                "valid": False
            }

        if game.user_a.token != token and game.user_b.token is None and token is not None:
            game.user_b.token = token
            game.user_b.keep_alive = time.time()
            game.tokens.append(token)

            game.joining = False
            game.readying = True

            game.user_a.event_queue.put({
                "event": "player_joined"
            })

            lock.release()
            return {
                "valid": True,
                "board_size": game.board_size,
                "ship_lengths": game.ship_lengths,
                "quickfire": game.quickfire
            }
        else:
            lock.release()
            return {
                "valid": False
            }

    elif data["request"] == "keep_alive":

        lock.acquire()

        # Make sure that request format is valid
        if not compare_dicts({
            "request": str,
            "token": str,
            "id": lambda x: x in games
        }, data):
            lock.release()
            return {
                "valid": False
            }

        # Get game from id
        game = games[data["id"]]

        # Check if game is still alive
        if not game.alive:
            return {
                "valid": False
            }

        if game.user_a.token == token:
            game.user_a.keep_alive = time.time()

            lock.release()
            return {
                "valid": True
            }
        elif game.user_b.token == token:
            game.user_b.keep_alive = time.time()

            lock.release()
            return {
                "valid": True
            }
        else:

            lock.release()
            return {
                "valid": False
            }

    elif data["request"] == "set_ready":

        # Make sure that request format is valid
        if not compare_dicts({
            "request": str,
            "token": str,
            "id": lambda x: x in games,
            "ship_data": list
        }, data):
            return {
                "valid": False
            }

        lock.acquire()

        # Get game from id
        game = games[data["id"]]

        # Check if game is still alive
        if not game.alive:
            return {
                "valid": False
            }

        # Set the player as being ready
        reply = game.set_ready(token,
                              data["ship_data"])

        lock.release()
        return reply

    elif data["request"] == "fire":

        # Make sure that request format is valid
        if not compare_dicts({
            "request": str,
            "token": str,
            "id": lambda x: x in games,
            "pos": lambda x: type(x[0]) is int and type(x[1]) is int
        }, data):
            return {
                "valid": False
            }

        lock.acquire()

        # Get game from id
        game = games[data["id"]]

        # Check if game is still alive
        if not game.alive:
            return {
                "valid": False
            }

        # Check if pos is on board
        if not -1 < data["pos"][0] < game.board_size or not -1 < data["pos"][1] < game.board_size:
            return {
                "valid": False
            }

        reply = game.process_fire(token, data["pos"])

        lock.release()
        return reply

    elif data["request"] == "get_event":

        lock.acquire()

        # Make sure that request format is valid
        if not compare_dicts({
            "request": str,
            "token": str,
            "id": lambda x: x in games
        }, data):
            lock.release()
            return {
                "valid": False
            }

        # Get game from id
        game = games[data["id"]]

        # Check if game is still alive
        if not game.alive:
            return {
                "valid": False
            }

        # Return single event from event queue
        if game.user_a.token == token:

            lock.release()

            reply = {
                "valid": True
            }

            event = game.user_a.event_queue.get()

            if not event:
                return {
                    "valid": False
                }

            reply.update(event)
            return reply

        elif game.user_b.token == token:

            lock.release()

            reply = {
                "valid": True
            }

            event = game.user_b.event_queue.get()

            if not event:
                return {
                    "valid": False
                }

            reply.update(event)
            return reply

        else:
            lock.release()
            return {
                "valid": False
            }

    else:
        return {
            "valid": False
        }


def process_timeouts():
    def delete_game(id):
        lock.acquire()

        # Close event queues for game
        games[id].user_a.event_queue.close()
        games[id].user_b.event_queue.close()

        lock.release()

        # Wait for queues to finish closing
        time.sleep(3)

        lock.acquire()

        # Remove game from games list
        games.pop(id)

        lock.release()

    while True:
        lock.acquire()

        # Process timeouts for each game
        for game_copy in games.copy().values():
            game = games[game_copy.id]

            if game.alive:
                game.check_alive()
            else:
                continue

            if not game.alive:
                threading.Thread(target=delete_game, args=(game.id,)).start()

        lock.release()
        time.sleep(1)


# Start timeout task
threading.Thread(target=process_timeouts).start()
