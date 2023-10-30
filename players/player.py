from board.board import Board

class Player:
    def __init__(
        self, ship_count, game_size, coords=(850, 375), width=300, display=True, foreign=False
    ):
        self.__miss_next_turn: False
        self.board = Board(
            size=game_size,
            num_ships=ship_count,
            coords=coords,
            width=width,
            display=display,
            foreign=foreign,
        )
        self.large_board = Board(
            size=self.board.get_size(),
            num_ships=self.board.get_num_ships(),
            coords=(150, 150),
            width=550,
            display=True,
            foreign=foreign,
        )
        self.large_board.build_board()
        self.board.build_board()

    def init_ships(self) -> bool:
        self.board.place_ships()
        # self.board.print_cells()

    def use_ability(self) -> bool:
        pass

    # Large board is needed for the placement screen since we have the player board of a fixed size
    def draw_large_board(self, screen,display=False):
        if not display:
            self.large_board.draw_board(screen)
        else:
            self.large_board.draw_board(screen,display=display)
