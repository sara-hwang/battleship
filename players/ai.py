'''
Class for the AI opponent. 
'''

import random
from time import sleep
from players.opponent import Opponent

class AI(Opponent):
    '''
    AI Interface

    All AI should support a guess function
    that allows it to guess a coordinate on the
    opponent's board

    Later AI will also support a set_last_hit(x, y)
    method that allows communication when a cell is 
    hit. Declare it in the interface
    '''
    def guess(self):
        pass

    def set_last_hit(self, x, y):
        pass



class EasyAI(AI):
    def __init__(self,ship_count,game_size):
        # print("started easy ai game")
        super().__init__(ship_count,game_size)
        self.init_ships()
        self.guessed = []
        self.__size = self.board.get_size()

    def guess(self):
        success = False

        while not success:
            x = random.randint(0, self.__size - 1)
            y = random.randint(0, self.__size - 1)
            if (x, y) not in self.guessed:
                success = True

        self.guessed.append((x, y))
        return x, y

class MedAI(AI):
    def __init__(self,ship_count,game_size):
        # print("Started med ai game")
        super().__init__(ship_count,game_size)
        self.init_ships()
        self.guessed = []
        self.__size = self.board.get_size()
        self.last_hit = None

    '''
    self.last_hit contains the coords of the last hit cell

    The idea behind Medium AI is to exlpore cells
    adjacent to the last hit cell

    once we have explored all adjacent cells and there are no
    more hits, set last_hit back to None and continue to
    find another random cell
    '''
    def guess(self):
        '''
        If there is not a recently hit cell to explore,
        simply pick a random one (like EasyAI)
        '''
        
        if self.last_hit == None:
            return self.random_guess()

        else:
            '''
            If we reach this point, it is because last_hit is not None

            We explore an adjacent cell that has not yet been fired on

            Do this with adjacent_cells(), which will return None
            if there are no adjacent cells that are available to be fired
            on. If there are available adjacent cells, it will return one
            of them
            '''
            adjacent = self.get_adjacent()
            if adjacent != None:
                self.guessed.append((adjacent[0], adjacent[1]))
                return adjacent

            else:
                # all adjacent cells are explored, take a random guess
                # also, set last_hit back to None
                self.last_hit = None
                return self.random_guess()

    def random_guess(self):
        # guess a random cell, similar to EasyAI
        success = False

        while not success:
            x = random.randint(0, self.__size - 1)
            y = random.randint(0, self.__size - 1)
            if (x, y) not in self.guessed:
                success = True

        self.guessed.append((x, y))
        return x, y

    def set_last_hit(self, x, y):
        '''
        Setter for last hit

        The idea is, if we fire a shot and hit, the client
        will call this method and set the last hit
        to let us know
        '''
        self.last_hit = (x, y)

    def get_adjacent(self):
        '''
        Prerequisite: self.last_hit is NOT None

        This function will examine the cells adjacent
        to last_hit

        If there exists some adjacent cell that has not
        been guessed, we return any one of them

        If all such adjacent cells have been guessed,
        return None

        Adjacent cells to (x, y) are:

        (x-1, y)
        (x+1, y)

        (x, y-1)
        (x, y+1)

        A cell is invalid if it is in self.guessed,
        or if it exceeds the boundaries of the board
        '''
        if self.last_hit == None:
            return None

        x = self.last_hit[0]
        y = self.last_hit[1]

        adjacents = [
            (x-1, y),
            (x+1, y),
            (x, y-1),
            (x, y+1)
        ]

        for cell in adjacents:
            if cell not in self.guessed and cell[0] < self.__size \
            and cell[1] < self.__size and cell[0] >= 0 and cell[1] >= 0:
                return cell[0], cell[1]

        return None


