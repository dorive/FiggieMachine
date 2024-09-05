import pandas as pd
import numpy as np

class GoalSuitEstimator:

    def __init__(self) -> None:

        # Load precomputed probabilities
        self.dfPreProb = pd.read_csv('precomputed/GoalDist.csv', delimiter=',')


    def get_goalsuit_prob(self, n_suits):
        """
        Evaluates the probability of being goal suit [spades, clubs, hearts, diamonds]

        INPUTS:
            * n_suits (list): list containing the number of cards for each suit [spades, clubs, hearts, diamonds]

        OUTPUTS:
            * list containing the probability of being goal suit [spades, clubs, hearts, diamonds]
            * list containing the probability of goal suit having 10 cards [spades, clubs, hearts, diamonds]
        """

        # Reorder suits based on largest suit 
        idx_max = np.argmax(n_suits)

        if idx_max == 1:
            new_n_suits = [n_suits[1], n_suits[0], n_suits[2], n_suits[3]]
        elif idx_max == 2:
            new_n_suits = [n_suits[2], n_suits[3], n_suits[0], n_suits[1]]
        elif idx_max == 3:
            new_n_suits = [n_suits[3], n_suits[2], n_suits[0], n_suits[1]]
        else:
            new_n_suits = n_suits

        # Get the probabilities
        probs = self.dfPreProb[ (self.dfPreProb['Suit_1'] == new_n_suits[0]) & \
                                (self.dfPreProb['Suit_2'] == new_n_suits[1]) & \
                                (self.dfPreProb['Suit_3'] == new_n_suits[2]) & \
                                (self.dfPreProb['Suit_4'] == new_n_suits[3])].iloc[:,4:8].values[0]
            
        probs = list(probs)

        probs_10 = self.dfPreProb[  (self.dfPreProb['Suit_1'] == new_n_suits[0]) & \
                                    (self.dfPreProb['Suit_2'] == new_n_suits[1]) & \
                                    (self.dfPreProb['Suit_3'] == new_n_suits[2]) & \
                                    (self.dfPreProb['Suit_4'] == new_n_suits[3])].iloc[:,8:].values[0]
        probs_10 = list(probs_10)

        
        # Reorder the suits
        if idx_max == 1:
            return [probs[1], probs[0], probs[2], probs[3]], [probs_10[1], probs_10[0], probs_10[2], probs_10[3]]
        elif idx_max == 2:
            return [probs[2], probs[3], probs[0], probs[1]], [probs_10[2], probs_10[3], probs_10[0], probs_10[1]]
        elif idx_max == 3:
            return [probs[2], probs[3], probs[1], probs[0]], [probs_10[2], probs_10[3], probs_10[1], probs_10[0]]
        else:
            return probs, probs_10
