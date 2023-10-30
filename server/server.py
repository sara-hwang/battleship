import asyncio
import json
import logging
import random
import signal
import uuid
import websockets.server
import websockets.exceptions

ADDRESS = "0.0.0.0"
PORT = "8765"
logging.basicConfig(
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s - %(message)s",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Player:
    def __init__(self):
        self.ships: list[list[tuple[int, int]]] = []
        self.guessed_by_opponent: list[list[tuple[int, int]]] = []
        self.next_guess = None
        self.result = None
        self.socket: websockets.server.WebSocketServerProtocol | None = None


class Game:
    def __init__(self, ship_count: int, board_size: int):
        self.logger = logging.getLogger("battleship.game")
        self.id = str(uuid.uuid4())
        self.players: tuple[Player, Player] = (Player(), Player())
        self.password = Game.generate_pw()
        self.ship_count = ship_count
        self.board_size = board_size
        self.logger.info(
            f"Game created, id {self.id} password {self.password} {ship_count} {board_size}"
        )
        self.turn = 0

    def generate_pw():
        chars = 'ABCDEFGHIJKLMNPQRSTUVWXYZ123456789'
        return "".join(random.choice(chars) for i in range(9))

    def is_empty(self):
        return self.players[0].socket == None and self.players[1].socket == None


class Server:
    """
    {
        "request": request,
        "game": game,
        "player": player,
        "details": details
    }
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger("battleship.server")
        self.games: dict[str, Game] = {}
        self.queues: list[asyncio.Queue] = []
        self.tasks = []
        self.clients = set()
        self.socket_to_player: dict[websockets.server.WebSocketServerProtocol, Player] = {}
        self.code_to_game: dict[str, Game] = {}
        self.player_to_game: dict[Player, Game] = {}

    async def handler(self, websocket: websockets.server.WebSocketServerProtocol):
        self.logger.info("Incoming client")
        self.clients.add(websocket)
        try:
            # each worker has it's own queue
            new_worker = asyncio.Queue()
            worker_id = len(self.queues)
            task = asyncio.create_task(self.worker(websocket, worker_id))
            self.tasks.append(task)
            self.queues.append(new_worker)
            while True:
                self.logger.debug("Ready to handle next request from client")
                packet = await websocket.recv()
                self.queues[worker_id].put_nowait(packet)
        except websockets.exceptions.ConnectionClosedOK:
            self.logger.info("Client quit")
        except websockets.exceptions.ConnectionClosedError:
            self.logger.info("Client quit unexpectedly")
        finally:
            self.logger.info("Removing client")
            self.clients.remove(websocket)
            socket_player = self.socket_to_player.get(websocket)
            if socket_player:
                socket_player.socket = None
                del self.socket_to_player[websocket]
                game = self.player_to_game.get(socket_player)
                if game != None:
                    del self.player_to_game[socket_player]

    async def worker(self, websocket: websockets.server.WebSocketServerProtocol, workerID: int):
        while True:
            self.logger.debug(f"worker {workerID} is awaiting task")
            packet = await self.queues[workerID].get()
            self.logger.debug(f"worker id: {workerID} packet: {packet}")
            msg: dict = json.loads(packet)
            request = msg.get("request")
            player = self.socket_to_player.get(websocket)
            if player != None:
                game = self.player_to_game.get(player)
                player_id = game.players.index(player)
                if not (player_id in [0, 1]):
                    player_id = 0
                    self.logger.error("Player associated with game, but game does not recognise")
            details = msg.get("details")
            try:
                match request:
                    # create a new game
                    case "new_game":
                        game = Game(msg.get("ship_count"), msg.get("board_size"))
                        game.players[0].socket = websocket
                        self.socket_to_player[websocket] = game.players[0]
                        self.games[game.id] = game
                        self.code_to_game[game.password] = game
                        self.player_to_game[game.players[0]] = game
                        response = {
                            "request": "new_game",
                            "game_id": game.id,
                            "password": game.password,
                        }
                        await websocket.send(json.dumps(response))

                    case "join_game":
                        game = self.code_to_game.get(msg.get("game_code"))
                        if game == None:
                            self.logger.debug("No such game")
                            await websocket.send(
                                json.dumps({"request": "new_game", "error": "Invalid invite code"})
                            )
                            raise Exception("No such game")
                        if game.players[0].socket != None and game.players[1].socket != None:
                            self.logger.debug("Game is full")
                            raise Exception("Game is full")
                        available_slot = -1
                        if game.players[1].socket == None:
                            available_slot = 1
                        if game.players[0].socket == None:
                            available_slot = 0
                        game.players[available_slot].socket = websocket
                        self.socket_to_player[websocket] = game.players[available_slot]
                        self.player_to_game[game.players[available_slot]] = game
                        response = {
                            "request": "new_game",
                            "game_id": game.id,
                            "password": game.password,
                            "board_size": game.board_size,
                            "num_ships": game.ship_count
                        }
                        await websocket.send(json.dumps(response))
                        if game.players[0].socket != None and game.players[1].socket != None:
                            self.logger.debug("Game starting, notifying clients")
                            response = {"request": "ready_for_placement"}
                            response_json = json.dumps(response)
                            await game.players[0].socket.send(response_json)
                            await game.players[1].socket.send(response_json)
                        else:
                            self.logger.debug("Still waiting for both players...")

                    case "set_placement":
                        if player == None or game == None:
                            response = {"request": "set_placement", "error": "Unknown error"}
                            response_json = json.dumps(response)
                            await websocket.send(response_json)
                        ships = msg.get("ships")
                        player.ships = [[tuple(cell) for cell in ship] for ship in ships]
                        player.guessed_by_opponent = [[] for ship in ships]
                        if all(len(player.ships) == game.ship_count for player in game.players):
                            response = {"request": "play", "your_turn": True}
                            response_json = json.dumps(response)
                            await game.players[0].socket.send(response_json)
                            response = {"request": "play", "your_turn": False}
                            response_json = json.dumps(response)
                            await game.players[1].socket.send(response_json)

                    # join first empty game
                    # might need to return error if no empty games, then create game instead
                    case "joinrandom":
                        pass

                    case "set_guess":
                        if player_id != game.turn:
                            response = {"request": "set_guess", "warning": "not_your_turn"}
                            await websocket.send(json.dumps(response))
                            break
                        # sanitize input before passing on to opponent
                        coords = (msg.get("coords")[0], msg.get("coords")[1])
                        print("set guess as", coords)
                        opponent = game.players[player_id ^ 1]
                        hit = any(coords in ship for ship in opponent.ships)
                        if hit:
                            for i in range(len(opponent.ships)):
                                if coords in opponent.ships[i]:
                                    opponent.guessed_by_opponent[i].append(coords)

                        is_endgame = all(
                            set(ship) == set(opponent.guessed_by_opponent[i])
                            for i, ship in enumerate(opponent.ships)
                        )
                        game.turn ^= 1
                        response = {
                            "request": "set_guess",
                            "hit": hit,
                            "endgame": is_endgame,
                            "won": is_endgame,
                        }
                        await websocket.send(json.dumps(response))
                        response = {
                            "request": "opponent_guess",
                            "coords": coords,
                            "hit": hit,
                            "endgame": is_endgame,
                        }
                        await opponent.socket.send(json.dumps(response))

                    case "identify":
                        await websocket.send(json.dumps({"request": "identify", "response": "hello"}))

                    case _:
                        self.logger.debug("Invalid request")
            except Exception:
                pass

            self.queues[workerID].task_done()


async def main():
    server = Server()

    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    try:
        loop.add_signal_handler(signal.SIGTERM, loop.stop)
    except NotImplementedError:
        pass  # Ignore if not implemented. Means this program is running in windows.

    async with websockets.server.serve(server.handler, ADDRESS, PORT, ping_interval=None):
        await stop  # run forever

    logging.info("Cancelling worker tasks...")
    # Cancel our worker tasks.
    for task in server.tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*server.tasks, return_exceptions=True)


if __name__ == "__main__":
    logging.info("Starting server...")
    asyncio.run(main())
