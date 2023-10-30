import pygame
from client import Stages
from ui.colours import Colours
from ui.elements import quit_button_image, make_button, make_settings_button
from ui.router import Screen
from ui.sounds import click_sound
from ui.text import Text


class OnlineCreatePending(Screen):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.draw_background = True
        self.quit_button = make_button(1000, 25, "QUIT", 20, image=quit_button_image)
        self.volume_button = make_settings_button()

        waiting_title = Text("Waiting for opponent", (650, 300), 50, Colours.GOLD)
        waiting_text = Text(
            "You can invite a friend to this game with the code below",
            (650, 375),
            30,
            Colours.WHITE,
        )

        self.code_text = Text("", (650, 425), 30, Colours.GOLD)

        self.text_array = [waiting_title, waiting_text, self.code_text]
        self.button_array = [self.quit_button, self.volume_button]

    async def render(self, mouse, router, manager) -> None:
        if manager.client.stage == Stages.PLACEMENT:
            return router.navigate_to("placement")
        self.code_text.value = (
            manager.client.code
            if manager.client != None and manager.client.code != ""
            else "Loading... (If you keep seeing this, please check your internet connection)"
        )

    def handle_event(self, event, mouse, router, manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.volume_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("volume")
            if self.quit_button.is_hovered(mouse):
                click_sound.play()
                manager.reset()
                router.navigate_to("main_menu")
