from .ship import Ship


class NormalShip(Ship):
    # track the size
    __size = 0

    # track the HP
    __hp = None

    vertical = True

    def __init__(self, ship_size: int):
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
        return False

"""
# TESTING CODE:

ship = NormalShip(4)
print("Showing size, HP. expect 4 4")
print(ship.get_size())
print(ship.get_hp())
print("Sunk?", ship.sunk())

print("\nHitting twice. expect F F 4 2")
print(ship.hit())
print(ship.hit())
print(ship.get_size())
print(ship.get_hp())
print("Sunk?", ship.sunk())

print("\nHitting twice. expect F T 4 ")
print(ship.hit())
print(ship.hit())
print(ship.get_size())
print(ship.get_hp())
print("Sunk?", ship.sunk())
"""
