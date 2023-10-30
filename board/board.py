import math
import pygame
import random
import string

from board.board_factory import BoardFactory
from ui.fonts import get_font

sea = pygame.image.load("assets/Sea.png")
sea.set_alpha(170)
class Board:
    # number of ships on the board
    __nships = 0

    # array of ships on this board
    __ships = []

    # size of this board
    __size = 0

    # array of cells on this board
    __cells = []

    # factory for board setup
    __board_factory = None

    # coordinates where this board should be drawn
    __coordinates = None

    # track the size of the rectangle representing the board
    __width = 0

    # On my board, I want to display the ships' locations.
    # On the opponent's board, I do not
    __display = False

    __foreign = False

    """
    coordinates is a tuple (x, y) that represents the location
    of the board's top left corner when you draw it on the screen

    width is a number that represents the number of pixels in one
    side length of the board
    """

    def __init__(self, size, num_ships, coords, width, display, foreign=False):
        self.__nships = num_ships
        self.__size = size

        self.__coordinates = coords
        self.__width = width
        self.__display = display
        self.__foreign = foreign

        self.__board_factory = BoardFactory(
            self.__size, self.__nships, self.__coordinates, self.__width
        )

    def build_board(self):
        self.__cells = self.__board_factory.create_cells(self.__foreign)
        self.__ships = self.__board_factory.create_ships()

    def get_size(self):
        return self.__size

    def get_num_ships(self):
        return self.__nships

    def get_placement_data(self):
        cells_in_ships = [[] for ship in self.__ships]
        for col in self.__cells:
            for cell in col:
                if cell.ship != None:
                    cells_in_ships[self.__ships.index(cell.ship)].append(cell.coordinates)
        return cells_in_ships

    def get_ship(self, idx: int):
        if self.__ships is not None:
            return self.__ships[idx]

    # For testing purposes. Print all the cells in the board
    def print_cells(self):
        col = 0
        for column in self.__cells:
            print("Column", col)

            for cell in column:
                cell.print_cell()

            col += 1
    def place_pirate(self):
        num_pirates=self.__size-3
        for i in range(1, num_pirates+1):
            occupied =False
            while not occupied:
                x=random.randint(0,self.__size-1)
                y=random.randint(0,self.__size-1)
                conflict = False
                if x<self.__size and y <self.__size:
                    cell = self.__cells[x][y]
                    if cell.ship!= None:
                        conflict=True
                else:
                    conflict=True
            
                if not conflict:
                    if cell.ship==None:
                        cell.set_pirate()
                        occupied=True
        
    def place_ships(self, num_ships=None):
        """
        Place each ship in a random, legal position
        num_ships is number of ships left to place
        """
        if num_ships is None:
            num_ships = self.__nships
        for i in range(1, num_ships + 1):
            current_ship = self.__ships[-(self.__nships - num_ships + i)]

            occupied = False

            # Place a ship in a random spot
            while not occupied:
                x = random.randint(0, self.__size - 1)
                y = random.randint(0, self.__size - 1)

                """
                We begin at cell (x, y) and explore in either the horizontal
                or vertical direction for the size of the ship

                We obtain a list of all cells that would be occupied by the
                ship, starting with its head at cell (x, y).

                If all such cells are legal (no conflicts), we place the ship
                there

                A cell is NOT legal if:
                    - it exceeds the boundaries of the board
                    - the cell already contains a ship
                """
                current_ship.vertical = True
                conflict = False
                cells: list[tuple[int, int]] = []
                for j in range(current_ship.get_size()):
                    cells.append((x, y + j))

                for c in cells:
                    if c[0] < self.__size and c[1] < self.__size:
                        cell = self.__cells[c[0]][c[1]]
                        if cell.ship != None:
                            conflict = True
                    else:
                        conflict = True

                if conflict:
                    current_ship.vertical = False
                    # If there are conflicts, explore in the other direction
                    conflict = False
                    cells = []
                    for j in range(current_ship.get_size()):
                        cells.append((x + j, y))

                    for c in cells:
                        if c[0] < self.__size and c[1] < self.__size:
                            cell = self.__cells[c[0]][c[1]]
                            if cell.ship != None:
                                conflict = True
                        else:
                            conflict = True

                # place ships if possible
                if not conflict:
                    for index, c in enumerate(cells):
                        if c[0] < self.__size and c[1] < self.__size:
                            cell = self.__cells[c[0]][c[1]]
                            if cell.ship == None:
                                cell.set_ship(current_ship)
                                cell.set_index(index)
                                occupied = True
                                # print("Place a size "+ str(current_ship.get_size()) + " ship on coords " + str(c[0]) + "," + str(c[1]))

    def draw_board(self, screen: pygame.Surface,display=False):
        """
        location is the coordinates of the top left corner

        rect_size is the size of the total square

        We need to evenly divide rect_size into self._size
        equal segments.

        screen is the screen on which we draw


        UPDATE: i am storing this all in a data member so no need
        """
        # square_size = rect_size / self._size

        """
        So, now we have the sqaure sizes. We draw them
        in columns

        x_0 and y_0 are the coords of the top left corner
        of the board
        """
        x_0 = self.__coordinates[0]
        y_0 = self.__coordinates[1]
        sea_bg = pygame.Surface.convert_alpha(sea)
        sea_bg = pygame.transform.scale(sea_bg, (self.__width, self.__width))
        screen.blit(sea_bg, (x_0, y_0))
        # draw the board labels
        self.draw_labels(screen)
        for i in range(self.__size):
            for j in range(self.__size):
                """
                cell.draw_cell() takes the following arguments:

                screen is the screen on which we want to draw it

                display is the boolean toggle if we should draw
                the unhit ships
                """
                cell = self.__cells[i][j]
                if not display:
                    cell.draw_cell(screen, self.__display)
                else:
                    cell.draw_cell(screen, display)


    def draw_labels(self, screen: pygame.Surface):
        """
        Draw the labels on the side of the board

        Create the necessary texts first

        The location in which we draw the row labels
        is determined by the cell center of the cells
        in the self._cells[0]

        the location in which we draw the col labels
        is determined by the cell center of the cell
        at self._cells[j][0]
        """

        row_labels = []
        row_rects = []

        col_labels = []
        col_rects = []

        for i in range(self.__size):
            location = list(self.__cells[0][i].get_cell_center())
            # Translate it a little to the left
            location[0] -= 0.7 * self.__cells[0][i].get_width()

            text = get_font(15).render("{}".format(i + 1), True, "White")
            rect = text.get_rect(center=location)
            row_labels.append(text)
            row_rects.append(rect)

            location2 = list(self.__cells[i][0].get_cell_center())
            # Translate it a little to the left
            location2[1] -= 0.7 * self.__cells[i][0].get_width()

            text2 = get_font(15).render("{}".format(string.ascii_uppercase[i]), True, "White")
            rect2 = text.get_rect(center=location2)
            col_labels.append(text2)
            col_rects.append(rect2)

        # Draw all teh texts and rects
        for j in range(self.__size):
            screen.blit(row_labels[j], row_rects[j])
            screen.blit(col_labels[j], col_rects[j])

    def get_cell(self, col: int, row: int):
        return self.__cells[col][row]

    def get_cell_mouse(self, mouse_pos: tuple[int, int]):
        """
        Given the position of a mouse, find a cell in self._cells
        such that the mouse collides with the cell.

        Returns None if the mouse does not collide with any cell
        """
        cell_size = self.__width / self.__size
        row: int = math.floor((mouse_pos[1] - self.__coordinates[1]) / cell_size)
        column: int = math.floor((mouse_pos[0] - self.__coordinates[0]) / cell_size)
        if (
            row < 0
            or column < 0
            or row >= self.__size
            or column >= self.__size
            or self.__cells[column][row].is_hit
            or self.__cells[column][row].is_guessed
        ):
            return None

        return self.__cells[column][row]

    def gameover(self):
        return all(ship.sunk() for ship in self.__ships)
