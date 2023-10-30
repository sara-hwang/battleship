import pygame

"""
CITATION: This button class is based on code from https://github.com/baraltech/Menu-System-PyGame

as introduced in this YouTube video: https://www.youtube.com/watch?v=GMBqjxcKogA
"""


class Button:
    def __init__(self, pos: tuple[int, int], image: pygame.Surface) -> None:
        self.pos = pos
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.image = image
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def render(self, screen, mouse_position) -> None:
        if self.image is not None:
            screen.blit(self.image, self.rect)

    def is_hovered(self, position) -> bool:
        return position[0] in range(self.rect.left, self.rect.right) and position[1] in range(
            self.rect.top, self.rect.bottom
        )

    def on_click(self, position):
        pass


class ButtonDecorator(Button):
    def __init__(self, button: Button) -> None:
        super().__init__(button.pos, button.image)
        self._button = button

    @property
    def button(self) -> Button:
        return self._button

    def render(self) -> None:
        return self._button.render()


class TextButton(ButtonDecorator):

    def __init__(self, button: Button, text: str, font: pygame.font.Font) -> None:
        super().__init__(button)
        self.__text = text
        self.__font = font

    def set_image(self, image):
        self.button.image = image

    @property
    def text(self):
        return self.__text

    def set_text(self, value: str):
        self.__text = value

    @property
    def font(self):
        return self.__font

    @font.setter
    def set_font(self, value: pygame.font.Font):
        self.__font = value

    def render(self, screen: pygame.Surface, mouse_position: tuple[int, int]):
        self.button.render(screen, mouse_position)
        self._rendered_text: pygame.Surface = self.__font.render(self.__text, True, "White")
        self._text_rect = self._rendered_text.get_rect(center=self.button.pos)
        screen.blit(self._rendered_text, self._text_rect)


class ReactiveButton(ButtonDecorator):
    def __init__(
        self,
        button: Button,
        hover_surface: pygame.Surface,
        active_surface: pygame.Surface,
    ) -> None:
        super().__init__(button)
        self.hover_surface = hover_surface
        self.active_surface = active_surface

    @property
    def hover_surface(self):
        return self._hover_surface

    @hover_surface.setter
    def hover_surface(self, surface: pygame.Surface):
        self._hover_surface = surface
        self._hover_rect = self._hover_surface.get_rect(center=self.button.pos)

    @property
    def active_surface(self):
        return self._active_surface

    @active_surface.setter
    def active_surface(self, surface: pygame.Surface):
        self._active_surface = surface
        self._active_rect = self._active_surface.get_rect(center=self.button.pos)

    def render(self, screen: pygame.Surface, mouse_position: tuple[int, int]):
        if self.is_hovered(mouse_position):
            screen.blit(self.hover_surface, self._hover_rect)
        else:
            self.button.render(screen, mouse_position)
