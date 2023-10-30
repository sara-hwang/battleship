import pygame
from ui.elements import make_button, make_back_button, make_settings_button
from ui.router import Screen
from ui.sounds import click_sound


class SelectOpponent(Screen):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.draw_background = True
        self.play_button_ai = make_button(650, 150, "Play vs. AI", 50, reactive=True)
        self.play_button_human = make_button(650, 350, "Play vs. Human", 50, reactive=True)
        self.back_button = make_back_button()
        self.volume_button = make_settings_button()

        self.button_array = [self.back_button, 
                             self.volume_button, 
                             self.play_button_human, 
                             self.play_button_ai]

    def handle_event(self, event, mouse, router, manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_button_ai.is_hovered(mouse):
                click_sound.play()
                manager.set_ai_game(True)
                return router.navigate_to("ai_configuration")
            if self.play_button_human.is_hovered(mouse):
                click_sound.play()
                manager.set_ai_game(False)
                return router.navigate_to("online_game_options")
            if self.volume_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("volume")
            if self.back_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_back()
