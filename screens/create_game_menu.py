import json
import os

from collections import Counter
from collections import deque

import pygame

import vars

from objects.preset import Preset
from objects.thread import ThreadedTask


def draw_ship_info(ships):
    """
    Draws ship info to the screen
    :param ships: [int length, int length, ...]]
    """

    # Unpack ship data
    ship_data = Counter(ships)

    # Calculate how large each ship cell should be
    ship_indicator_size_a = (vars.screen.BORDER_SIZE * 4 -
                             (len(ship_data) + 2) * vars.screen.MARGIN_SIZE * 3) / (len(ship_data) + 1)
    ship_indicator_size_b = (vars.screen.BORDER_SIZE * 9 - vars.screen.MARGIN_SIZE * 3) / max(ship_data.keys())
    ship_indicator_size = min(ship_indicator_size_a, ship_indicator_size_b)

    # Draw title text
    text = vars.screen.render_text(ship_indicator_size * 0.9 / vars.screen.FONT_SCALE, "-",
                                   vars.screen.theme.TEXT_COLOR)
    text_rect = text.get_rect()
    text_rect.midtop = (vars.screen.MID[0],
                        vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2 + vars.screen.MARGIN_SIZE * 3)
    vars.screen.screen.blit(text, text_rect)

    for index, data in enumerate(sorted(ship_data.items())):
        ship_length, count = data

        spacing = vars.screen.MARGIN_SIZE * 3
        y_pos = vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2 + (ship_indicator_size + spacing) * (index + 1)


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

    def run(self):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    # Check if hit left preset button
                    if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 4) and (
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5.25) < event.pos[1] < (
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 4.25):
                        self.presets.rotate(1)

                    # Check if hit right preset button
                    if (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 4) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5.25) < event.pos[1] < (
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 4.25):
                        self.presets.rotate(-1)

                    # Check if hit quickfire on button
                    if (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 1.5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 3) and (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.25) < event.pos[1] < (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 2.25):
                        self.quickfire = True

                    # Check if hit quickfire off button
                    if (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 3.5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.25) < event.pos[1] < (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 2.25):
                        self.quickfire = False

                    # Check if hit host button
                    if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 2.75) < event.pos[1] < (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 3.75):
                        vars.host_thread = ThreadedTask(vars.network.host_game,
                                                        self.presets[0].BOARD_SIZE,
                                                        self.presets[0].SHIPS,
                                                        self.quickfire)
                        vars.host_thread.start()

                    # Check if hit cancel button
                    if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 4.25) < event.pos[1] < (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 5.25):
                        vars.game.set_screen("main_menu")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
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
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5.25,
            vars.screen.BORDER_SIZE,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, button_left_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, button_left_rect,
                         vars.screen.MARGIN_SIZE)

        preset_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 3.5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5.25,
            vars.screen.BORDER_SIZE * 7,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, preset_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, preset_rect,
                         vars.screen.MARGIN_SIZE)

        button_right_rect = (
            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 4,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 5.25,
            vars.screen.BORDER_SIZE,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, button_right_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, button_right_rect,
                         vars.screen.MARGIN_SIZE)

        button_left_text = vars.screen.render_text(30, "<", vars.screen.theme.TEXT_COLOR)
        button_left_rect = button_left_text.get_rect()
        button_left_rect.center = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 4.5,
                                   vars.screen.MID[1] - vars.screen.BORDER_SIZE * 4.75)
        vars.screen.screen.blit(button_left_text, button_left_rect)

        preset_text = vars.screen.render_text(30, self.presets[0].NAME, vars.screen.theme.TEXT_COLOR)
        preset_rect = preset_text.get_rect()
        preset_rect.center = (vars.screen.MID[0],
                              vars.screen.MID[1] - vars.screen.BORDER_SIZE * 4.75)
        vars.screen.screen.blit(preset_text, preset_rect)

        button_right_text = vars.screen.render_text(30, ">", vars.screen.theme.TEXT_COLOR)
        button_right_rect = button_right_text.get_rect()
        button_right_rect.center = (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 4.5,
                                    vars.screen.MID[1] - vars.screen.BORDER_SIZE * 4.75)
        vars.screen.screen.blit(button_right_text, button_right_rect)

        # Size info
        size_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 3.75,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, size_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, size_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "BOARD SIZE: %s" % self.presets[0].BOARD_SIZE, vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 3.25)
        vars.screen.screen.blit(text, text_rect)

        # Ship info box
        info_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2.25,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE * 3
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, info_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, info_rect,
                         vars.screen.MARGIN_SIZE)

        draw_ship_info(self.presets[0].SHIPS)

        # Quickfire selector
        quickfire_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.25,
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
                             vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.75)
        vars.screen.screen.blit(text, text_rect)

        on_rect = (
            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 1.5,
            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.25,
            vars.screen.BORDER_SIZE * 1.5,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, on_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, on_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "ON", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 2.25,
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.75)
        vars.screen.screen.blit(text, text_rect)

        off_rect = (
            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 3.5,
            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.25,
            vars.screen.BORDER_SIZE * 1.5,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, off_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, off_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "OFF", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0] + vars.screen.BORDER_SIZE * 4.25,
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.75)
        vars.screen.screen.blit(text, text_rect)

        # Host game button
        host_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 2.75,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, host_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, host_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "HOST", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 3.25)
        vars.screen.screen.blit(text, text_rect)

        # Cancel button
        host_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 4.25,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, host_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, host_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "CANCEL", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 4.75)
        vars.screen.screen.blit(text, text_rect)

        # Update display
        vars.screen.draw()
