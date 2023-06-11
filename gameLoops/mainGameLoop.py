import time

import pygame
from pygame import Vector2

import settings
from sprites.menuSurface import MarketMenu, BuildingMenu, AbstractMenu
from sprites.textSprites import TextSprite, TextButtonSprite
from tiles.hexGrid import HexGrid


def main_game_loop() -> None:
    # Init ------------------------------------------------------------------------------
    pygame.init()
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption("IS THAT AMOGUS???")
    clock = pygame.time.Clock()
    in_menu = False
    run = True
    scroll = Vector2((0, 0))
    start_time = time.time()
    current_turn = 0

    # Groups ------------------------------------------------------------------------------
    hex_grid1 = HexGrid()
    hex_grid1.add_3()

    text_group = pygame.sprite.Group()
    TextSprite("Time Passed (s): ", (1050, 20)).add(text_group)
    TextSprite("Current Turn:", (1050, 50)).add(text_group)

    next_turn_button = TextButtonSprite("Next Turn", (1050, 80), border=2)

    dud_menu = AbstractMenu()
    current_menu_surface = dud_menu

    # Timer ------------------------------------------------------------------------------
    timer_2s = pygame.USEREVENT + 1
    pygame.time.set_timer(timer_2s, 2000)

    # Loop ------------------------------------------------------------------------------
    while run:
        # mouse hover stuff
        mouse_pos = pygame.mouse.get_pos()
        hexagon_hover_cord = hex_grid1.cord_of_collision_with_point((mouse_pos[0]-scroll.x, mouse_pos[1]-scroll.y))
        current_menu_surface.update(mouse_pos)
        next_turn_button.update(mouse_pos)
        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # Mouse press
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Press upgrade button
                    if current_menu_surface.hover:
                        hex_grid1.grid[current_menu_surface.cord].add_level()
                        current_menu_surface = BuildingMenu(hex_grid1.grid[current_menu_surface.cord],
                                                            current_menu_surface.cord)
                    elif next_turn_button.hover:
                        current_turn += 1
                        hex_grid1.next_turn()
                    elif hexagon_hover_cord not in hex_grid1.grid:
                        current_menu_surface = dud_menu
                    elif hex_grid1.grid[hexagon_hover_cord].market_dict:
                        current_menu_surface = BuildingMenu(hex_grid1.grid[hexagon_hover_cord],
                                                            hexagon_hover_cord)
                    else:
                        current_menu_surface = dud_menu
                if event.button == 2:
                    # initialize scroll
                    pygame.mouse.get_rel()
                if event.button == 3:
                    current_menu_surface = MarketMenu(hex_grid1.total_market_dict())
            # Keyboard press
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    in_menu = not in_menu

        # other user input -------------------------------------------------------------
        pressed_mouse_buttons = pygame.mouse.get_pressed()
        if pressed_mouse_buttons[1]:
            # do the actual scroll
            scroll += pygame.mouse.get_rel()

        # static blits ------------------------------------------------------------------------------
        screen.fill((0, 0, 15))
        hex_grid1.draw(screen, scroll)

        text_group.draw(screen)

        next_turn_button.draw(screen)

        # moving blits ------------------------------------------------------------------------------
        time_passed = time.time() - start_time
        time_passed_sprite = TextSprite(f"{time_passed:.0f}", (1230, 20))
        time_passed_sprite.draw(screen)

        current_turn_sprite = TextSprite(f"{current_turn}", (1230, 50))
        current_turn_sprite.draw(screen)

        hex_grid1.draw_single(screen, scroll, hexagon_hover_cord, (255, 255, 255), 8)

        current_menu_surface.draw(screen)

        # test ------------------------------------------------------------------------------

        # end ------------------------------------------------------------------------------
        pygame.display.update()
        # print(clock.get_fps())
        clock.tick(settings.FPS)

    pygame.quit()


if __name__ == '__main__':
    main_game_loop()
