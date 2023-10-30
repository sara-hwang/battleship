import pygame


# Returns specified font in the desired size
def get_font(size, font="Georgia"):
    if font == "Georgia":
        return pygame.font.Font("assets/fonts/Georgia.ttf", size)
    if font == "Helvetica":
        return pygame.font.Font("assets/fonts/Helvetica.ttf", size)
