import string
import pygame
from client import Stages
from ui.colours import Colours
from ui.elements import make_back_button, make_button, make_settings_button
from ui.input import Input
from ui.router import Screen
from ui.sounds import click_sound
from ui.text import Text


class OnlineJoin(Screen):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.draw_background = True
        self.code_input = Input(max_length=9)

        self.back_button = make_back_button()
        self.volume_button = make_settings_button()

        join_title = Text("Join game", (650, 300), 50, Colours.GOLD)
        join_desc = Text("Enter an invite code to join a game", (650, 375), 30, Colours.WHITE)

        self.code_chars = Text("_________", (650, 425), 30, Colours.GOLD)

        self.join_button = make_button(650, 550, "Join", 50, reactive=True)

        self.text_array = [join_title, join_desc, self.code_chars]
        self.button_array = [self.back_button, self.volume_button, self.join_button]

    async def render(self, mouse, router, manager):
        if manager.client.stage == Stages.PLACEMENT:
            manager.create_online_game(False)
            return router.navigate_to("placement")
        if manager.client.stage == Stages.PENDING_OPPONENT_JOIN:
            return router.navigate_to("online_create_pending")
        self.code_chars.value = " ".join(self.code_input.value.ljust(9, "_"))
        if manager.client.error != None:
            return router.navigate_to("error")

    def handle_event(self, event, mouse, router, manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_back()
            if self.join_button.is_hovered(mouse) and len(self.code_input.value) == 9:
                click_sound.play()
                manager.client.join_game(self.code_input.value)
                return
            if self.volume_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("volume")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.code_input.backspace()
            elif event.key == pygame.K_RETURN and len(self.code_input.value) == 9:
                manager.client.join_game(self.code_input.value)
            elif event.unicode in string.ascii_letters + string.digits:
                self.code_input.input(event.unicode.upper())
