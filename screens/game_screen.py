from collections import defaultdict

import pygame

import states
import vars


def get_grid_pos(grid_pos, pos):
    """
    Converts pixel coordinates to grid coordinates
    :param grid_pos: (int, int)
    :param pos: (int, int)
    :return: (int, int),        if in grid
             False              if outside grid
    """

    grid_x, grid_y = grid_pos
    x, y = pos

    x = int((x - grid_x - vars.screen.MARGIN_SIZE) //
            (vars.screen.CELL_SIZE + vars.screen.MARGIN_SIZE))
    y = int((y - grid_y - vars.screen.MARGIN_SIZE) //
            (vars.screen.CELL_SIZE + vars.screen.MARGIN_SIZE))

    if -1 < x < vars.game.board_size and -1 < y < vars.game.board_size:
        return x, y

    return False


def draw_ship_info():
    """
    Draws ship info to the screen
    """
    # Unpack ship data
    ship_data = defaultdict(lambda: [0, 0, 0, 0])
    for local_ship, other_ship in zip(vars.game.local_player.board.ships, vars.game.other_player.board.ships):
        if local_ship.sunk:
            ship_data[local_ship.length][1] += 1
        else:
            ship_data[local_ship.length][0] += 1

        if other_ship.sunk:
            ship_data[other_ship.length][3] += 1
        else:
            ship_data[other_ship.length][2] += 1

    # Calculate how large each ship cell should be
    ship_indicator_size_a = (vars.screen.HEIGHT - vars.screen.BOARD_SIZE - vars.screen.BORDER_SIZE * 7 -
                             (len(ship_data) + 2) * vars.screen.MARGIN_SIZE * 3) / (len(ship_data) + 1)
    ship_indicator_size_b = (vars.screen.BOARD_SIZE * 0.5 - vars.screen.MARGIN_SIZE * 3) / max(ship_data.keys())
    ship_indicator_size = min(ship_indicator_size_a, ship_indicator_size_b)

    # Draw title text
    text = vars.screen.render_text(ship_indicator_size * 0.9 / vars.screen.FONT_SCALE, "SHIPS", vars.screen.theme.TEXT_COLOR)
    text_rect = text.get_rect()
    text_rect.midtop = (vars.screen.MID[0],
                          vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 6 + vars.screen.MARGIN_SIZE * 3)
    vars.screen.screen.blit(text, text_rect)

    # Draw ship indicators
    for index, data in enumerate(sorted(ship_data.items(), reverse=True)):
        ship_length, data = data
        local_alive, local_sunk, other_alive, other_sunk = data

        spacing = vars.screen.MARGIN_SIZE * 3
        x_unit = ship_indicator_size * ship_length
        y_pos = vars.screen.HEIGHT - vars.screen.BORDER_SIZE - (ship_indicator_size + spacing) * (index + 1)

        # Ship length text
        text = vars.screen.render_text(ship_indicator_size * 0.5 / vars.screen.FONT_SCALE, "-%s-" % ship_length, vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            y_pos + ship_indicator_size * 0.5)
        vars.screen.screen.blit(text, text_rect)

        # Local alive indicator
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.SHIP_COLOR, (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 0.5 - x_unit,
            y_pos,
            ship_indicator_size * ship_length,
            ship_indicator_size
        ))

        # Local alive text
        text = vars.screen.render_text(ship_indicator_size * 0.5 / vars.screen.FONT_SCALE, str(local_alive), vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 0.5 - ship_indicator_size * 0.5,
                              y_pos + ship_indicator_size * 0.5)
        vars.screen.screen.blit(text, text_rect)

        # Local sunk indicator
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.SUNK_SHIP_COLOR, (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 0.5 - x_unit * 2 - spacing,
            y_pos,
            ship_indicator_size * ship_length,
            ship_indicator_size
        ))

        # Local sunk text
        text = vars.screen.render_text(ship_indicator_size * 0.5 / vars.screen.FONT_SCALE, str(local_sunk), vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 0.5 - ship_indicator_size * 0.5
                              - x_unit - spacing,
                              y_pos + ship_indicator_size * 0.5)
        vars.screen.screen.blit(text, text_rect)

        # Other alive indicator
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.SHIP_COLOR, (
            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 0.5,
            y_pos,
            ship_indicator_size * ship_length,
            ship_indicator_size
        ))

        # Other alive text
        text = vars.screen.render_text(ship_indicator_size * 0.5 / vars.screen.FONT_SCALE, str(other_alive), vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 0.5 + ship_indicator_size * 0.5,
                              y_pos + ship_indicator_size * 0.5)
        vars.screen.screen.blit(text, text_rect)

        # Other sunk indicator
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.SUNK_SHIP_COLOR, (
            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 0.5 + x_unit + spacing,
            y_pos,
            ship_indicator_size * ship_length,
            ship_indicator_size
        ))

        # Other sunk text
        text = vars.screen.render_text(ship_indicator_size * 0.5 / vars.screen.FONT_SCALE, str(other_sunk), vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 0.5 + ship_indicator_size * 0.5
                             + x_unit + spacing,
                             y_pos + ship_indicator_size * 0.5)
        vars.screen.screen.blit(text, text_rect)


