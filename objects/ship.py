import vars


class Ship:
    """Ship object with length, position and hit information"""

    def __init__(self, length):
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

    def check_collisions(self):
        """
        Checks if the ship is intersecting with another ship

        :return: bool
        """

        for ship in vars.game.local_player.board.ships:
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

    def set_initial_pos(self, index):
        """
        Set the initial position of the ship based on its index
        :param index: int
        """

        self.pos = (0, index)
        self.axis = "x"

        self.x_length = self.length
        self.y_length = 1

    def set_pos(self, pos, axis):
        """
        Sets the position of the ship
        """

        self.pos = pos
        self.axis = axis

        if self.axis == "x":
            self.x_length = self.length
            self.y_length = 1
        else:
            self.x_length = 1
            self.y_length = self.length

    def move(self, pos):
        """
        Move the ship to a different location
        """

        # Check if new location is on board
        if all(-1 < x < vars.game.board_size and -1 < y < vars.game.board_size for x, y in self.get_coords(pos)):
            self.pos = pos

        self.check_collisions()

    def toggle_axis(self):
        """
        Changes the axis of the ship
        """

        if self.axis == "x":
            self.axis = "y"
            self.x_length, self.y_length = self.y_length, self.x_length
        else:
            self.axis = "x"
            self.x_length, self.y_length = self.y_length, self.x_length

        if self.axis == "x" and self.pos[0] + self.length > vars.game.board_size:
            self.pos = (vars.game.board_size - self.length, self.pos[1])

        elif self.axis == "y" and self.pos[1] + self.length > vars.game.board_size:
            self.pos = (self.pos[0], vars.game.board_size - self.length)

        self.check_collisions()

    def get_position_info(self):
        """
        Get a list containing position information about the ship
        """

        return [*self.pos, self.axis]
