import asyncio
import string
import pygame
from game_manager import AIDifficulty
from ui.colours import Colours
from ui.elements import make_button, confirm_button_image, make_help_button, make_settings_button, quit_button_image, confirm_button_greyed
from ui.router import Screen
from ui.sounds import click_sound
from ui.text import Text
from utilities import Turn


class Play(Screen):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.draw_background = True
        self.selected_coords = ()
        self.change_turn = False if manager.ai_game or manager.client.player_id == "0" else True
        
        if manager.ai_game and manager.ai_difficulty == AIDifficulty.HARD:
            manager.hard_ai_setup()

        opponent_board_label = Text("OPPONENT'S BOARD", (425, 100), 30, Colours.WHITE)
        my_board_label = Text("MY BOARD", (1000, 325), 30, Colours.WHITE)
        self.turn_text = Text("", (1000, 100), 30, Colours.GOLD)
        select_text = Text("YOU HAVE SELECTED:", (1000, 150), 15, Colours.WHITE)
        self.coord_text = Text("", (1000, 200), 15, Colours.WHITE)

        self.fire_button = make_button(1000, 250, "FIRE", 20, image=confirm_button_greyed)
        self.quit_button = make_button(1000, 25, "QUIT", 20, image=quit_button_image)
        self.volume_button = make_settings_button()
        self.help_button = make_help_button()

        self.text_array = [opponent_board_label, 
                           my_board_label, 
                           self.turn_text, 
                           select_text, 
                           self.coord_text]
        self.button_array = [self.quit_button,
                             self.volume_button,
                             self.fire_button,
                             self.help_button]

    async def render(self, mouse, router, manager):
        if manager.client != None and manager.client.error != None:
            return router.navigate_to("error")
        if manager.turn == Turn.PLAYER_ONE:
            if manager.active_cell is not None:
                self.fire_button.set_image(confirm_button_image)
            self.turn_text.value = "Your Turn"
        elif manager.turn ==Turn.PLAYER_TWO:
            self.fire_button.set_image(confirm_button_greyed)
            self.turn_text.value = "Opponent Turn"
        if manager.skip_turn:
            self.fire_button.set_image(confirm_button_image)
            self.turn_text.value = "You missed your turn!"
            self.fire_button.set_text("OK")
        elif manager.p2_skip_turn:
            self.turn_text.value = "Opponent missed their turn!"
        
        manager.update_boards()
        if manager.game_over:
            return router.navigate_to("endgame")
        if manager.get_active_cell() != None:
            """
            We have selected a cell.

            First, display the cell as text on screen.

            If the user then clicks FIRE, we call the game
            manager to execute the fire
            """
            cell_coords = manager.get_active_cell().coordinates
            self.coord_text.value = f"({string.ascii_uppercase[cell_coords[0]]}, {cell_coords[1] + 1})"
        if self.change_turn and manager.ai_game:
            asyncio.create_task(manager.change_turn())
            self.change_turn = False
          
    def handle_event(self, event, mouse, router, manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.help_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("play_help")
            if self.volume_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("volume")
            # check if we clicked a cell or something else
            if not manager.set_active_cell(mouse):
                if self.quit_button.is_hovered(mouse):
                    click_sound.play()
                    return router.navigate_to("main_menu")
                # if we hit confirm, fire with the manager
                if self.fire_button.is_hovered(mouse):
                    if manager.skip_turn:
                        click_sound.play()
                        manager.skip()
                        self.change_turn =True
                        self.fire_button.set_text("FIRE")
                    elif manager.active_cell is not None:
                        self.change_turn = manager.fire_shot()
                        self.coord_text.value = ""
