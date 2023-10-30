import pygame
from client import Stages
from ui.colours import Colours
from ui.elements import make_back_button, make_button, make_settings_button
from ui.router import Screen
from ui.text import Text
from ui.sounds import click_sound

class Error(Screen):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.draw_background = True

        error_title = Text(
            "Error",
            (650, 150),
            100,
            Colours.GOLD,
        )
        error_text = Text(manager.client.error, (650, 300), 50, Colours.WHITE)
        self.volume_button = make_settings_button()

        self.text_array = [error_title, error_text]
        if manager.client.error == "Invalid invite code":
            self.quit_button = None
            self.back_button = make_back_button()
            self.button_array = [self.volume_button, self.back_button]
        else:
            self.quit_button = make_button(650, 600, "QUIT", 75, reactive=True)
            self.back_button = None
            self.button_array = [self.volume_button, self.quit_button]

    def handle_event(self, event, mouse, router, manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.volume_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("volume")
            if self.quit_button != None and self.quit_button.is_hovered(mouse):
                click_sound.play()
                router.quit_game()
            if self.back_button != None and self.back_button.is_hovered(mouse):
                click_sound.play()
                manager.client.error = None
                manager.client.stage = Stages.WAITING_FOR_CODE
                router.navigate_back()
