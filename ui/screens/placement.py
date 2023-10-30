import pygame
from ui.colours import Colours
from ui.elements import make_button, confirm_button_image, make_settings_button, quit_button_image
from ui.router import Screen
from ui.sounds import click_sound
from ui.text import Text


class Placement(Screen):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.draw_background = True
        self.ships_left = manager.num_ships
        self.ship_vertical = True

        placement_board_label = Text("Board Setup", (425, 100), 30, Colours.WHITE)
        self.confirm_button = make_button(1000, 225, "Place", 20, image=confirm_button_image)
        self.random_button = make_button(1000, 300, "Randomize", 20, image=confirm_button_image)
        self.quit_button = make_button(1000, 25, "QUIT", 20, image=quit_button_image)
        self.volume_button = make_settings_button()
        self.rotate_button = make_button(1000, 150, "Rotate", 20, image=confirm_button_image)
        self.ships_left_label = Text(
            f"Ships Left: {str(self.ships_left)}", (1000, 500), 30, Colours.WHITE
        )

        self.text_array = [placement_board_label, self.ships_left_label]
        self.button_array = [
            self.quit_button,
            self.rotate_button,
            self.confirm_button,
            self.random_button,
            self.volume_button,
        ]

    async def render(self, mouse, router, manager) -> None:
        if manager.client != None and manager.client.error != None:
            return router.navigate_to("error")
        if self.ships_left <= 0:
            return router.navigate_to("play")
        manager.update_placement()
        # active cell is teh cell we are clicking on
        if manager.get_active_cell() != None:
            """
            We have selected a cell.

            First, display the cell as text on screen.

            If the user then clicks FIRE, we call the game
            manager to execute the fire

            Here, I want to draw all the cells that will be occupied
            by the ship i'm about to place.

            IF there is a conflict, i will draw  the ship's cells in red
            if there is no conflict, the ship will be drawn in green

            there is a conflict IF:
                - one or more cells that this ship will occupy is already
                occupied by some ship
                - one or more cells that this ship will occupy exceeds the
                boundaries of the board

            If the user attempts to place a ship in an invlaid position,
            simply do nothing
            """
            manager.preview_ship(self.ships_left, self.ship_vertical)

        self.ships_left_label.value = f"Ships Left: {str(self.ships_left)}"

    def handle_event(self, event, mouse, router, manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.volume_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("volume")
            # check if we clicked a cell or something else
            if not manager.set_active_cell_placement(mouse):
                if self.quit_button.is_hovered(mouse):
                    click_sound.play()
                    router.navigate_to("main_menu")

                # if we hit confirm, place with the manager
                if manager.active_cell is not None and self.confirm_button.is_hovered(mouse):
                    click_sound.play()
                    successful_placement = manager.place_ship(self.ships_left, self.ship_vertical)
                    # if the placement is successful, subtract the number of ships remaining.
                    if successful_placement:
                        self.ships_left -= 1
                    if self.ships_left <= 0:
                        
                        if manager.ai_game:
                            manager.place_pirate()
                            return router.navigate_to("play")
                        manager.client.set_placement(manager.get_local_player().board.get_placement_data())
                        return router.navigate_to("online_placement_pending")

                if self.rotate_button.is_hovered(mouse):
                    click_sound.play()
                    self.ship_vertical = not self.ship_vertical

                if self.random_button.is_hovered(mouse):
                    click_sound.play()
                    manager.place_random(self.ships_left)
                    if manager.ai_game:
                        manager.place_pirate()
                        return router.navigate_to("play")
                    manager.client.set_placement(manager.get_local_player().board.get_placement_data())
                    return router.navigate_to("online_placement_pending")
