import pygame

import vars


class MainMenu:
    def __init__(self):
        vars.state = None
        vars.substate = None

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
                    # Check if hit create game button
                    if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2) < event.pos[1] < (
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE):
                        vars.game.set_screen("create_game_menu")

                    # Check if hit join button
                    if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 0.5) < event.pos[1] < (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 0.5):
                        vars.game.set_screen("join_menu")

                    # Check if hit quit button
                    if (vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5) < event.pos[0] < (
                            vars.screen.MID[0] + vars.screen.BORDER_SIZE * 5) and (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE) < event.pos[1] < (
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 2):
                        quit()

        # Fill background
        vars.screen.screen.fill(vars.screen.theme.BACKGROUND_COLOR)

        # Draw title
        text = vars.screen.render_text(100, "BATTLESHIPS", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.midtop = (vars.screen.MID[0],
                            vars.screen.BORDER_SIZE)
        vars.screen.screen.blit(text, text_rect)

        # Create game button
        create_game_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 2,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, create_game_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, create_game_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "CREATE GAME", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 1.5)
        vars.screen.screen.blit(text, text_rect)

        # Join button
        join_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] - vars.screen.BORDER_SIZE * 0.5,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, join_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, join_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "JOIN GAME", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1])
        vars.screen.screen.blit(text, text_rect)

        # Quit button
        quit_rect = (
            vars.screen.MID[0] - vars.screen.BORDER_SIZE * 5,
            vars.screen.MID[1] + vars.screen.BORDER_SIZE,
            vars.screen.BORDER_SIZE * 10,
            vars.screen.BORDER_SIZE
        )

        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BUTTON_COLOR, quit_rect)
        pygame.draw.rect(vars.screen.screen, vars.screen.theme.BOX_OUTLINE_COLOR, quit_rect,
                         vars.screen.MARGIN_SIZE)

        text = vars.screen.render_text(30, "QUIT", vars.screen.theme.TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (vars.screen.MID[0],
                            vars.screen.MID[1] + vars.screen.BORDER_SIZE * 1.5)
        vars.screen.screen.blit(text, text_rect)

        # Update display
        vars.screen.draw()
