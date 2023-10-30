class Ship:
    vertical: bool
    # getter for ship size
    def get_size(self) -> int:
        return 0

    # getter for HP
    def get_hp(self):
        pass

    """
    "Hits" this ship.

    Returns a boolean value: True indicates the
    hit resulted in the ship sinking
    """

    def hit(self):
        pass

    # determine if this ship is sunk
    def sunk(self) -> bool:
        pass

    def set_orientation(self, vertical: bool) -> None:
        pass

    def ispirate(self):
        pass