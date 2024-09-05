import logging
import json

from GoalSuitEstimator import GoalSuitEstimator
from PortfolioEval import PortfolioEval
from GameController import GameController

logger = logging.getLogger(__name__)


class GameStrategy:
        
   def __init__(self, 
                 goalEst: GoalSuitEstimator, 
                 portEval: PortfolioEval,
                 gameCon: GameController) -> None:
      self.goalEst  = goalEst
      self.portEval = portEval
      self.gameCon  = gameCon
      self.orders = []

   def reset(self):
      self.orders = []


   async def perform_strategy(self):
      """
      Computes quoting prices for each suit and sends the orders.
      """

      # STEP 1) Get the updated probabilities of the goal suit
      probs, probs_10 = self.goalEst.get_goalsuit_prob(self.gameCon.get_ncards_per_suit())
      self.gameCon.print_my_inventory()
      self.gameCon.print_seen_cards()
      logger.info(f'Goal suit probabilities: {json.dumps(probs)} [spades, clubs, hearts, diamonds]')

      # STEP 2) Update the value of the portfolio
      port_ev = self.portEval.evaluate_portfolio(self.gameCon.get_my_inventory(), self.gameCon.inventory2d, probs, probs_10)
      logger.info(f'Portfolio eval: {port_ev:.2f}')
      logger.info(f"Orderbook: {self.gameCon.orderbook}.")

      # STEP 3) Compute neutral quotes for each suit
      neutral_quotes = self.portEval.get_neutral_quotes(port_ev, self.gameCon.inventory2d, probs, probs_10)
      logger.info(f"Neutral quotes: {' '.join(['[' + ', '.join(f'{num:.2f}' for num in row) + ']' for row in neutral_quotes])}")

      # STEP 4) Adjust quoting prices
      adj_quotes = self.portEval.get_adjusted_quotes(neutral_quotes, sum(self.gameCon.get_ncards_per_suit()), probs, self.gameCon.get_my_inventory())
      logger.info(f"Adjusted quotes: {' '.join(['[' + ', '.join(f'{num:.2f}' for num in row) + ']' for row in adj_quotes])}")

      # STEP 5) Compare the quotes with the orderbook
      take_order, direction, suit, price = self.portEval.get_market_taking_order(self.gameCon.orderbook, neutral_quotes, adj_quotes)

      # STEP 6) If market taking is profitable, send the order
      if take_order and (self.gameCon.get_suit_n(suit + 's') > 0 or direction == 'buy'):
         logger.info(f"Trying to take order: {direction}, {suit}, {price} ...")
         self.gameCon.get_restAPI().post_order(suit, int(price), direction)

      # STEP 7) If not, put the most profitable quotes
      if not take_order:
         limit_order, ldirection, lsuit, lprice = self.portEval.get_market_limiting_order(neutral_quotes, adj_quotes)

         if limit_order:
            new_orders = []
            for idx in range(len(ldirection)):
               direction = ldirection[idx]
               suit = lsuit[idx]
               price = lprice[idx]
               order_id = direction + ',' + suit + ',' + str(price)
               new_orders.append(direction + ',' + suit)

               # Check if order is already in the market
               if ((order_id) not in self.orders) and (price > 0) and (price < 100):
                  if (direction == "buy") or ((direction == "sell") and (price > 3)):
                     logger.info(f"Trying to put limiting order: {direction}, {suit}, {price} ...")
                     bool_limit = self.gameCon.get_restAPI().post_order(suit, int(price), direction)
                     if bool_limit:
                        self.orders.append(order_id)

            # Remove old orders from the market
            for order in self.orders:
               temp_dir = order.split(',')[0]
               temp_suit = order.split(',')[1]
               temp_order_id = temp_dir + ',' + temp_suit
               if temp_order_id not in new_orders:
                  logger.info(f"Trying to cancel order: {temp_dir}, {temp_suit} ...")
                  bool_cancel = self.gameCon.get_restAPI().cancel_order(temp_suit, temp_dir)
                  if bool_cancel:
                     self.orders.remove(order)