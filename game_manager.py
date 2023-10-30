import asyncio
from enum import Enum
from board.cell import Cell
from client import Client
from game_config import DEFAULT_SIZE, DEFAULT_VOLUME, MAX_VOLUME, MIN_VOLUME
from players.opponent import Opponent
from players.player import Player
from players.ai import EasyAI, AI, HardAI, MedAI

import pygame
from pygame.locals import *
from ships.normal_ship import NormalShip
from ships.pirate import Pirate
from ui.sounds import miss_sound, hit_sound, click_sound, fire_sound, pirate_sound
from utilities import Turn


class AIDifficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2


SCREEN_SIZE = (1300, 800)

SCREEN = pygame.display.set_mode(SCREEN_SIZE)


class GameManager:
    """
    create two instances of board
    sends coords between boards
    passes turn
    """

    """
    manager will check if a miss is returned and flip boolean if no ships are hit
    0=game over 
    1= player1 
    2=player2
    """

    client = None
    won = False

    # singleton class
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(GameManager, cls).__new__(cls)
        return cls.instance

    async def start_client(self, stop: asyncio.Future):
        self.client = Client(self)
        print("manager attempting to start client (for real)")
        await self.client.start(stop)

    def get_player(self, player_ID):
        if player_ID == 1:
            return self.__player1
        if player_ID == 2:
            return self.__player2
        else:
            return None

    def create_online_game(self, creating_game: bool):
        if self.client == None:
            raise Exception("Multiplayer client must be started first!")
        print(f"{'Creating' if creating_game else 'Joining'} online game")
        self.game_over = False
        self.turn = Turn.PLAYER_ONE if creating_game else Turn.PLAYER_TWO
        self.run = True
        self.won = False
        self.ai_difficulty = None
        self.skip_turn = False
        self.p2_skip_turn = False
        self.__player1 = Player(self.num_ships, self.board_size)
        self.__player2 = Opponent(self.num_ships, self.board_size)
        self.client.identify()
        if creating_game:
            self.client.create_game(self.num_ships, self.board_size)
        self.active_cell = None

    def create_ai_game(self):
        print("creating AI game")
        self.game_over = False
        self.turn = Turn.PLAYER_ONE
        self.run = True
        self.won = False
        self.skip_turn = False
        self.p2_skip_turn = False

        self.__player1 = Player(self.num_ships, self.board_size)
        match self.ai_difficulty:
            case AIDifficulty.EASY:
                self.__player2 = EasyAI(self.num_ships, self.board_size)
            case AIDifficulty.MEDIUM:
                self.__player2 = MedAI(self.num_ships, self.board_size)
            case AIDifficulty.HARD:
                self.__player2 = HardAI(
                    self.num_ships, self.board_size, self.__player1)
            case _:
                print("Invalid AI Difficulty")
        self.active_cell = None

    def reset(self, init=False):
        self.board_size = DEFAULT_SIZE
        self.num_ships = DEFAULT_SIZE
        self.ai_difficulty = None
        self.client = None
        self.__player1 = None
        self.__player2 = None
        if init:
            self.animations = True
            self.volumes = {}
            self.volumes["bg"] = DEFAULT_VOLUME
            self.volumes["sfx"] = DEFAULT_VOLUME
            self.volumes["click"] = DEFAULT_VOLUME
            self.premute_volumes = {}
            self.premute_volumes["bg"] = DEFAULT_VOLUME
            self.premute_volumes["sfx"] = DEFAULT_VOLUME
            self.premute_volumes["click"] = DEFAULT_VOLUME
            hit_sound.set_volume(self.volumes["sfx"] * 0.1)
            miss_sound.set_volume(self.volumes["sfx"] * 0.1)
            fire_sound.set_volume(self.volumes["sfx"] * 0.1)
            pirate_sound.set_volume(self.volumes["sfx"] * 0.1)
            click_sound.set_volume(self.volumes["click"] * 0.1)

    def change_volume(self, type, increase=True, mute=False, unmute=False):
        if mute:
            self.premute_volumes[type] = self.volumes[type]
            self.volumes[type] = 0
        elif unmute:
            self.volumes[type] = self.premute_volumes[type]
            self.premute_volumes[type] = DEFAULT_VOLUME
        elif increase:
            self.volumes[type] = min(self.volumes[type]+1, MAX_VOLUME)
        else:
            self.volumes[type] = max(self.volumes[type]-1, MIN_VOLUME)
        pygame.mixer.music.set_volume(self.volumes["bg"] * 0.1)
        hit_sound.set_volume(self.volumes["sfx"] * 0.1)
        miss_sound.set_volume(self.volumes["sfx"] * 0.1)
        fire_sound.set_volume(self.volumes["sfx"] * 0.1)
        pirate_sound.set_volume(self.volumes["sfx"] * 0.1)
        click_sound.set_volume(self.volumes["click"] * 0.1)

    def get_volume(self, type):
        return self.volumes[type]

    def set_size(self, size):
        self.board_size = size

    def set_num_ships(self, num):
        self.num_ships = num

    def set_ai_game(self, ai_bool: bool):
        self.ai_game = ai_bool

    def set_ai_difficulty(self, difficulty: AIDifficulty):
        self.ai_difficulty = difficulty

    def hard_ai_setup(self):
        """
        HardAI wil be able to peek into its opponent's array.

        However, it is instantiated before the opponentn places
        their ships. So after the oppoennt has placed their ships,
        invoke this method to tell the hardAI where they are

        *************PRECONDITION - IMPORTANT!!!!!!!
        This function will assume __player2 is a hardAI
        if this is not the case, I make no promises to what
        this function will do
        """
        if isinstance(self.__player2, HardAI):
            self.__player2.get_opp_ships()

    def update_boards(self):
        # draw my board
        self.__player1.board.draw_board(SCREEN)
        self.__player2.board.draw_board(SCREEN)
        # Draw active cell if it is not None
        if self.active_cell is not None:
            self.active_cell.draw_selected_cell(SCREEN)

    def render_board(self, screen):
        if screen == "player1":
            self.__player1.board.draw_board(SCREEN)
        else:
            self.__player2.board.draw_board(SCREEN)

        if self.active_cell is not None:
            self.active_cell.draw_selected_cell(SCREEN)

    def update_placement(self):
        # Draw a larger board for the placement stage
        self.__player1.draw_large_board(SCREEN)
        if self.active_cell is not None:
            self.active_cell.draw_selected_cell(SCREEN)

    def update_pirate(self):
        self.__player1.draw_large_board(SCREEN, display=True)
        if self.active_cell is not None:
            self.active_cell.draw_selected_cell(SCREEN)

    def place_random(self, num_ships):
        self.active_cell = None
        self.__player1.board.place_ships(num_ships=num_ships)

    def preview_ship(self, num_left: int, vertical: bool):
        """
        This function previews the ship that is about to be placed.

        A ship will be drawn as a collection of contiguous green cells
        if the selected location is a valid place to put the ship

        If there is a conflict, the ship cells will be drawn in red

        The parameter num_left tells us which ship in the array we
        should consider

        The parameter vertical tells us the orientation of the ship
        """
        s = self.__player1.board.get_ship(num_left - self.num_ships - 1)

        cells = []

        for i in range(s.get_size()):
            if vertical:
                newcell = (
                    self.active_cell.coordinates[0],
                    self.active_cell.coordinates[1] + i,
                )
            else:
                newcell = (
                    self.active_cell.coordinates[0] + i,
                    self.active_cell.coordinates[1],
                )
            cells.append(newcell)

        """
        Check for conflicts.

        If there is a conflict,
            - set conflicts = True
            - remove the conflicting cell from the list

        I will need to iterate over a copy of the cells lsit.
        This is because we are potentially changing it as we loop,
        so the array will become messed up if we iterate 
        over the array while removing stuff from it
        """
        cellscopy = []
        for cell in cells:
            cellscopy.append(cell)

        conflicts = False

        for c in cellscopy:
            # is c out of bounds?
            # c[0] is the column. if c[0] >= the board size, we are out of bounds
            # c[1] is the row. if c[1] >= the board size, we are out of bounds
            if c[0] >= self.__player1.board.get_size():
                conflicts = True
                cells.remove(c)

            elif c[1] >= self.__player1.board.get_size():
                conflicts = True
                cells.remove(c)

            # does c already contain a ship?
            elif self.__player1.large_board.get_cell(c[0], c[1]).ship != None:
                conflicts = True

        """
        Now, draw the cells in the list 'cells'

        If conflicts = True, draw said cells in red

        Draw them in green otherwise.
        """

        for c in cells:
            color = "Red"
            if conflicts == False:
                color = "Green"

            self.__player1.large_board.get_cell(
                c[0], c[1]).draw_cell_color(SCREEN, color)

    def place_ship(self, num_left, vertical):
        """
        Create a list of cells that this ship would occupy

        let n = __player1. board.get_ship(-num_left)

        the list should be of length n.get_size()

        The first cell in the list will be active_cell
        then, proceed to add cells to the list in ascending
        order of column

        Maintain an array of cells which this ship will occupy.

        We can validate each cell before the ship is placed.
        A cell is invlid if:
            - another ship is placed there
            - its coordinates are out of bounds

        Then, place the ship into each of the cells iff all are valid

        NEW PARAMETER: vertical=True indiccates that this
        ship should be placed vertically. Set the cells as such
        """
        s = self.__player1.board.get_ship(num_left - self.num_ships - 1)
        s.set_orientation(vertical)

        cells = []

        for i in range(s.get_size()):
            if vertical:
                newcell = (
                    self.active_cell.coordinates[0],
                    self.active_cell.coordinates[1] + i,
                )
            else:
                newcell = (
                    self.active_cell.coordinates[0] + i,
                    self.active_cell.coordinates[1],
                )
            cells.append(newcell)

        # validate each cell
        # if any cell is invalid, return False
        for c in cells:
            # is c out of bounds?
            # c[0] is the column. if c[0] >= the board size, we are out of bounds
            # c[1] is the row. if c[1] >= the board size, we are out of bounds
            if c[0] >= self.__player1.board.get_size():
                self.active_cell = None
                return False

            if c[1] >= self.__player1.board.get_size():
                self.active_cell = None
                return False
            # does c already contain a ship?
            if self.__player1.large_board.get_cell(c[0], c[1]).ship != None:
                self.active_cell = None
                return False

        # set the ship in each cell
        for i, c in enumerate(cells):
            self.__player1.board.get_cell(c[0], c[1]).set_ship(s)
            self.__player1.board.get_cell(c[0], c[1]).set_index(i)
            self.__player1.large_board.get_cell(c[0], c[1]).set_ship(s)
            self.__player1.large_board.get_cell(c[0], c[1]).set_index(i)

        self.active_cell = None

        """
        if self.active_cell:
            self.active_cell.ship = s
            # place the ships onto the large board and then copy the ship to the small board


            self.__player1.board.get_cell(self.active_cell.coordinates[0],self.active_cell.coordinates[1]).ship = self.active_cell.ship
            self.active_cell = None
            return True
        """
        return True

    def get_active_cell(self):
        return self.active_cell

    def set_active_cell(self, mouse: tuple[int, int]):
        """
        returns false if mouse click is not on cell,
        returns true and sets the active cell otherwise
        """
        if self.__player2.board.get_cell_mouse(mouse) is not None:
            self.active_cell = self.__player2.board.get_cell_mouse(mouse)
            return True
        return False

    def set_active_cell_placement(self, mouse: tuple[int, int]):
        if self.__player1.large_board.get_cell_mouse(mouse) is not None:
            self.active_cell = self.__player1.large_board.get_cell_mouse(mouse)
            return True
        return False

    async def change_turn(self):
        # if p2 hit a mine on previous turn dont change turn
        skip = False
        self.turn ^= Turn.PLAYER_TWO
        if self.turn != Turn.PLAYER_TWO:
            return
        if self.p2_skip_turn:
            print("skipped2")
            self.p2_skip_turn = False
            skip = True

        if isinstance(self.__player2, AI) and not skip:
            await asyncio.sleep(1)
            x, y = self.__player2.guess()
            hit = self.validate_shot(self.__player1.board.get_cell(x, y))
            if hit:
                # if the cell is a hit, set last_hit to x, y
                self.__player2.set_last_hit(x, y)

        self.turn ^= Turn.PLAYER_TWO

    def fire_shot(self):
        """
        Player shot
        Returns true if the shot was fired successfully
        """
        if self.skip_turn:
            self.skip_turn = False
            print("skip")
            return True
        if not self.active_cell or self.turn != Turn.PLAYER_ONE:
            return False
        fire_sound.play()
        if isinstance(self.__player2, Opponent) and self.client:
            self.client.set_guess(self.active_cell)

        self.validate_shot(self.active_cell)
        self.active_cell = None
        return True

    def validate_shot(self, active_cell: Cell):
        """
        Marks the active cell as hit.
        Checks if there was a ship in the active cell.
        If ship, returns True, False otherwise.
        """

        if active_cell.checkpirate():
            pirate_sound.play()
            active_cell.hit(flash=self.animations)
            if self.turn == Turn.PLAYER_ONE:
                self.skip_turn = True
            else:
                self.p2_skip_turn = True
            return True
        elif active_cell.hit(flash=self.animations):
            self.endgame()
            hit_sound.play()
            return True
        else:
            miss_sound.play(0)
            return False

    def place_pirate(self):
        self.__player1.board.place_pirate()
        self.__player2.board.place_pirate()

    def validate_pirate(self, active_cell: Cell):
        if (self.turn == Turn.PLAYER_ONE):
            cell = self.__player1.board.get_cell(
                active_cell.coordinates[0], active_cell.coordinates[1])
        else:
            cell = self.__player2.board.get_cell(
                active_cell.coordinates[0], active_cell.coordinates[1])
        return cell.set_pirate()

    def endgame(self):
        """
        Checks if the game is over and update the state variables accordingly
        """
        if self.__player1.board.gameover():
            self.game_over = True
            self.won = False
        elif self.__player2.board.gameover():
            self.game_over = True
            self.won = True
        elif self.client and self.client.game_over:
            self.game_over = True
            self.won = self.client.won

    def get_local_player(self):
        return self.__player1

    def skip(self):
        self.skip_turn = False
