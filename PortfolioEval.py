import numpy as np
import math
import logging
from GoalSuitPremium import GoalSuitPremium
from GoalSuitEstimator import GoalSuitEstimator

logger = logging.getLogger(__name__)

class PortfolioEval:

    def __init__(self, gsPremium: GoalSuitPremium, gsEst: GoalSuitEstimator) -> None:
        self.gsPrem = gsPremium
        self.gsEst  = gsEst


    def evaluate_portfolio(self, own_cards, pl_cards, probs, probs_10):
        """
        Evaluates the value of the portfolio in dollars.

        INPUTS:
            * own_cards (list): number of cards you have in your portfolio, array [spades, clubs, hearts, diamonds]
            * pl_cards (numpy 2d array): number of cards each player has of each suit
            * probs (list): probability of goal suit, array [spades, clubs, hearts, diamonds]
            * probs_10 (list): probability of each suit having 10 cards
        """

        return 10*np.dot(own_cards, probs) + np.sum([probs[ii]*self.gsPrem.get_goal_suit_premium(own_cards[ii], list(pl_cards[:,ii]), probs_10[ii]) for ii in range(4)])
    


    def get_neutral_quotes(self, port_ev, pl_cards, probs, probs_10):
        """
        Computes the neutral quotes (portfolio will have the same EV) for each suit.

        INPUTS:
            * port_ev (double): portfolio EV
            * pl_cards (numpy 2d array): number of cards each player has of each suit
            * probs (list): probability of goal suit, array [spades, clubs, hearts, diamonds]
            * probs_10 (list): probability of each suit having 10 cards

        OUTPUTS:
            * (numpy 2d array) equilibrium price for each action
        """

        # Neutral quotes
        neutral_quotes = np.array([ [np.nan, np.nan],
                                    [np.nan, np.nan],
                                    [np.nan, np.nan],
                                    [np.nan, np.nan]])        

        for suit in range(4):

            # Selling case
            least_port_eval = np.nan
            if pl_cards[0, suit] > 0: # At least I have one card to sell
                for idx_opp in range(1,4):
                    new_port_eval = self.evaluate_portfolio([n if idx != suit else n-1 for idx, n in enumerate(pl_cards[0,:])], # substract one card to suit
                                            np.array([[pl_cards[i, j] + 1 if i == idx_opp and j == suit else pl_cards[i, j] for j in range(pl_cards.shape[1])] for i in range(pl_cards.shape[0])]), 
                                            probs, 
                                            probs_10)
                    
                    least_port_eval = np.nanmin([least_port_eval, new_port_eval])
                
                    if new_port_eval > port_ev:
                        logger.error('By giving one card your portfolio cannot have greater value!')
            
                neutral_quotes[suit][1] = port_ev - least_port_eval


            # Buying case
            least_port_eval = np.nan
            for idx_opp in range(1,4):

                if pl_cards[idx_opp, suit] == 0: # in the case someone sell to us one card we did not see before
                    try:
                        new_probs, new_probs_10 = self.gsEst.get_goalsuit_prob([n if idx != suit else n+1 for idx, n in enumerate(np.sum(pl_cards,axis=0))])
                    except: # special cases were adding more cards than feasible
                        continue
                else: # in this case we already saw the card
                    new_probs, new_probs_10 = probs, probs_10

                new_port_eval = self.evaluate_portfolio([n if idx != suit else n+1 for idx, n in enumerate(pl_cards[0,:])], # add one card to suit
                                        np.array([[pl_cards[i, j] - 1 if (i == idx_opp) and (j == suit) and (pl_cards[i, j] > 0) else pl_cards[i, j] for j in range(pl_cards.shape[1])] for i in range(pl_cards.shape[0])]), 
                                        new_probs, 
                                        new_probs_10)

                least_port_eval = np.nanmin([least_port_eval, new_port_eval])
                
                if (new_port_eval < port_ev) & (pl_cards[idx_opp, suit] != 0):
                    logger.error('By having one more card your portfolio cannot have lower value!')

            neutral_quotes[suit][0] = np.nanmax([least_port_eval - port_ev, 0.0])
        
        return neutral_quotes


    def get_adjusted_quotes(self, neutral_quotes, n_seen_cards, probs, own_cards):
        """
        Adjust the quotes based on a spread constant and the number of card seen.

        INPUTS:
            * neutral_quotes (list): neutral quotes for each suit
            * n_seen_cards (int): number of seen cards

        OUTPUTS:
            * (list): adjusted quotes
        """

        # Adjusted quotes
        adj_quotes = np.array([ [-999,999],
                                [-999,999],
                                [-999,999],
                                [-999,999]], dtype=int)
        
        for suit in range(4):

            if not math.isnan(neutral_quotes[suit][0]):
                adj_quotes[suit][0] = int(math.floor(neutral_quotes[suit][0] * (n_seen_cards/40)))

            if not math.isnan(neutral_quotes[suit][1]):
                adj_quotes[suit][1] = int(math.ceil(neutral_quotes[suit][1] * (1 + (1-n_seen_cards/40))))

            if adj_quotes[suit][1] <= adj_quotes[suit][0]:
                logger.warning(f'Bid-Ask quotes were not correctly adjusted!: {adj_quotes[suit][0]} - {adj_quotes[suit][1]}')

        return adj_quotes
    

    def get_market_taking_order(self, orderbook, neutral_quotes, adj_quotes):
        """
        Computes if there is an order to market take.

        INPUTS:
            * orderbook (dict): orderbook for each suit
            * neutral_quotes (numpy 2d array): equilibrium quotes
            * adj_quotes (numpy 2d array): adjusted quotes

        OUTPUTS:
            * (boolean): if there is a market order to take
            * (str): direction
            * (str): suit
            * (int): price
        """

        taking_orders = []

        for idx, suit in enumerate(['spades', 'clubs', 'hearts', 'diamonds']):

            if (orderbook[suit][0] >= adj_quotes[idx][1]) and (adj_quotes[idx][1] != 999):
                EV_quoting = orderbook[suit][0] - adj_quotes[idx][1]
                EV_adj     = adj_quotes[idx][1] - neutral_quotes[idx][1]
                taking_orders.append([EV_quoting + EV_adj, 
                                      "sell", 
                                      suit[:-1], 
                                      orderbook[suit][0]]) # EV, direction, suit, price

            if (orderbook[suit][1] <= adj_quotes[idx][0]) and (adj_quotes[idx][0] != -999):
                EV_quoting = adj_quotes[idx][0] - orderbook[suit][1]
                EV_adj     = neutral_quotes[idx][0] - adj_quotes[idx][0]
                taking_orders.append([EV_quoting + EV_adj, 
                                      "buy", 
                                      suit[:-1], 
                                      orderbook[suit][1]]) # EV, direction, suit, price

        # Get the taking order with more EV
        if taking_orders:
            highest = None
            for order in taking_orders:
                if highest is None or order[0] > highest[0]:
                    highest = order
            return True, highest[1], highest[2], highest[3]
        else:
            return False, None, None, None
        
    
    def get_market_limiting_order(self, neutral_quotes, adj_quotes):
        """
        Computes the four-highest EV market limiting order.

        INPUTS:
            * neutral_quotes (numpy 2d array): equilibrium quotes
            * adj_quotes (numpy 2d array): adjusted quotes

        OUTPUTS:
            * (str): direction
            * (str): suit
            * (int): price
        """

        limiting_orders = []

        for idx, suit in enumerate(['spades', 'clubs', 'hearts', 'diamonds']):

            if adj_quotes[idx][1] <= 99:
                EV_adj = adj_quotes[idx][1] - neutral_quotes[idx][1]
                limiting_orders.append([EV_adj, 
                                        "sell", 
                                        suit[:-1], 
                                        adj_quotes[idx][1]]) # EV, direction, suit, price

            if adj_quotes[idx][0] > 0:
                EV_adj = neutral_quotes[idx][0] - adj_quotes[idx][0]
                limiting_orders.append([EV_adj, 
                                        "buy", 
                                        suit[:-1], 
                                        adj_quotes[idx][0]]) # EV, direction, suit, price


        # Get the four limiting orders with more EV
        if limiting_orders:
            limiting_orders = sorted(limiting_orders, key=lambda x: x[0], reverse=True)
            limiting_orders = limiting_orders[:4]
            return True, \
                [sublist[1] for sublist in limiting_orders], \
                [sublist[2] for sublist in limiting_orders], \
                [sublist[3] for sublist in limiting_orders]
    
        else:
            return False, None, None, None
