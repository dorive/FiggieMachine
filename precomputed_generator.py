import numpy as np
import pandas as pd




run_goal_premium = False
run_goal_distribution = True





##################################################################
# GoalPremium.csv generator
# Computes all the possible distributions of cards between
# four players, the goal suit pot and the weight you will
# win in each case.
##################################################################


if run_goal_premium:

    dfDist = pd.DataFrame(0.0, index=range(249), columns=['Me','Pl_2','Pl_3','Pl_4', 'Pr_goal', 'Weight', 'Pot'])

    count = 0

    for nn in range(2,11):
        for py2 in range(11):
            for py3 in range(11):
                for py4 in range(11):
                    dist = [nn, py2, py3, py4]

                    # Only two cases, 10-cards or 8-cards
                    if (np.sum(dist) == 10) or (np.sum(dist) == 8):

                        # Cards distribution
                        dfDist.iloc[count, :4] = dist

                        # Pot
                        if np.sum(dist) == 10:
                            dfDist.iloc[count, 6] = 100
                        else:
                            dfDist.iloc[count, 6] = 120

                        # Weights
                        if dist[0] > np.max(dist[1:]):
                            dfDist.iloc[count, 5] = 1.0
                        elif dist[0] == np.max(dist[1:]):
                            dfDist.iloc[count, 5] = 1.0/(dist.count(np.max(dist[1:])))
                        elif dist[0] < np.max(dist[1:]):
                            dfDist.iloc[count, 5] = 0.0

                        count += 1           

    dfDist.to_csv("precomputed/GoalPremium.csv", index=False)








##################################################################
# GoalDist.csv generator
# Computes all the possible distributions of seen cards between
# four players, the probabability of being goal suit and
# the probability of being 10 cards.
##################################################################

if run_goal_distribution:

    def prob_calculation(suits, temp):
        d_goal = np.prod([gg/(40-idx) for idx, gg in enumerate(range(suits[0],suits[0]-temp[0],-1))]) * \
                np.prod([gg/(40-temp[0]-idx) for idx, gg in enumerate(range(suits[1],suits[1]-temp[1],-1))]) * \
                np.prod([gg/(40-temp[0]-temp[1]-idx) for idx, gg in enumerate(range(suits[2],suits[2]-temp[2],-1))]) * \
                np.prod([gg/(40-temp[0]-temp[1]-temp[2]-idx) for idx, gg in enumerate(range(suits[3],suits[3]-temp[3],-1))])
        
        return d_goal

    count = 0

    dfGoalSuit = pd.DataFrame(0.0, index=np.arange(6993), columns=['Suit_1', 'Suit_2', 'Suit_3', 'Suit_4', 
                                                                'Pr_suit_1', 'Pr_suit_2', 'Pr_suit_3', 'Pr_suit_4',
                                                                'Pr_10_1', 'Pr_10_2', 'Pr_10_3', 'Pr_10_4']) 

    for ii in range(13):
        for jj in range(13):
            for zz in range(13):
                for ww in range(13):
                    temp = np.array([ii, jj, zz, ww])

                    if (temp.sum() <= 40) and \
                    (np.count_nonzero(temp == 12) < 2) and \
                    (np.count_nonzero(temp > 10) < 2) and \
                    (np.count_nonzero(temp > 8) < 4) and \
                    (temp[0] >= np.max(temp[1:])): 
                        
                        dfGoalSuit.iloc[count, 0:4] = temp

                        # Deck1: 12,10,10,8 -- Goal = 2
                        suits = [12, 10, 10, 8]
                        d1_goal = prob_calculation(suits, temp)
                        
                        # Deck2:  12,10,8,10 -- Goal = 2
                        suits = [12, 10, 8, 10]
                        d2_goal = prob_calculation(suits, temp)
                        
                        # Deck3:  12,8,10,10 -- Goal = 2
                        suits = [12, 8, 10, 10]
                        d3_goal = prob_calculation(suits, temp)
                        
                        # Deck4:  8,12,10,10 -- Goal = 1
                        suits = [8, 12, 10, 10]
                        d4_goal = prob_calculation(suits, temp)
                        
                        # Deck5:  10,12,10,8 -- Goal = 1
                        suits = [10, 12, 10, 8]
                        d5_goal = prob_calculation(suits, temp)
                        
                        # Deck6:  10,12,8,10 -- Goal = 1
                        suits = [10, 12, 8, 10]
                        d6_goal = prob_calculation(suits, temp)

                        # Deck7:  10,8,12,10 -- Goal = 4
                        suits = [10, 8, 12, 10]
                        d7_goal = prob_calculation(suits, temp)
                        
                        # Deck8:  8,10,12,10 -- Goal = 4
                        suits = [8, 10, 12, 10]
                        d8_goal = prob_calculation(suits, temp)
                        
                        # Deck9:  10,10,12,8 -- Goal = 4
                        suits = [10, 10, 12, 8]
                        d9_goal = prob_calculation(suits, temp)

                        # Deck10: 10,10,8,12 -- Goal = 3
                        suits = [10, 10, 8, 12]
                        d10_goal= prob_calculation(suits, temp)
                        
                        # Deck11: 10,8,10,12 -- Goal = 3
                        suits = [10, 8, 10, 12]
                        d11_goal= prob_calculation(suits, temp)
                        
                        # Deck12: 8,10,10,12 -- Goal = 3
                        suits = [8, 10, 10, 12]
                        d12_goal= prob_calculation(suits, temp)

                        # Probabilities of being goal suit
                        sum_tot = d1_goal + d2_goal + d3_goal + d4_goal + d5_goal + d6_goal + d7_goal + d8_goal + d9_goal + d10_goal + d11_goal + d12_goal
                        dfGoalSuit.iloc[count, 4] = (d4_goal + d5_goal + d6_goal) / sum_tot
                        dfGoalSuit.iloc[count, 5] = (d1_goal + d2_goal + d3_goal) / sum_tot
                        dfGoalSuit.iloc[count, 6] = (d10_goal + d11_goal + d12_goal) / sum_tot
                        dfGoalSuit.iloc[count, 7] = (d7_goal + d8_goal + d9_goal) / sum_tot

                        # Probabilities of goal suit having 10 cards
                        dfGoalSuit.iloc[count, 8]  = np.nan_to_num((d5_goal + d6_goal) / (d4_goal + d5_goal + d6_goal), nan=0.0)
                        dfGoalSuit.iloc[count, 9]  = np.nan_to_num((d1_goal + d2_goal) / (d1_goal + d2_goal + d3_goal), nan=0.0)
                        dfGoalSuit.iloc[count, 10] = np.nan_to_num((d11_goal + d12_goal) / (d10_goal + d11_goal + d12_goal), nan=0.0)
                        dfGoalSuit.iloc[count, 11] = np.nan_to_num((d7_goal + d8_goal) / (d7_goal + d8_goal + d9_goal), nan=0.0)

                        count += 1

    dfGoalSuit = dfGoalSuit.round(3)
    dfGoalSuit.to_csv('precomputed/GoalDist.csv', index=False)   