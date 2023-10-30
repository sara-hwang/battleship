from game_config import DEFAULT_SIZE, START_SIZE
import pygame
from game_manager import AIDifficulty
from ui.colours import Colours
from ui.elements import make_back_button, make_button, confirm_button_image, confirm_button_select, make_settings_button
from ui.router import Screen
from ui.sounds import click_sound
from ui.text import Text


class Size(Screen):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.draw_background = True

        size_text = Text("Board Size", (650, 100), 40, Colours.GOLD)
        self.x4_button = make_button(
            350, 175, "4x4", 20, image=confirm_button_image)
        self.x5_button = make_button(
            650, 175, "5x5", 20, image=confirm_button_image)
        self.x6_button = make_button(
            950, 175, "6x6", 20, image=confirm_button_image)
        self.x7_button = make_button(
            350, 250, "7x7", 20, image=confirm_button_image)
        self.x8_button = make_button(
            650, 250, "8x8", 20, image=confirm_button_image)
        self.x9_button = make_button(
            950, 250, "9x9", 20, image=confirm_button_image)

        ships_text = Text("Number of Ships", (650, 350), 40, Colours.GOLD)
        self.ships4_button = make_button(
            350, 425, "4", 20, image=confirm_button_image)
        self.ships5_button = make_button(
            650, 425, "5", 20, image=confirm_button_image)
        self.ships6_button = make_button(
            950, 425, "6", 20, image=confirm_button_image)
        self.ships7_button = make_button(
            350, 500, "7", 20, image=confirm_button_image)
        self.ships8_button = make_button(
            650, 500, "8", 20, image=confirm_button_image)
        self.ships9_button = make_button(
            950, 500, "9", 20, image=confirm_button_image)

        self.incompatible_text = Text("", (650, 565), 20, Colours.RED)
        self.next_button = make_button(650, 650, "Next", 75, reactive=True)
        self.back_button = make_back_button()
        self.volume_button = make_settings_button()

        self.ship_buttons = [self.ships4_button,
                             self.ships5_button,
                             self.ships6_button,
                             self.ships7_button,
                             self.ships8_button,
                             self.ships9_button]
        self.size_buttons = [self.x4_button,
                             self.x5_button,
                             self.x6_button,
                             self.x7_button,
                             self.x8_button,
                             self.x9_button]
        self.button_array = [self.back_button,
                             self.volume_button,
                             self.next_button] + self.ship_buttons + self.size_buttons
        self.text_array = [size_text, ships_text, self.incompatible_text]

        self.ship_buttons[DEFAULT_SIZE -
                          START_SIZE].set_image(confirm_button_select)
        self.size_buttons[DEFAULT_SIZE -
                          START_SIZE].set_image(confirm_button_select)

    def handle_event(self, event, mouse, router, manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.ship_buttons:
                if button.is_hovered(mouse):
                    if not self.check_compatible(self.ship_buttons.index(button) + START_SIZE, manager.board_size):
                        self.incompatible_text.value = "Too many ships for the selected board size!"
                        break
                    click_sound.play()
                    self.incompatible_text.value = ""
                    self.ship_buttons[manager.num_ships -
                                      START_SIZE].set_image(confirm_button_image)
                    button.set_image(confirm_button_select)
                    manager.num_ships = self.ship_buttons.index(
                        button) + START_SIZE
            for button in self.size_buttons:
                if button.is_hovered(mouse):
                    if not self.check_compatible(manager.num_ships, self.size_buttons.index(button) + START_SIZE):
                        self.incompatible_text.value = "Too small of a board size for the selected number of ships!"
                        break
                    click_sound.play()
                    self.incompatible_text.value = ""
                    self.size_buttons[manager.board_size -
                                      START_SIZE].set_image(confirm_button_image)
                    button.set_image(confirm_button_select)
                    manager.board_size = self.size_buttons.index(
                        button) + START_SIZE
            if self.next_button.is_hovered(mouse):
                click_sound.play()
                if manager.ai_game:
                    manager.create_ai_game()
                    return router.navigate_to("placement")
                else:
                    manager.create_online_game(True)
                    return router.navigate_to("online_create_pending")
            if self.volume_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("volume")
            if self.back_button.is_hovered(mouse):
                click_sound.play()
                manager.num_ships = DEFAULT_SIZE
                manager.board_size = DEFAULT_SIZE
                return router.navigate_back()

    def check_compatible(self, num_ships, board_size):
        if board_size == 4 and num_ships > 6:
            return False
        if board_size == 5 and num_ships > 8:
            return False
        return True
