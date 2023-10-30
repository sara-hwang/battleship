import pygame
from game_manager import AIDifficulty
from ui.colours import Colours
from ui.elements import make_back_button, make_button, confirm_button_image, make_settings_button
from ui.router import Screen
from ui.sounds import click_sound
from ui.text import Text


class AIConfiguration(Screen):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.draw_background = True
        text = Text("Difficulty", (650, 100), 50, Colours.GOLD)
        self.back_button = make_back_button()
        self.easy_button = make_button(650, 200, "Easy", 20, image=confirm_button_image)
        self.med_button = make_button(650, 300, "Medium", 20, image=confirm_button_image)
        self.hard_button = make_button(650, 400, "Hard", 20, image=confirm_button_image)
        self.volume_button = make_settings_button()

        self.button_array = [self.back_button, 
                             self.volume_button, 
                             self.easy_button, 
                             self.med_button, 
                             self.hard_button]
        self.text_array = [text]

    def handle_event(self, event, mouse, router, manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.easy_button.is_hovered(mouse):
                click_sound.play()
                manager.set_ai_difficulty(AIDifficulty.EASY)
                return router.navigate_to("size")
            if self.med_button.is_hovered(mouse):
                click_sound.play()
                manager.set_ai_difficulty(AIDifficulty.MEDIUM)
                return router.navigate_to("size")
            if self.hard_button.is_hovered(mouse):
                click_sound.play()
                manager.set_ai_difficulty(AIDifficulty.HARD)
                return router.navigate_to("size")
            if self.volume_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("volume")
            if self.back_button.is_hovered(mouse):
                click_sound.play()
                manager.set_ai_difficulty(None)
                return router.navigate_back()
