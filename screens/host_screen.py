import socket

import pygame

import vars


class HostScreen:
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())

    def run(self):

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    # Check if hit cancel button
                    if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE) < event.pos[1] < (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 2):
                        vars.state = None
                        vars.substate = None
                        vars.network.network.disconnect()
                        vars.game.set_screen("create_game_menu")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    vars.state = None
                    vars.substate = None
                    vars.network.network.disconnect()
                    vars.game.set_screen("create_game_menu")

        # Fill background
        vars.screen.screen.fill(vars.screen.theme.BACKGROUND_COLOR)

        # Title
        text = vars.screen.render_text(100, "HOSTING GAME", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midtop = (vars.screen.MID[0],
                            vars.screen.BORDER_SIZE)
        vars.screen.screen.blit(text, text_rect)

        # IP text
        text = vars.screen.render_text(30, "YOUR LOCAL IP:", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midleft = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
                             vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2.5)
        vars.screen.screen.blit(text, text_rect)

        # IP box
        ip_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, ip_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, ip_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(20, self.ip, vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midleft = (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5 + vars.screen.MARGIN_SIZE * 6,
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 1.5)
        vars.screen.screen.blit(text, text_rect)

        # Cancel button
        cancel_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] + vars.screen.BORDER_SIZE,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_COLOR, cancel_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, cancel_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "CANCEL", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                             vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.5)
        vars.screen.screen.blit(text, text_rect)

        # Update display
        vars.screen.draw()