class GameScreen:
    def __init__(self):
        # Set default location for player's ships
        for index, ship in enumerate(vars.game.local_player.board.ships):
            ship.set_initial_pos(index)

        self.cursor_selected = None
        self.cursor_selected_offset = None

        self.LOCAL_BOARD_POS = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 0.5 - vars.screen.BOARD_SIZE,
                                vars.screen.BORDER_SIZE * 3)
        self.OTHER_BOARD_POS = (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 0.5,
                                vars.screen.BORDER_SIZE * 3)

        self.blink_time = 0

    def run(self):
        self.blink_time += 1

        if self.blink_time > vars.screen.FRAMERATE:
            self.blink_time = 0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.VIDEORESIZE:
                vars.screen.rescale_window(event.size, None)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    vars.screen.toggle_fullscreen()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # If in ready position
                if vars.state == states.SETUP and vars.substate == states.AWAITING_READY:
                    grid_pos = get_grid_pos(self.LOCAL_BOARD_POS, event.pos)

                    if grid_pos:
                        for ship in vars.game.local_player.board.ships:
                            if grid_pos in ship.get_coords():
                                if event.button == pygame.BUTTON_LEFT:
                                    self.cursor_selected = ship
                                    self.cursor_selected_offset = (grid_pos[0] - ship.pos[0],
                                                                   grid_pos[1] - ship.pos[1])

                                elif event.button == pygame.BUTTON_RIGHT:
                                    ship.toggle_axis()

                                break

                    # Check if hit ready button
                    if (vars.screen.MID[0] - vars.screen.BOARD_SIZE - vars.screen.BORDER_SIZE * 0.5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 0.5) and (
                            vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 6) < event.pos[1] < (
                            vars.screen.HEIGHT - vars.screen.BORDER_SIZE):

                        # Check that ship placement is valid
                        if not any(ship.collisions for ship in vars.game.local_player.board.ships):
                            vars.substate = states.AWAITING_START
                            vars.network.set_ready()

                # Check if hit disconnect button
                if event.button == pygame.BUTTON_LEFT:
                    if (vars.screen.MID[0] - vars.screen.BOARD_SIZE - vars.screen.BORDER_SIZE * 0.5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 0.5) and (
                            vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 4) < event.pos[1] < (
                            vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 5):

                        vars.network.disconnect()
                        vars.game.set_screen("main_menu")
                        return

                # Check if click corresponds to fire action
                if vars.state == states.FIRING and vars.substate == states.AWAITING_INPUT and event.button == pygame.BUTTON_LEFT:
                    grid_pos = get_grid_pos(self.OTHER_BOARD_POS, event.pos)

                    if grid_pos:
                        x, y = grid_pos

                        if not vars.game.other_player.board.board[x][y]:
                            vars.substate = states.AWAITING_RESULT
                            vars.network.fire(grid_pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT and self.cursor_selected:
                    self.cursor_selected = None

            elif event.type == pygame.MOUSEMOTION:
                if self.cursor_selected:
                    grid_pos = get_grid_pos(self.LOCAL_BOARD_POS, event.pos)

                    if grid_pos:
                        self.cursor_selected.move((grid_pos[0] - self.cursor_selected_offset[0],
                                                   grid_pos[1] - self.cursor_selected_offset[1]))

        # Fill background
        vars.screen.screen.fill(vars.screen.theme.BACKGROUND_COLOR)

        # Draw center rectangle
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.CENTER_COLOR, (
            vars.screen.MID[0] - vars.screen.BOARD_SIZE - vars.screen.BORDER_SIZE * 1.5,
            0,
            vars.screen.BOARD_SIZE * 2 + vars.screen.BORDER_SIZE * 3,
            vars.screen.HEIGHT
        ))

        # Draw title box
        title_rect = (
            vars.screen.MID[0] - vars.screen.BOARD_SIZE - vars.screen.BORDER_SIZE * 0.5,
            vars.screen.BORDER_SIZE,
            vars.screen.BOARD_SIZE * 2 + vars.screen.BORDER_SIZE,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, title_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, title_rect,
                         vars.screen.MARGIN_SIZE)

        # Title text
        if vars.state in [states.FIRING, states.RECEIVING_FIRE, states.GAME_OVER]:
            you = "YOU - %s" % vars.game.local_player.score
            enemy = "ENEMY - %s" % vars.game.other_player.score
        else:
            you = "YOU"
            enemy = "ENEMY"

        text = vars.screen.render_text(30, you, vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (self.LOCAL_BOARD_POS[0] + vars.screen.BOARD_SIZE * 0.5,
                            vars.screen.BORDER_SIZE * 1.5)
        vars.screen.screen.blit(text, text_rect)

        text = vars.screen.render_text(30, enemy, vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (self.OTHER_BOARD_POS[0] + vars.screen.BOARD_SIZE * 0.5,
                            vars.screen.BORDER_SIZE * 1.5)
        vars.screen.screen.blit(text, text_rect)

        # Draw game boards
        vars.game.local_player.board.draw(self.LOCAL_BOARD_POS)
        vars.game.other_player.board.draw(self.OTHER_BOARD_POS)

        # Disconnect button
        disconnect_rect = (
            vars.screen.MID[0] - vars.screen.BOARD_SIZE - vars.screen.BORDER_SIZE * 0.5,
            vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 4,
            vars.screen.BOARD_SIZE * 2 + vars.screen.BORDER_SIZE,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, disconnect_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, disconnect_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "DISCONNECT", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 4.5)
        vars.screen.screen.blit(text, text_rect)

        # Draw info box
        info_rect = (
            vars.screen.MID[0] - vars.screen.BOARD_SIZE - vars.screen.BORDER_SIZE * 0.5,
            vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 6,
            vars.screen.BOARD_SIZE * 2 + vars.screen.BORDER_SIZE,
            vars.screen.HEIGHT - vars.screen.BOARD_SIZE - vars.screen.BORDER_SIZE * 7
        )

        # Draw info box
        if vars.state == states.SETUP and vars.substate == states.AWAITING_READY:
            color = vars.screen.theme.BUTTON_COLOR
        else:
            color = vars.screen.theme.BOX_COLOR

        pygame.draw.rect(vars.screen.screen, color, info_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, info_rect,
                         vars.screen.MARGIN_SIZE)

        if vars.state in [states.FIRING, states.RECEIVING_FIRE]:
            pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, info_rect)
            pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, info_rect,
                             vars.screen.MARGIN_SIZE)

            draw_ship_info()
        else:
            if vars.state == states.SETUP and vars.substate == states.AWAITING_READY:
                text = "READY"
                text_b = ""
            elif vars.state == states.SETUP and vars.substate == states.AWAITING_START:
                text = "WAITING"
                text_b = ""
            elif vars.state == states.GAME_OVER and vars.substate == states.WON:
                text = "YOU WIN"
                text_b = ""
            elif vars.state == states.GAME_OVER and vars.substate == states.LOST:
                text = "YOU LOSE"
                text_b = ""
            elif vars.state == states.GAME_OVER and vars.substate == states.LOST_CONNECTION:
                text = "LOST"
                text_b = "CONNECTION"
            elif vars.state == states.GAME_OVER and vars.substate == states.DISCONNECT:
                text = "OPPONENT"
                text_b = "DISCONNECTED"
            else:
                text = "ERROR"
                text_b = "INVALID STATE"

            if text_b:
                text = vars.screen.render_text(75, text, vars.screen.theme.TEXT_COLOR)
                text_rect = text.get_rect()
                text_rect.center = (vars.screen.MID[0],
                                    (vars.screen.HEIGHT + vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 3) * 0.5)

                vars.screen.screen.blit(text, text_rect)

                text = vars.screen.render_text(75, text_b, vars.screen.theme.TEXT_COLOR)
                text_rect = text.get_rect()
                text_rect.center = (vars.screen.MID[0],
                                    (vars.screen.HEIGHT + vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 7) * 0.5)

                vars.screen.screen.blit(text, text_rect)
            else:
                text = vars.screen.render_text(150, text, vars.screen.theme.TEXT_COLOR)
                text_rect = text.get_rect()
                text_rect.center = (vars.screen.MID[0],
                                    (vars.screen.HEIGHT + vars.screen.BOARD_SIZE + vars.screen.BORDER_SIZE * 5) * 0.5)

                vars.screen.screen.blit(text, text_rect)

        # Draw attack arrows
        if vars.state == states.RECEIVING_FIRE:
            points = [(vars.screen.CELL_SIZE * 0.3, vars.screen.CELL_SIZE * -0.7),
                      (vars.screen.CELL_SIZE * 0.9, vars.screen.CELL_SIZE * -0.7),
                      (vars.screen.CELL_SIZE * 0.6, vars.screen.CELL_SIZE * -0.3)
                      ]

            points = [(x + self.LOCAL_BOARD_POS[0], y + self.LOCAL_BOARD_POS[1]) for x, y in points]
        elif vars.state == states.FIRING:
            points = [(vars.screen.CELL_SIZE * 0.3, vars.screen.CELL_SIZE * -0.3),
                      (vars.screen.CELL_SIZE * 0.9, vars.screen.CELL_SIZE * -0.3),
                      (vars.screen.CELL_SIZE * 0.6, vars.screen.CELL_SIZE * -0.7)
                      ]

            points = [(x + self.OTHER_BOARD_POS[0], y + self.OTHER_BOARD_POS[1]) for x, y in points]

        if vars.state in [states.RECEIVING_FIRE, states.FIRING]:
            if self.blink_time < vars.screen.FRAMERATE * 0.5:
                for i in range(vars.game.board_size):
                    new_points = [(x + (vars.screen.CELL_SIZE + vars.screen.MARGIN_SIZE) * i, y) for x, y in
                                  points]

                    pygame.draw.polygon(vars.screen.screen, vars.screen.theme.ATTACK_COLOR, new_points)
                    pygame.draw.polygon(vars.screen.screen, vars.screen.theme.ATTACK_OUTLINE_COLOR, new_points,
                                        int(vars.screen.MARGIN_SIZE * 0.75))

        # Update display
        vars.screen.draw()
