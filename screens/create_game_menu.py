import json
import os
import random

from collections import deque

import pygame

import vars

from objects.preset import Preset
from objects.thread import ThreadedTask

from objects.board import Board


class CreateGameMenu:
    def __init__(self):
        self.presets = deque()
        with open(os.path.join(".", "presets", ".index.json")) as file:
            index = json.load(file)

        for filename in index["files"]:
            with open(os.path.join(".", "presets", filename)) as file:
                data = json.load(file)

                self.presets.append(Preset(data))

        self.quickfire = True

        self.preview_board = None
        self.preview_board_visible = False

        self.create_preview_board()

    def create_preview_board(self):
        # Create a new board
        vars.screen.calc_board_spacing(self.presets[0].BOARD_SIZE)
        self.preview_board = Board(self.presets[0].BOARD_SIZE, self.presets[0].SHIPS)

        # Place ships on board
        for index, ship in enumerate(self.preview_board.ships):
            ship.set_initial_pos(index)

        # Set 50% of ships to be sunken
        for ship in random.sample(self.preview_board.ships,
                                  min(len(self.preview_board.ships), 2)):
            ship.sunk = True

            for pos in ship.get_coords(None):
                self.preview_board.set_hit(pos)

        # Populate board with shots
        for i in range(self.presets[0].BOARD_SIZE):
            pos = (random.randint(0, self.presets[0].BOARD_SIZE - 1),
                   random.randint(0, self.presets[0].BOARD_SIZE - 1))

            for ship in self.preview_board.ships:
                if pos in ship.get_coords():
                    if ship.hits.count(True) == ship.length - 1:
                        break

                    ship.hits[ship.get_coords().index(pos)] = True
                    self.preview_board.set_hit(pos)
                    break

            else:
                self.preview_board.set_miss(pos)

    def run(self):
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
                if event.button == pygame.BUTTON_LEFT:
                    if not self.preview_board_visible:
                        # Check if hit left preset button
                        if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                                vars.screen.MID[0] - vars.screen.BORDER_SIZE * 4) and (
                                vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5.5) < event.pos[1] < (
                                vars.screen.MID[1] - vars.screen.BORDER_SIZE * 4.5):
                            self.presets.rotate(1)

                        # Check if hit right preset button
                        if (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 4) < event.pos[0] < (
                                vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                                vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5.5) < event.pos[1] < (
                                vars.screen.MID[1] - vars.screen.BORDER_SIZE * 4.5):
                            self.presets.rotate(-1)

                        # Check if hit preview_board button
                        if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                                vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                                vars.screen.MID[1] - vars.screen.BORDER_SIZE * 1.5) < event.pos[1] < (
                                vars.screen.MID[1] - vars.screen.BORDER_SIZE * 0.5):
                            self.create_preview_board()
                            self.preview_board_visible = True

                        # Check if hit quickfire on button
                        if (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 1.5) < event.pos[0] < (
                                vars.screen.MID[0] + vars.screen.BORDER_SIZE * 3) and (
                                vars.screen.MID[1]) < event.pos[1] < (
                                vars.screen.MID[1] + vars.screen.BORDER_SIZE):
                            self.quickfire = True

                        # Check if hit quickfire off button
                        if (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 3.5) < event.pos[0] < (
                                vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                                vars.screen.MID[1]) < event.pos[1] < (
                                vars.screen.MID[1] + vars.screen.BORDER_SIZE):
                            self.quickfire = False

                        # Check if hit host button
                        if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                                vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                                vars.screen.MID[1] + vars.screen.BORDER_SIZE * 3) < event.pos[1] < (
                                vars.screen.MID[1] + vars.screen.BORDER_SIZE * 4):
                            vars.host_thread = ThreadedTask(vars.network.host_game,
                                                            self.presets[0].BOARD_SIZE,
                                                            self.presets[0].SHIPS,
                                                            self.quickfire)
                            vars.host_thread.start()

                        # Check if hit cancel button
                        if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                                vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                                vars.screen.MID[1] + vars.screen.BORDER_SIZE * 4.5) < event.pos[1] < (
                                vars.screen.MID[1] + vars.screen.BORDER_SIZE * 5.5):
                            vars.game.set_screen("main_menu")
                    else:
                        # Check if hit outside preview_board button
                        if (event.pos[0] < vars.screen.MID[0] - vars.screen.BOARD_SIZE * 0.5) or (
                                event.pos[0] > vars.screen.MID[0] + vars.screen.BOARD_SIZE * 0.5) or (
                                event.pos[1] < vars.screen.MID[1] - vars.screen.BOARD_SIZE * 0.5) or (
                                event.pos[1] > vars.screen.MID[1] + vars.screen.BOARD_SIZE * 0.5):
                            self.preview_board_visible = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.preview_board_visible:
                        self.preview_board_visible = False
                    else:
                        vars.state = None
                        vars.substate = None
                        vars.game.set_screen("main_menu")

        # Fill background
        vars.screen.screen.fill(vars.screen.theme.BACKGROUND_COLOR)

        # Draw title
        text = vars.screen.render_text(100, "CREATE GAME", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midtop = (vars.screen.MID[0],
                            vars.screen.BORDER_SIZE)
        vars.screen.screen.blit(text, text_rect)

        # Draw preset selector
        button_left_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5.5,
            vars.screen.BORDER_SIZE,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, button_left_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, button_left_rect,
                         vars.screen.MARGIN_SIZE)

        preset_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 3.5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5.5,
            vars.screen.BORDER_SIZE * 7,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, preset_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, preset_rect,
                         vars.screen.MARGIN_SIZE)

        button_right_rect = (
            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 4,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5.5,
            vars.screen.BORDER_SIZE,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, button_right_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, button_right_rect,
                         vars.screen.MARGIN_SIZE)

        button_left_text = vars.screen.render_text(30, "<", vars.screen.theme.TEXT_COLOR)
        button_left_rect = button_left_text.get_rect()
        button_left_rect.center = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 4.5,
                                   vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5)
        vars.screen.screen.blit(button_left_text, button_left_rect)

        preset_text = vars.screen.render_text(30, self.presets[0].NAME, vars.screen.theme.TEXT_COLOR)
        preset_rect = preset_text.get_rect()
        preset_rect.center = (vars.screen.MID[0],
                              vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5)
        vars.screen.screen.blit(preset_text, preset_rect)

        button_right_text = vars.screen.render_text(30, ">", vars.screen.theme.TEXT_COLOR)
        button_right_rect = button_right_text.get_rect()
        button_right_rect.center = (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 4.5,
                                    vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5)
        vars.screen.screen.blit(button_right_text, button_right_rect)

        # Preset info box
        info_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 4,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE * 2
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, info_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, info_rect,
                         vars.screen.MARGIN_SIZE)

        info_text = vars.screen.render_text(20, "BOARD SIZE: %s" % self.presets[0].BOARD_SIZE,
                                            vars.screen.theme.TEXT_COLOR)
        info_rect = info_text.get_rect()
        info_rect.midleft = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5 + vars.screen.MARGIN_SIZE * 6,
                             vars.screen.MID[1] - vars.screen.BORDER_SIZE * 3.5)
        vars.screen.screen.blit(info_text, info_rect)

        info_text = vars.screen.render_text(20, self.presets[0].DESCRIPTION, vars.screen.theme.TEXT_COLOR)
        info_rect = info_text.get_rect()
        info_rect.midleft = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5 + vars.screen.MARGIN_SIZE * 6,
                             vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2.5)
        vars.screen.screen.blit(info_text, info_rect)

        # Preview board button
        preview_board_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 1.5,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, preview_board_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, preview_board_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "PREVIEW BOARD", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE)
        vars.screen.screen.blit(text, text_rect)

        # Quickfire selector
        quickfire_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1],
            vars.screen.BORDER_SIZE * 6,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, quickfire_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, quickfire_rect,
                         vars.screen.MARGIN_SIZE)

        if self.quickfire:
            text = "QUICKFIRE: ON"
        else:
            text = "QUICKFIRE: OFF"

        text = vars.screen.render_text(30, text, vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midleft = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5 + vars.screen.MARGIN_SIZE * 3,
                             vars.screen.MID[1] + vars.screen.BORDER_SIZE * 0.5)
        vars.screen.screen.blit(text, text_rect)

        on_rect = (
            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 1.5,
            vars.screen.MID[1],
            vars.screen.BORDER_SIZE * 1.5,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, on_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, on_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "ON", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 2.25,
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 0.5)
        vars.screen.screen.blit(text, text_rect)

        off_rect = (
            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 3.5,
            vars.screen.MID[1],
            vars.screen.BORDER_SIZE * 1.5,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, off_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, off_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "OFF", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 4.25,
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 0.5)
        vars.screen.screen.blit(text, text_rect)

        # Host game button
        host_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 3,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, host_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, host_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "HOST", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 3.5)
        vars.screen.screen.blit(text, text_rect)

        # Cancel button
        host_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 4.5,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, host_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, host_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "CANCEL", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 5)
        vars.screen.screen.blit(text, text_rect)

        # Preview board overlay
        if self.preview_board_visible:
            background_rect = pygame.Surface(vars.screen.SIZE)
            background_rect.set_alpha(192)
            background_rect.fill((0, 0, 0))
            vars.screen.screen.blit(background_rect, (0, 0))

            self.preview_board.draw((vars.screen.MID[0] - vars.screen.BOARD_SIZE * 0.5,
                                     vars.screen.MID[1] - vars.screen.BOARD_SIZE * 0.5))

        # Update display
        vars.screen.draw()
