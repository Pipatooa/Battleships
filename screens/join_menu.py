import pygame

import states
import vars

from objects.thread import ThreadedTask

class JoinMenu:
    def __init__(self):
        self.ip = ""

        self.shift_held = False

        self.blink_time = 0

    def run(self):
        self.blink_time += 1

        if self.blink_time >= vars.screen.FRAMERATE * 0.5:
            self.blink_time = 0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    # Check if hit join button
                    if not (vars.state == states.JOINING_GAME and vars.substate == states.AWAITING_JOIN):
                        if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                                vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                                vars.screen.MID[1] + vars.screen.BORDER_SIZE * 0.25) < event.pos[1] < (
                                vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.25):
                            vars.state = states.JOINING_GAME
                            vars.substate = states.AWAITING_JOIN
                            ThreadedTask(vars.network.join_game, self.ip).start()

                    # Check if hit cancel button
                    if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.75) < event.pos[1] < (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 2.75):
                        vars.game.set_screen("main_menu")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    vars.game.set_screen("main_menu")

                # Type into ip box
                else:
                    mods = pygame.key.get_mods()

                    if chr(event.key).isalnum() and chr(event.key).isascii():
                        self.ip += chr(event.key)
                    elif event.key == pygame.K_PERIOD:
                        self.ip += "."
                    elif event.key == pygame.K_SEMICOLON and mods & pygame.KMOD_LSHIFT:
                        self.ip += ":"
                    elif event.key == pygame.K_BACKSPACE:
                        self.ip = self.ip[:-1]



        # Fill background
        vars.screen.screen.fill(vars.screen.theme.BACKGROUND_COLOR)

        # Draw title
        text = vars.screen.render_text(100, "JOIN GAME", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midtop = (vars.screen.MID[0],
                            vars.screen.BORDER_SIZE)
        vars.screen.screen.blit(text, text_rect)

        # Draw ip box
        ip_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2.75,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE * 1
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, ip_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, ip_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "HOST ADDRESS:", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midleft = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 3.25)
        vars.screen.screen.blit(text, text_rect)

        # Draw ip text
        if self.blink_time < vars.screen.FRAMERATE * 0.25:
            text = self.ip[-40:]
        else:
            text = self.ip[-40:] + "_"

        text = vars.screen.render_text(20, text, vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midleft = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5 + vars.screen.MARGIN_SIZE * 6,
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2.25)
        vars.screen.screen.blit(text, text_rect)

        # Draw info text
        if vars.state == states.JOINING_GAME and vars.substate == states.AWAITING_JOIN:
            text = "Connecting..."
        elif vars.state == states.JOINING_GAME and vars.substate == states.FAILED:
            text = "ERROR: Connection failed"
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

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, join_rect)
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

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, cancel_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, cancel_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "CANCEL", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 2.25)
        vars.screen.screen.blit(text, text_rect)

        # Update display
        vars.screen.draw()
