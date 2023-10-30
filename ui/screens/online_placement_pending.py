import pygame
from client import Stages
from ui.colours import Colours
from ui.elements import make_button, make_settings_button, quit_button_image
from ui.router import Screen
from ui.sounds import click_sound
from ui.text import Text


class OnlinePlacementPending(Screen):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.draw_background = True
        self.quit_button = make_button(1000, 25, "QUIT", 20, image=quit_button_image)
        self.volume_button = make_settings_button()

        waiting_title = Text("Waiting for opponent", (650, 350), 50, Colours.GOLD)
        waiting_text = Text(
            "Please wait while your opponent places their ships",
            (650, 425),
            30,
            Colours.WHITE,
        )

        self.text_array = [waiting_title, waiting_text]
        self.button_array = [self.quit_button, self.volume_button]

    async def render(self, mouse, router, manager) -> None:
        if manager.client.error != None:
            return router.navigate_to("error")
        if manager.client.stage == Stages.PLAY:
            return router.navigate_to("play")

    def handle_event(self, event, mouse, router, manager):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.volume_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("volume")
            if self.quit_button.is_hovered(mouse):
                click_sound.play()
                return router.navigate_to("main_menu")
