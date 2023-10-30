import pygame
from ui.colours import Colours
from ui.fonts import get_font
from dataclasses import dataclass


@dataclass
class Text:
    value: str
    pos: tuple[int, int]
    size: int
    colour: Colours

    def render(self, screen: pygame.Surface):
        text_rendered = get_font(self.size).render(self.value, True, self.colour.value)
        text_rect = text_rendered.get_rect(center=self.pos)
        screen.blit(text_rendered, text_rect)
