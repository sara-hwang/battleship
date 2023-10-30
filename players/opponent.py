from players.player import Player


class Opponent(Player):
    def __init__(self, ship_count, game_size):
        super().__init__(
            ship_count, game_size, coords=(150, 150), width=550, display=False, foreign=True
        )

    def set_client(self, client):
        self.client = client
