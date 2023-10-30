from .ship import Ship

class Pirate(Ship):
    
    __size=0
    
    __hp=None
    
    vertical = True
    
    def __init__(self, ship_size:int):
        self.__size = ship_size
        self.__hp = ship_size

    def get_size(self):
        return self.__size

    def get_hp(self):
        return self.__hp
    
    def set_orientation(self, vertical: bool) -> None:
        self.vertical = vertical

    """
    "Hits" this ship.

    Returns a boolean value: True indicates the
    hit resulted in the ship sinking
    """

    def hit(self):
        # Do not hit a dead ship
        if self.__hp <= 0:
            return None

        self.__hp -= 1

        # return true if ship has sunk
        return self.__hp == 0

    # determine if this ship is sunk
    def sunk(self):
        return self.__hp <= 0
    
    def ispirate(self):
        return True