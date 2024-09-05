import websockets
import json
import logging
import asyncio

from GameController import GameController
from GameStrategy import GameStrategy
from GoalSuitEstimator import GoalSuitEstimator
from PortfolioEval import PortfolioEval
from RESTAPIController import RESTAPIController

logger = logging.getLogger(__name__)


class WSController:

    def __init__(self, 
                 uri, 
                 player_id, 
                 restapi: RESTAPIController, 
                 game: GameController, 
                 gameStr: GameStrategy, 
                 goalEst: GoalSuitEstimator,
                 portEval: PortfolioEval) -> None:
        """
        Constructor.

        INPUTS:
            * restapi (RESTAPIController): REST API object
            * game (GameController)
            * player_id (str): ID of the player.
        """

        self.uri            = uri
        self.player_id      = player_id
        self.restapi        = restapi
        self.gameCon        = game
        self.gameStr        = gameStr
        self.goalEst        = goalEst
        self.portEval       = portEval


    async def subscribe_to_websocket(self):
        """
        Subscribe to the websocket.
        """

        async with websockets.connect(self.uri, ping_interval = 20000, ping_timeout=20000) as websocket:

            # Send an initial request
            initial_request = {"action": "subscribe", "playerid": self.player_id}
            await websocket.send(json.dumps(initial_request))
            logger.info("WebSocket request was sent.")

            await self.handle_messages(websocket)



    async def handle_messages(self, ws):
        """
        Handle the messages from the websocket.
        """

        cards_were_dealt = False

        while True:
            message = await ws.recv()
            message = json.loads(message)

            if "status" in message:
                if message['status'] == "SUCCESS":
                    logger.info("Correctly subscribed to the websocket.")
                elif message['status'] == "UNKNOWN_PLAYER":
                    logger.error("Unknown player. If test mode then register in Testnet.")
                elif message['status'] == "UNAUTHORIZED_ACTION":
                    logger.error("Unauthorized action. Subscription to websocket failed.")
                elif message['status'] == "PARSE_ERROR":
                    logger.error("JSON malformed. Subscription to websocket failed.")

            elif "kind" in  message:

                # The game has ended
                if message['kind'] == "end_game":
                    logger.info("The game ended.")
                    for player in message['data']['player_points']:
                        logger.info(f"{player['player_name']} has {player['points']} points.")
                    self.gameCon.print_game_end(message)
                    self.gameCon.reset_game_inventory()
                    self.gameStr.reset()
                    cards_were_dealt = False
                
                # The round has ended
                elif message['kind'] == "end_round":
                    logger.info(f'Round has ended.')
                    self.gameCon.print_round_end(message)
                    self.gameCon.reset_round_inventory()
                    self.gameStr.reset()
                    cards_were_dealt = False

                # Cards were dealt
                elif message['kind'] == "dealing_cards":
                    logger.info(f'Cards were dealt.')
                    self.gameCon.set_starting_hand(message)
                    asyncio.create_task(self.gameStr.perform_strategy())
                    cards_were_dealt = True

                # State was updated
                elif message['kind'] == "update":

                    if cards_were_dealt:

                        # Update inventory with REST API because I found it more reliable during test phase
                        bool_inven, nsuits = self.gameCon.get_restAPI().get_inventory()
                        suit_names = ['spades', 'clubs', 'hearts', 'diamonds']
                        if bool_inven:
                            for idx, nsuit in enumerate(nsuits):
                                self.gameCon.set_suit_n(suit_names[idx], nsuit)

                        # Update players and inventory
                        is_trade = self.gameCon.update_game_status(message)
                        if is_trade:
                            self.gameStr.reset()
                        asyncio.create_task(self.gameStr.perform_strategy())

    