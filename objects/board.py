from collections import defaultdict

import pygame

import vars

from objects.ship import Ship


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
        self.ships = [Ship(length) for length in ship_lengths]

        # Reset the board
        self.board = [[0 for i in range(self.SIZE)] for i in range(self.SIZE)]

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

    def draw(self, pos):
        """Draws the board onto the screen at pos"""

        # Draw grid to the screen
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.GRID_COLOR, (
            pos[0],
            pos[1],
            vars.screen.BOARD_SIZE,
            vars.screen.BOARD_SIZE
        ))

        # Draw grid cells to screen
        for x in range(self.SIZE):
            for y in range(self.SIZE):
                # Determine cell position in pixels
                x_location = pos[0] + vars.screen.MARGIN_SIZE + (vars.screen.CELL_SIZE + vars.screen.MARGIN_SIZE) * x
                y_location = pos[1] + vars.screen.MARGIN_SIZE + (vars.screen.CELL_SIZE + vars.screen.MARGIN_SIZE) * y

                # Draw cell to screen
                pygame.draw.rect(vars.screen.screen, vars.screen.theme.CELL_COLOR,
                                 (x_location,
                                  y_location,
                                  vars.screen.CELL_SIZE,
                                  vars.screen.CELL_SIZE)
                                 )

        # Draw ships to the screen
        for ship in self.ships:
            # If ship has unknown position, do not draw
            if not ship.pos:
                continue

            # If sunk, set theme
            if ship.sunk or ship.collisions:
                color = vars.screen.theme.SUNK_SHIP_COLOR
            else:
                color = vars.screen.theme.SHIP_COLOR

            # Determine ship position in pixels
            x_location = pos[0] + vars.screen.MARGIN_SIZE + (vars.screen.CELL_SIZE + vars.screen.MARGIN_SIZE) * \
                         ship.pos[0]
            y_location = pos[1] + vars.screen.MARGIN_SIZE + (vars.screen.CELL_SIZE + vars.screen.MARGIN_SIZE) * \
                         ship.pos[1]

            width = (vars.screen.CELL_SIZE + vars.screen.MARGIN_SIZE) * ship.x_length - vars.screen.MARGIN_SIZE
            height = (vars.screen.CELL_SIZE + vars.screen.MARGIN_SIZE) * ship.y_length - vars.screen.MARGIN_SIZE

            # Draw ship to the screen
            pygame.draw.rect(vars.screen.screen, color,
                             (x_location,
                              y_location,
                              width,
                              height
                              )
                             )

        # Draw dots to the screen
        for x, column in enumerate(self.board):
            for y, cell in enumerate(column):

                # By default, no dot should be displayed
                dot = None

                # If miss, set themed dot
                if cell == 1:
                    dot = (255, 255, 255)

                # If hit, set themed dot
                elif cell == 2:
                    dot = (255, 0, 0)

                # If not set, skip
                else:
                    continue

                # Determine position of dot in pixels
                x_location = int(
                    pos[0] + vars.screen.MARGIN_SIZE + (vars.screen.CELL_SIZE + vars.screen.MARGIN_SIZE) * x + (
                            vars.screen.CELL_SIZE // 2))
                y_location = int(
                    pos[1] + vars.screen.MARGIN_SIZE + (vars.screen.CELL_SIZE + vars.screen.MARGIN_SIZE) * y + (
                            vars.screen.CELL_SIZE // 2))

                pygame.draw.circle(vars.screen.screen, dot, (x_location, y_location), vars.screen.CELL_DOT_SIZE)