class HardAI(AI):
    def __init__(self,ship_count,game_size, opp):
        # print("started Hard AI game")
        super().__init__(ship_count,game_size)
        self.init_ships()
        self.guessed = []
        self.__size = self.board.get_size()
        self.last_hit = None
        self.opp = opp


    def get_opp_ships(self):
        '''
        HardAI should keep track of the opponent's ships
        as an array of tuples

        [ (x1, y1), (x2, y2), ... ]

        where (xi, yi) are the grid coordinates of the
        oppontent's ships.

        In the constructor, we have passed an instance of
        a Player object (opp). This object contains a board
        which contains coordinates of my opponent's ships

        This method extracts the coordinates of cells that
        contain ships, and makes a nice array

        [ (x1, y1), (x2, y2), ... ]

        where (xi, yi) are locations of my opponent's ships
        '''
        self.opp_ships = []

        for i in range(self.__size):
            for j in range(self.__size):
                # print("Checking cell {}, {}".format(i, j))
                if self.opp.board.get_cell(i, j).ship != None:
                    # print("Found ship in cell {} {}".format(i, j))
                    self.opp_ships.append((i, j))

    '''
    self.last_hit contains the coords of the last hit cell

    The idea behind Medium AI is to exlpore cells
    adjacent to the last hit cell

    once we have explored all adjacent cells and there are no
    more hits, set last_hit back to None and continue to
    find another random cell
    '''
    def guess(self):
        '''
        If there is not a recently hit cell to explore,
        simply pick a random one (like EasyAI)
        '''
        
        if self.last_hit == None:
            return self.peek_guess()

        else:
            '''
            If we reach this point, it is because last_hit is not None

            We explore an adjacent cell that has not yet been fired on

            Do this with adjacent_cells(), which will return None
            if there are no adjacent cells that are available to be fired
            on. If there are available adjacent cells, it will return one
            of them
            '''
            adjacent = self.get_adjacent()
            if adjacent != None:
                self.guessed.append((adjacent[0], adjacent[1]))
                return adjacent

            else:
                # all adjacent cells are explored, take a random guess
                # also, set last_hit back to None
                self.last_hit = None
                return self.peek_guess()

    def peek_guess(self):
        '''
        This is what sets apart hard AI and medium AI.

        In the constructor, we take in a list of ship positions.

        This method is called when the AI needs to guesss a
        "random" cell.

        In mediumAI, the cell woudl be truly random (generated by
        the below method random_guess()). In this AI, the cell will
        be random 1-p of the time, and p of the time it will simply
        pick a cell from the positions it knows the ships are.

        The value for p will be determined thorugh experiment.
        Read my code to see what I picked
        '''
        randomint = random.randint(1, 10)
        # print(randomint)

        if randomint <= 5:
            # pick a cell out of the opponent's ships that has not
            # been picked yet
            success = False

            while not success:
                location = random.choice(self.opp_ships)

                # If location has alrady been guessed, guess a new one
                if not (location in self.guessed):
                    success = True

            self.guessed.append(location)
            # print("peeking and firing on", location)
            return location[0], location[1]

        else:
            return self.random_guess()



    def random_guess(self):
        success = False

        while not success:
            x = random.randint(0, self.__size - 1)
            y = random.randint(0, self.__size - 1)
            if (x, y) not in self.guessed:
                success = True

        self.guessed.append((x, y))
        # print("randomly guessed", x, y)
        return x, y

    def set_last_hit(self, x, y):
        '''
        Setter for last hit

        The idea is, if we fire a shot and hit, the client
        will call this method and set the last hit
        to let us know
        '''
        self.last_hit = (x, y)

    def get_adjacent(self):
        '''
        Prerequisite: self.last_hit is NOT None

        This function will examine the cells adjacent
        to last_hit

        If there exists some adjacent cell that has not
        been guessed, we return any one of them

        If all such adjacent cells have been guessed,
        return None

        Adjacent cells to (x, y) are:

        (x-1, y)
        (x+1, y)

        (x, y-1)
        (x, y+1)

        A cell is invalid if it is in self.guessed,
        or if it exceeds the boundaries of the board
        '''
        if self.last_hit == None:
            return None

        x = self.last_hit[0]
        y = self.last_hit[1]

        adjacents = [
            (x-1, y),
            (x+1, y),
            (x, y-1),
            (x, y+1)
        ]

        for cell in adjacents:
            if cell not in self.guessed and cell[0] < self.__size \
            and cell[1] < self.__size and cell[0] >= 0 and cell[1] >= 0:
                return cell[0], cell[1]

        return None
