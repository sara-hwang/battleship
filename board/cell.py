from time import sleep
from game_config import FLASH_DURATION, NUM_FLASHES
import pygame

from ui.colours import Colours
from ui.fonts import get_font
from ships.normal_ship import Ship
from ships.pirate import Pirate
ship_1x1 = pygame.image.load("assets/ships/ship_1x1.png")
ship_head = pygame.image.load("assets/ships/ship_head.png")
ship_middle = pygame.image.load("assets/ships/ship_middle.png")
ship_tail = pygame.image.load("assets/ships/ship_tail.png")
X_img = pygame.image.load("assets/X.png")
X_invert = pygame.image.load("assets/Xinvert.png")
Dash_img = pygame.image.load("assets/Dash.png")
pirate_flag = pygame.image.load("assets/ships/Pirate_Flag.png")


class Cell:
    coordinates: tuple[int, int] = (0, 0)
    ship: Ship | None = None
    is_guessed: bool = False
    is_hit: bool = False
    foreign: bool = False
    index: int = -1
    flash: int = 0

    # for drawing purposes. the side length and location of the cell
    __width = 0
    __location = None
    __bigMarkingSize = 64
    __smallMarkingSize = 48
    """
    width represents a number of pixels that is the side length
    of the cell when you draw it on the screen

    location is a tuple (x, y) that represents the coordinates of
    the top left corner of the cell when it is drawn on teh screen
    """

    def __init__(self, coords, width, location, foreign=False) -> None:
        self.coordinates = coords
        self.foreign = foreign
        self.__width = width
        self.__location = location
        self.__bigMarkingSize = int(width/1.2)
        self.__smallMarkingSize = int(width/1.2)

    def set_ship(self, ship: Ship):
        self.ship = ship

    def set_index(self, index: int):
        self.index = index

    def hit(self, flash) -> bool:
        self.is_guessed = True

        if self.ship == None:
            return False

        self.is_hit = True
        self.flash = NUM_FLASHES if flash else 0
        self.ship.hit()

        return True

    def multiplayer_hit(self, hit: bool):
        self.is_guessed = True
        self.is_hit = hit

    def print_cell(self):
        print("Coords:", self.coordinates, "Hit?",
              self.is_hit, "Ship?", self.ship != None)

    def draw_cell(self, screen: pygame.Surface, display):
        """
        x, y are the coordinate of the top left corner
        of the cell.

        self_width is the side length (pixels) of the cell

        screen is the screen on which we draw

        display indicates if we should draw unhit
        ship cells differently. This would be done
        on my board only, not the opponenets board
        """
        markingSize = self.__smallMarkingSize if display else self.__bigMarkingSize

        x = self.__location[0]
        y = self.__location[1]

        cell = pygame.Rect(x, y, self.__width, self.__width)

        # Get the center of the cell
        cell_center = self.get_cell_center()
        # if display, draw unhit ships differently
        if display and self.ship is not None and self.is_hit == False:
            if self.ship.ispirate():
                ship = pirate_flag
            elif self.ship.get_size() == 1:
                ship = ship_1x1
            elif self.index == 0:
                ship = ship_head
            elif self.index == self.ship.get_size() - 1:
                ship = ship_tail
            else:
                ship = ship_middle
            ship = pygame.Surface.convert_alpha(ship)
            ship = pygame.transform.scale(ship, (self.__width, self.__width))
            if not self.ship.vertical:
                ship = pygame.transform.rotate(ship, 90)
            screen.blit(ship, self.get_cell_corner())
            pygame.draw.rect(screen, Colours.GOLD.value, cell, 1)

        # draw a cell that has not been fired on
        elif not self.is_guessed:
            pygame.draw.rect(screen, Colours.GOLD.value, cell, 2)

        # draw a cell that has been fired on without hitting a ship
        elif not self.is_hit:
            # draw the square yellow
            pygame.draw.rect(screen, Colours.GOLD.value, cell, 2)
            # draw the dash
            Dash = pygame.Surface.convert_alpha(Dash_img)
            Dash = pygame.transform.scale(Dash, (self.__width, self.__width))
            screen.blit(Dash, self.get_cell_corner())
        # draw hit pirates
        elif self.ship != None and self.ship.ispirate() and self.is_hit:
            ship = pirate_flag
            ship = pygame.Surface.convert_alpha(ship)
            ship = pygame.transform.scale(ship, (self.__width, self.__width))
            screen.blit(ship, self.get_cell_corner())
            X = pygame.Surface.convert_alpha(X_img)
            X = pygame.transform.scale(X, (self.__width, self.__width))
            screen.blit(X, self.get_cell_corner())
        # draw a cell that has been fired on hitting a ship
        else:
            if self.ship is not None and display:
                if self.ship.ispirate():
                    ship = pirate_flag
                elif self.ship.get_size() == 1:
                    ship = ship_1x1
                elif self.index == 0:
                    ship = ship_head
                elif self.index == self.ship.get_size() - 1:
                    ship = ship_tail
                else:
                    ship = ship_middle
                ship = pygame.Surface.convert_alpha(ship)
                ship = pygame.transform.scale(
                    ship, (self.__width, self.__width))
                if not self.ship.vertical:
                    ship = pygame.transform.rotate(ship, 90)
                screen.blit(ship, self.get_cell_corner())
                pygame.draw.rect(screen, Colours.GOLD.value, cell, 1)

            pygame.draw.rect(screen, Colours.GOLD.value, cell, 2)
            # draw the X
            X = pygame.Surface.convert_alpha(X_img)
            X = pygame.transform.scale(X, (self.__width, self.__width))
            Xi = pygame.Surface.convert_alpha(X_invert)
            Xi = pygame.transform.scale(Xi, (self.__width, self.__width))

            if self.flash > 0:
                if self.flash % 2 == 1:
                    screen.blit(Xi, self.get_cell_corner())
                else:
                    screen.blit(X, self.get_cell_corner())
                sleep(FLASH_DURATION)
                self.flash -= 1
            else:
                screen.blit(X, self.get_cell_corner())

    def draw_selected_cell(self, screen):
        # Draw a special cell that has been selected
        x = self.__location[0]
        y = self.__location[1]

        cell = pygame.Rect(x, y, self.__width, self.__width)

        # Get the center of the cell
        cell_center = self.get_cell_center()

        # Draw teh cell in green
        pygame.draw.rect(screen, "Green", cell, int(self.__width/10))

        # Draw its marking
        question_text = get_font(
            self.__bigMarkingSize, "Helvetica").render("?", True, "Green")
        question_rect = question_text.get_rect(
            center=(cell_center[0], cell_center[1]+int(self.__width/12)))
        screen.blit(question_text, question_rect)

    def draw_cell_color(self, screen, color):
        # Draw this cell on the specified screen in the specifed color
        # Draw a special cell that has been selected
        x = self.__location[0]
        y = self.__location[1]

        cell = pygame.Rect(x, y, self.__width, self.__width)

        # Get the center of the cell
        cell_center = self.get_cell_center()

        pygame.draw.rect(screen, color, cell, int(self.__width / 10))

        question_text = get_font(
            self.__bigMarkingSize, "Helvetica").render("?", True, color)
        question_rect = question_text.get_rect(
            center=(cell_center[0], cell_center[1] + int(self.__width / 12)))
        screen.blit(question_text, question_rect)

    def get_cell_center(self):
        return (
            self.__location[0] + (0.5 * self.__width),
            self.__location[1] + (0.5 * self.__width),
        )

    def get_cell_corner(self):
        return (self.__location[0], self.__location[1])

    def get_width(self):
        return self.__width

    def checkpirate(self):
        self.is_guessed = True
        if self.ship == None:
            return False
        if self.ship.ispirate():
            print("true")
            return True
        return False

    def get_ispirate(self):
        return self.ship.ispirate()

    def set_pirate(self):
        if self.ship != None:
            return False
        self.ship = Pirate(1)
        return True
