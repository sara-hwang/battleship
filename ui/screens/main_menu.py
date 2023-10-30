import pygame
from ui.colours import Colours
from ui.elements import make_button, make_settings_button
from ui.router import Screen
from ui.sounds import click_sound
from ui.text import Text


class MainMenu(Screen):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        manager.reset()
        text = Text("BATTLESHIP", (650, 150), 100, Colours.GOLD)
        self.play_button = make_button(650, 350, "PLAY", 75, reactive=True)
        self.quit_button = make_button(650, 550, "QUIT", 75, reactive=True)
        self.volume_button = make_settings_button()

        self.button_array = [self.quit_button, self.play_button, self.volume_button]
        self.text_array = [text]

    def handle_event(self, event, mouse, router, manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.volume_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("volume")
            if self.play_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("select_opponent")
            if self.quit_button.is_hovered(mouse):
                click_sound.play()
                router.quit_game()
