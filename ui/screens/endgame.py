import pygame
from ui.colours import Colours
from ui.elements import make_button, make_settings_button
from ui.router import Screen
from ui.text import Text
from ui.sounds import click_sound


class Endgame(Screen):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.draw_background = True

        endgame_title = Text(
            "Congratulations, you won!" if manager.won else "You lost, try again..",
            (650, 150),
            80,
            Colours.GOLD,
        )

        self.main_menu_button = make_button(650, 600, "Main Menu", 75, reactive=True)
        self.volume_button = make_settings_button()

        self.text_array = [endgame_title]
        self.button_array = [self.main_menu_button, self.volume_button]

    def handle_event(self, event, mouse, router, manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.volume_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("volume")
            if self.main_menu_button.is_hovered(mouse):
                click_sound.play()
                router.navigate_to("main_menu")
