import pandas as pd
import numpy as np

class GoalSuitPremium:

    def __init__(self) -> None:

        # Load precomputed probabilities
        self.dfDist = pd.read_csv('precomputed/GoalPremium.csv', delimiter=',')


    def get_goal_suit_premium(self, n_my_cards, n_pl_cards, prob_10):
        """
        Evaluates the premium of a suit being goal suit

        INPUTS:
            * n_my_cards (int): number of cards for the suit
            * n_pl_cards (list, 4 elements): list containing the number of cards each player has of the suit
            * prob_10 (double): probability of goal suit having 10 cards

        OUTPUTS:
            * premium in dollars of such suit being goal suit
        """

        # Easy cases
        if n_my_cards < 2:
            return 0.0
        elif n_my_cards > 6:
            return (2*100 + 120)/3.0
    
        # Not so simple cases
        condition   =   (self.dfDist['Me'] == n_my_cards) & \
                        (self.dfDist['Pl_2'] >= n_pl_cards[1]) & \
                        (self.dfDist['Pl_3'] >= n_pl_cards[2]) & \
                        (self.dfDist['Pl_4'] >= n_pl_cards[3])
        dfFilter = self.dfDist.copy(deep=True)
        dfFilter = dfFilter[condition]

        sum_condition_10 = dfFilter.iloc[:, :4].sum(axis=1) == 10
        sum_condition_8  = dfFilter.iloc[:, :4].sum(axis=1) == 8

        dfFilter.loc[sum_condition_10, 'Pr_goal'] = prob_10
        dfFilter.loc[sum_condition_8, 'Pr_goal']  = 1 - prob_10

        profit   = (dfFilter['Pr_goal']*dfFilter['Weight']*dfFilter['Pot']).sum()
        
        return  profit / dfFilter['Pr_goal'].sum(axis=0)