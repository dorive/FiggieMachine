import logging
import json
import numpy as np

from GoalSuitEstimator import GoalSuitEstimator
from PortfolioEval import PortfolioEval
from RESTAPIController import RESTAPIController

logger = logging.getLogger(__name__)


class GameController:

    def __init__(self) -> None:
        self.inventory = {'Myself': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          'P2': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          'P3': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          'P4': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          }
        self.players_names = ['Myself', 'P2', 'P3', 'P4']
        self.inventory2d = np.array([[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.known_players = 1
        self.orderbook = {"spades":   [-999, 999],
                          "clubs":    [-999, 999],
                          "hearts":   [-999, 999],
                          "diamonds": [-999, 999]}
        self.restapi = None
        
        
    def set_restAPI(self, rest_api: RESTAPIController):
        self.restapi = rest_api

    def get_restAPI(self):
        return self.restapi
    
    def set_playerName(self, player_name):
        self.player_name = player_name
        self.inventory[self.player_name] = self.inventory['Myself']
        del self.inventory['Myself']
        self.players_names[0] = self.player_name



    #####################################################################################################
    #                                      INVENTORY DEALERS
    #####################################################################################################

    def set_starting_hand(self, cards):
        """
        Sets bot's starting hand.

        INPUTS:
            * cards (dict): message from WebSocket.
        """

        for suit, value in cards['data'].items():
            try:
                self.inventory[self.player_name][suit] += value
            except:
                logger.error('Something wrong with the inventory player name!')
                self.inventory = {'Myself': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          'P2': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          'P3': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          'P4': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          }
                self.inventory[self.player_name][suit] += value
        
        self.print_my_inventory()
        self.inventory2d = self.get_inventory_matrix()


    def set_suit_n(self, suit, value):
        """
        Sets the number of cards in your inventory for a given suit.

        INPUTS:
            * suit (str): "spades" | "clubs" | "hearts" | "diamonds"
            * value (int)
        """

        self.inventory[self.player_name][suit] = value
        self.inventory2d = self.get_inventory_matrix()


    def get_suit_n(self, suit):
        """
        Returns the number of cards in your inventory for a given suit.

        INPUTS:
            * suit (str): "spades" | "clubs" | "hearts" | "diamonds"
        """

        return self.inventory[self.player_name][suit]
    

    def get_my_inventory(self):
        """
        Returns a list with my cards inventory.
        """
        return [self.inventory[self.player_name]['spades'],
                self.inventory[self.player_name]['clubs'],
                self.inventory[self.player_name]['hearts'],
                self.inventory[self.player_name]['diamonds']]  


    def get_inventory_matrix(self):
        """
        Returns the inventory in a 2d matrix format.
        """

        # Extract players (keys of the outer dictionary)
        players = self.players_names

        # Extract suits (keys of the inner dictionaries)
        suits = list(self.inventory[players[0]].keys())

        # Create a 2D inventory
        inventory_2d = []
        for player in players:
            row = [self.inventory[player][suit] for suit in suits]
            inventory_2d.append(row)

        return np.array(inventory_2d)
    

    def add_card_to_player(self, player_id, suit, qty=1):
        """
        Adds one card to a player.

        INPUTS:
            * player_id (str): name of the player.
            * suit (str): suit of the card to add.
            * qty (int): quantity
        """

        self.inventory[player_id][suit + 's'] += qty
        self.inventory[player_id][suit + 's'] = int(np.nanmax([self.inventory[player_id][suit + 's'], 0]))
        self.inventory2d = self.get_inventory_matrix()
        logger.info(f'{player_id} has {json.dumps(self.inventory[player_id])}.')


    def add_card_to_selling_player(self, player_id, suit):
        """
        Adds one card to a selling player.

        INPUTS:
            * player_id (str): name of the player.
            * suit (str): suit of the card to add.
        """

        if (self.inventory[player_id][suit] == 0) and (player_id != self.player_name):
            logger.info(f'{player_id} had {json.dumps(self.inventory[player_id])}.')
            self.inventory[player_id][suit] += 1
            self.inventory2d = self.get_inventory_matrix()
            logger.info('Adding card to selling player...')
            logger.info(f'{player_id} has {json.dumps(self.inventory[player_id])}.')


    def get_ncards_per_suit(self):
        """
        Returns th total number of cards per suit.

        OUTPUTS:
            * (list): [spades, clubs, hearts, diamonds]
        """
        totals = {'spades': 0, 'clubs': 0, 'hearts': 0, 'diamonds': 0}

        for player, suits in self.inventory.items():
            for suit, count in suits.items():
                totals[suit] += count

        return [totals['spades'], totals['clubs'], totals['hearts'], totals['diamonds']]
    

    def add_player(self, player_id):
        """
        Adds a new player to the inventory.
        
        INPUTS:
            * player_id (str): name of the player.
        """

        if player_id not in self.players_names:

            if 'P2' in self.inventory:
                self.inventory[player_id] = self.inventory['P2']
                del self.inventory['P2']
                self.players_names[1] = player_id
            elif 'P3' in self.inventory:
                self.inventory[player_id] = self.inventory['P3']
                del self.inventory['P3']
                self.players_names[2] = player_id
            elif 'P4' in self.inventory:
                self.inventory[player_id] = self.inventory['P4']
                del self.inventory['P4']
                self.players_names[3] = player_id

            self.known_players += 1
            logger.info(f'{player_id} player was added to the inventory.')


    def reset_round_inventory(self):
        """
        Sets the card inventory to zero for a new round.
        """

        self.inventory = {self.players_names[0]: {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          self.players_names[1]: {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          self.players_names[2]: {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          self.players_names[3]: {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          }
        self.inventory2d = np.array([[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.orderbook = {"spades":   [-999, 999],
                          "clubs":    [-999, 999],
                          "hearts":   [-999, 999],
                          "diamonds": [-999, 999]}
        logger.info('Card inventory was reset. Prepared for a new round.')


    def reset_game_inventory(self):
        """
        Sets the card inventory to zero for a new game.
        """

        self.inventory = {'Myself': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          'P2': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          'P3': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          'P4': {'spades':0, 'clubs':0, 'hearts':0, 'diamonds':0},
                          }
        self.inventory2d = np.array([[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]])
        self.known_players = 1
        self.players_names = ['Myself', 'P2', 'P3', 'P4']
        self.orderbook = {"spades":   [-999, 999],
                          "clubs":    [-999, 999],
                          "hearts":   [-999, 999],
                          "diamonds": [-999, 999]}
        logger.info('Card inventory was reset. Prepared for a new game.')

    
    def update_game_status(self, message):
        """
        Updates the cards each player has.
        """

        # Initialize the orderbook
        is_trade = False
        self.orderbook = {"spades":   [-999, 999],
                          "clubs":    [-999, 999],
                          "hearts":   [-999, 999],
                          "diamonds": [-999, 999]}

        # Updates info given by trades
        strTradesUp = message['data']['trade']
        if strTradesUp != '':
            suit, price, buyer_pl, seller_pl = strTradesUp.split(',')
            if self.known_players < 4:
                self.add_player(buyer_pl)
                self.add_player(seller_pl)
            if buyer_pl != self.player_name:
                self.add_card_to_player(buyer_pl, suit, 1)
            if seller_pl != self.player_name:
                self.add_card_to_player(seller_pl, suit, -1)
            #self.add_card_to_player(buyer_pl, suit, 1)
            #self.add_card_to_player(seller_pl, suit, -1)
            is_trade = True
            logger.info(f"Trade between {buyer_pl} and {seller_pl} - {suit} at {price}")

        # Updates info given by order book
        for suit in ['spades', 'clubs', 'diamonds', 'hearts']:

            # Ask
            asks = message['data'][suit]['asks']

            # Add players who are selling cards
            for ask in asks:
                if self.known_players < 4:
                    self.add_player(ask[1])
                self.add_card_to_selling_player(ask[1], suit)
                self.orderbook[suit][1] = int(np.nanmin([ask[0], self.orderbook[suit][1]]))

            # Bid
            bids = message['data'][suit]['bids']

            # Add players who are buying cards
            for bid in bids:
                if self.known_players < 4:
                    self.add_player(bid[1])
                self.orderbook[suit][0] = int(np.nanmax([bid[0], self.orderbook[suit][0]]))

        logger.info(f"Orderbook: {self.orderbook}.")

        return is_trade




    #####################################################################################################
    #                                           PRINTERS
    #####################################################################################################

    def print_round_end(self, message):
        """
        Prints the results of the round end.
        """

        # Prints the deck
        logger.info(f"The deck was: {json.dumps(message['data']['card_count'])}")

        # Prints the goal suit
        logger.info(f"The goal suit was: {json.dumps(message['data']['goal_suit'])}")

        # Prints player inventories
        for pl_inventory in message['data']['player_inventories']:
            logger.info(f'{json.dumps(pl_inventory)}')

        # Prints player points
        for pl_points in message['data']['player_points']:
            logger.info(f'{json.dumps(pl_points)}')


    def print_game_end(self, message):
        """
        Prints the results of the game end.
        """

        dict_points = {}

        # Prints player points
        for pl_points in message['data']['player_points']:
            logger.info(f'{json.dumps(pl_points)}')
            dict_points[pl_points['player_name']] = pl_points['points']

        # Prints the winners (first two)
        top_two_players = sorted(dict_points.items(), key=lambda item: item[1], reverse=True)[:2]
        logger.info('The winners are:')
        for player, points in top_two_players:
            logger.info(f'{player}: {points}')


    def print_my_inventory(self):
        """
        Prints my cards inventory.
        """
        logger.info(f"My inventory: {json.dumps(self.inventory[self.player_name])}.")


    def print_seen_cards(self):
        """
        Prints the number of cards seen for each suit.
        """
        logger.info(f"Seen cards: {self.get_ncards_per_suit()} [spades, clubs, hearts, diamonds]")
