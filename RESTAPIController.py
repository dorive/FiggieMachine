import requests
import json
import logging

logger = logging.getLogger(__name__)

class RESTAPIController:

    def __init__(self, url) -> None:
        self.url = url


    def register_to_testnet(self, player_id):
        """
        Only for Testnet. It registers a new player.

        INPUTS:
            * player_id (str): player identification. 
        """

        self.playerid = player_id

        # POST header
        header = {
            "Playerid" : player_id
        }

        # Send the POST request
        response = requests.post(self.url + '/register_testnet', headers=header)

        # Check the response status code
        if response.status_code == 200:
            response_data = json.loads(response.json())

            if response_data['status'] == 'SUCCESS':
                start = response_data['message'].find("Temp player name: ") + len("Temp player name: ")
                end = response_data['message'].find(".", start)
                player_name = response_data['message'][start:end]
                logging.info(f"Correctly registered to Testnet. Your name is: {player_name}.")
                return True, player_name
            
            elif response_data['status'] == 'MISSING_HEADER':
                logging.error(f"Testnet registration attempt: missing header.")
                return False, ''

        else:
            logging.error(f"Testnet registration attempt: request failed with status code {response.status_code}")
            return False, ''
        
    def set_playerid(self, player_id):
        """
        Only for competition day. It registers a new player.

        INPUTS:
            * player_id (str): player identification. 
        """
        self.playerid = player_id


    def post_order(self, suit, price, direction):
        """
        Sends an order to the market.

        INPUTS:
            * suit (str): "spade" | "club" | "diamond" | "heart"
            * price (int)
            * direction (str): "buy" | "sell"
        """

        # Sanity check
        if price < 1 or price > 99:
            logging.error(f'Invalid price. Price should be between 1 and 99.')
            return False

        # Define the headers
        headers = {
            "Content-Type": "application/json",
            "Playerid": self.playerid
        }

        # Define the data to send in the POST request
        data = {
            "card": suit,
            "price": price,
            "direction": direction
        }

        # Convert the data to JSON format
        json_data = json.dumps(data)

        # Send the POST request
        response = requests.post(self.url + '/order', headers=headers, data=json_data)

        # Check the response status code
        if response.status_code == 200:
            
            # Get the response data
            response_data = json.loads(response.json())
            
            if response_data['status'] == 'SUCCESS':
                logging.info(f'Order ({suit},{price},{direction}) was sent correctly.')
                return True
            elif response_data['status'] == 'NO_GAME':
                logging.warning(f'No game is currently active.')
                return False
            elif response_data['status'] == 'RATE_LIMIT':
                logging.warning(f'Rate limit was reached. Order was {suit},{price},{direction} not sent.')
                return False
            elif response_data['status'] == 'INVALID_DIRECTION':
                logging.error(f'Order direction is incorrect. Choose buy or sell.')
                return False
            elif response_data['status'] == 'INVALID_CARD':
                logging.error(f'Suit is invalid. Choose between spade, club, diamond, or heart.')
                return False
            elif response_data['status'] == 'INVALID_PRICE':
                logging.error(f'Invalid price. Price should be between 1 and 99.')
                return False
            elif response_data['status'] == 'INSUFFICIENT_FUNDS':
                logging.error(f'Not enough funds.')
                return False
            elif response_data['status'] == 'SELF_TRADE':
                logging.error(f'Trying to self-trade.')
                return False
            elif response_data['status'] == 'NO_INVENTORY':
                logging.error(f'Trying to sell a card you do not have.')
                return False
            elif response_data['status'] == 'UNKNOWN_PLAYER':
                logging.error(f'The player does not exist.')
                return False
            elif response_data['status'] == 'MISSING_HEADER':
                logging.error(f'The player header is missing.')
                return False

        else:
            logging.error(f"Request failed with status code {response.status_code}. Order was not sent.")
            return False
        
    
    def cancel_order(self, suit, direction):
        """
        Sends an order cancellation to the market.

        INPUTS:
            * suit (str): "spade" | "club" | "diamond" | "heart"
            * direction (str): "buy" | "sell"
        """

        # Define the headers
        headers = {
            "Content-Type": "application/json",
            "Playerid": self.playerid
        }

        # Define the data to send in the POST request
        data = {
            "card": suit,
            "direction": direction
        }

        # Convert the data to JSON format
        json_data = json.dumps(data)

        # Send the POST request
        response = requests.post(self.url + '/cancel', headers=headers, data=json_data)

        # Check the response status code
        if response.status_code == 200:
            
            # Get the response data
            response_data = json.loads(response.json())
            
            if response_data['status'] == 'SUCCESS':
                logging.info(f'Order ({suit},{direction}) was cancelled correctly.')
                return True
            elif response_data['status'] == 'NO_GAME':
                logging.warning(f'No game is currently active.')
                return False
            elif response_data['status'] == 'RATE_LIMIT':
                logging.warning(f'Rate limit was reached. Order was {suit},{direction} not sent.')
                return False
            elif response_data['status'] == 'INVALID_DIRECTION':
                logging.error(f'Order direction is incorrect. Choose buy or sell.')
                return False
            elif response_data['status'] == 'INVALID_CARD':
                logging.error(f'Suit is invalid. Choose between spade, club, diamond, or heart.')
                return False
            elif response_data['status'] == 'UNKNOWN_PLAYER':
                logging.error(f'The player does not exist.')
                return False
            elif response_data['status'] == 'MISSING_HEADER':
                logging.error(f'The player header is missing.')
                return False

        else:
            logging.error(f"Request failed with status code {response.status_code}. Order was not cancelled.")
            return False
        
    
    def get_inventory(self):
        """
        Get your current inventory.

        OUTPUTS:
            * list of cards for each suit [spades, clubs, hearts, diamonds]
        """

        # POST header
        header = {
            "Playerid" : self.playerid
        }

        # Send the POST request
        response = requests.post(self.url + '/inventory', headers=header)

        # Check the response status code
        if response.status_code == 200:
            response_data = json.loads(response.json())

            if response_data['status'] == 'SUCCESS':
                nspades, nclubs, ndiamonds, nhearts = response_data['message'].split(',')
                return True, [int(nspades), int(nclubs), int(nhearts), int(ndiamonds)]
            elif response_data['status'] == 'NO_GAME':
                logging.warning(f'No game is currently active.')
                return False, []
            elif response_data['status'] == 'RATE_LIMIT':
                logging.warning(f'Rate limit was reached. Inventory was not sent.')
                return False, []
            elif response_data['status'] == 'UNKNOWN_PLAYER':
                logging.error(f'The player does not exist.')
                return False, []
            elif response_data['status'] == 'MISSING_HEADER':
                logging.error(f'The player header is missing.')
                return False, []

        else:
            logging.error(f"Inventory was not received: request failed with status code {response.status_code}")
            return False, []