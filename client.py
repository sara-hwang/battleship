import asyncio
import json
import websockets.client
from enum import Enum
from board.cell import Cell
from utilities import Turn
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from game_manager import GameManager

URI = "ws://24.199.115.192:8765"
# URI = "ws://127.0.0.1:8765"


class Stages(Enum):
    ERROR = -1
    WAITING_FOR_CODE = 0
    PENDING_OPPONENT_JOIN = 1
    PLACEMENT = 2
    PENDING_OPPONENT_PLACEMENT = 3
    PLAY = 4


class Client:
    def __init__(self, manager: "GameManager") -> None:
        self.manager = manager
        self.game_id: str | None = None
        self.code = ""
        self.player_id = None
        self.requests = asyncio.Queue()
        self.response = []
        self.opp_guess = None
        self.my_result = None
        self.won = False
        self.game_over = False
        self.stage = Stages.WAITING_FOR_CODE
        self.error = None
        self.current_target: Cell | None = None

    async def start(self, stop: asyncio.Future):
        print("connecting to server")
        async with websockets.client.connect(URI) as websocket:
            print("Connected to server")
            await asyncio.gather(
                self.response_handler(websocket),
                self.request_sender(websocket, stop),
            )

    async def response_handler(self, websocket):
        print("Response handler ready")
        async for message in websocket:
            self.handle_response(message)

    async def request_sender(self, websocket, stop: asyncio.Future):
        print("Request sender ready")
        while not stop.done():
            message = await self.requests.get()
            print(f"message queued: {message}")
            await websocket.send(message)
            self.requests.task_done()

    def handle_response(self, response):
        """{
            request:
            response:
        }"""
        print(f"response {response}")
        msg: dict[str, Any] = json.loads(response)
        if msg.get("error"):
            self.error = msg.get("error")
            self.stage = Stages.ERROR
            return
        match msg.get("request"):
            case "new_game":
                self.game_id = msg.get("game_id")
                self.code = msg.get("password")
                self.stage = Stages.PENDING_OPPONENT_JOIN
                print(f"set game id to {self.game_id}")
                size = msg.get("board_size")
                ships = msg.get("num_ships")
                if size is not None:
                    self.manager.set_size(size)
                if ships is not None:
                    self.manager.set_num_ships(ships)

            case "ready_for_placement":
                print("ready for placement! proceed to placement screen")
                self.stage = Stages.PLACEMENT
            case "play":
                self.stage = Stages.PLAY
                self.manager.turn = Turn.PLAYER_ONE if msg.get("your_turn") else Turn.PLAYER_TWO
            case "set_guess":
                hit = msg.get("hit")
                print(f"hit? {hit}")
                self.manager.turn = Turn.PLAYER_TWO
                self.current_target.multiplayer_hit(hit)
                self.manager.active_cell = None
                if msg.get("endgame"):
                    self.game_over = True
                    self.won = msg.get("won")
                    self.manager.endgame()
            case "opponent_guess":
                self.manager.turn = Turn.PLAYER_ONE
                hit = msg.get("hit")
                coords = msg.get("coords")
                targeted_cell = self.manager.get_local_player().board.get_cell(coords[0], coords[1])
                targeted_cell.multiplayer_hit(hit)
                if msg.get("endgame"):
                    self.game_over = True
                    self.won = False
                    self.manager.endgame()
            case "identify":
                pass
            case other:
                print("invalid response")

    def identify(self):
        message = {"request": "identify"}
        self.requests.put_nowait(json.dumps(message))

    def create_game(self, ship_count, board_size):
        message = {"request": "new_game", "ship_count": ship_count, "board_size": board_size}
        self.requests.put_nowait(json.dumps(message))
        self.player_id = "0"
        print("creating game")

    def join_game(self, code: str):
        message = {"request": "join_game", "game_code": code}
        self.requests.put_nowait(json.dumps(message))
        self.player_id = "1"
        print(f"joining game with code {code}")

    def set_placement(self, ships: list[list[tuple[int, int]]]):
        message = {"request": "set_placement", "ships": ships}
        self.requests.put_nowait(json.dumps(message))
        print("sending placement")

    def set_guess(self, cell: Cell):
        self.current_target = cell
        coords = cell.coordinates
        message = {"request": "set_guess", "coords": [coords[0], coords[1]]}
        self.requests.put_nowait(json.dumps(message))
