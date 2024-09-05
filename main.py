# General imports
import numpy as np
import logging
import asyncio

# Custom libraries
from ColoredLogger import ColoredLogger
from GoalSuitEstimator import GoalSuitEstimator
from GoalSuitPremium import  GoalSuitPremium
from PortfolioEval import PortfolioEval
from WSController import WSController
from RESTAPIController import RESTAPIController
from GameController import GameController
from GameStrategy import GameStrategy


# Logging config
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
formatter = ColoredLogger(
    "{asctime} - {levelname} - {filename} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# Initialize objects
goalEst  = GoalSuitEstimator()
gsPrem   = GoalSuitPremium()
portEval = PortfolioEval(gsPrem, goalEst)
gameCon  = GameController()
gameStr  = GameStrategy(goalEst, portEval, gameCon)

# Websocket and REST API addresses
URL_RESTAPI = "http://localhost:8090"# "http://testnet.figgiewars.com" # "http://localhost:8090" # "http://testnet.figgiewars.com" # "http://exchange.figgiewars.com"
URL_WS      = "ws://localhost:8080" #"ws://testnet-ws.figgiewars.com" # "ws://localhost:8080" # "ws://testnet-ws.figgiewars.com" # "ws://exchange-ws.figgiewars.com"

# Player id
PLAYER_ID   = "MyTest" 

# Register to websocket and REST API
rest_api = RESTAPIController(URL_RESTAPI)
_, player_name = rest_api.register_to_testnet(PLAYER_ID)
gameCon.set_restAPI(rest_api)
gameCon.set_playerName(player_name)
obj = WSController(URL_WS, PLAYER_ID, rest_api, gameCon, gameStr, goalEst, portEval)

# Define an asynchronous function that calls the coroutine
async def main():
    await obj.subscribe_to_websocket()

# Run the asynchronous main function
asyncio.run(main())

