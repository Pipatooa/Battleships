import pygame

import states
import vars

from objects.thread import ThreadedTask


class JoinMenu:
    def __init__(self):
        self.game_id = ""
        self.blink_time = 0

    def run(self):
        self.blink_time += 1

        if self.blink_time >= vars.screen.FRAMERATE * 0.5:
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
                if event.button == pygame.BUTTON_LEFT:
                    # Check if hit join button
                    if not (vars.state == states.JOINING_GAME and vars.substate == states.CONNECTING):
                        if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                                vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                                vars.screen.MID[1] + vars.screen.BORDER_SIZE * 0.25) < event.pos[1] < (
                                vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.25):
                            try:
                                vars.state = states.JOINING_GAME
                                vars.substate = states.CONNECTING
                                ThreadedTask(vars.network.join_game, int(self.game_id)).start()
                            except ValueError:
                                vars.substate = states.INVALID_GAME_ID

                    # Check if hit cancel button
                    if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.75) < event.pos[1] < (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 2.75):
                        vars.game.set_screen("main_menu")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    vars.game.set_screen("main_menu")

                elif event.key == pygame.K_RETURN:
                    if not (vars.state == states.JOINING_GAME and vars.substate == states.CONNECTING):
                        try:
                            vars.state = states.JOINING_GAME
                            vars.substate = states.CONNECTING
                            ThreadedTask(vars.network.join_game, int(self.game_id)).start()
                        except ValueError:
                            vars.substate = states.INVALID_GAME_ID

                # Type into game id box
                else:
                    if chr(event.key).isdigit() and len(self.game_id) < 4:
                        self.game_id += chr(event.key)
                    elif event.key == pygame.K_BACKSPACE:
                        self.game_id = self.game_id[:-1]

        # Fill background
        vars.screen.screen.fill(vars.screen.theme.BACKGROUND_COLOR)

        # Draw title
        text = vars.screen.render_text(100, "JOIN GAME", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midtop = (vars.screen.MID[0],
                            vars.screen.BORDER_SIZE)
        vars.screen.screen.blit(text, text_rect)

        # Draw game id box
        game_id_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2.75,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE * 1
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, game_id_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, game_id_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "GAME ID:", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midleft = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
                             vars.screen.MID[1] - vars.screen.BORDER_SIZE * 3.25)
        vars.screen.screen.blit(text, text_rect)

        # Draw game id text
        if self.blink_time < vars.screen.FRAMERATE * 0.25:
            text = self.game_id + "_"
        else:
            text = self.game_id

        text = vars.screen.render_text(20, text, vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midleft = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5 + vars.screen.MARGIN_SIZE * 6,
                             vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2.25)
        vars.screen.screen.blit(text, text_rect)

        # Draw info text
        if vars.state == states.JOINING_GAME and vars.substate == states.CONNECTING:
            text = "Connecting..."
        elif vars.state == states.JOINING_GAME and vars.substate == states.CONNECTION_FAILED:
            text = "ERROR: Connection failed"
        elif vars.state == states.JOINING_GAME and vars.substate == states.INVALID_GAME_ID:
            text = "ERROR: Invalid game ID"
        else:
            text = ""

        text = vars.screen.render_text(20, text, vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midleft = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5 + vars.screen.MARGIN_SIZE * 3,
                             vars.screen.MID[1] - vars.screen.BORDER_SIZE * 1.25)
        vars.screen.screen.blit(text, text_rect)

        # Draw join button
        join_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 0.25,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, join_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, join_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "JOIN", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 0.75)
        vars.screen.screen.blit(text, text_rect)

        # Draw cancel button
        cancel_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.75,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, cancel_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, cancel_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "CANCEL", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 2.25)
        vars.screen.screen.blit(text, text_rect)

        # Update display
        vars.screen.draw()
