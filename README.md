# FiggieMachine
Trading algorithm used for [Figgie Wars](https://figgiewars.com/) competition based on Jane Street's [Figgie game](https://www.figgie.com/index.html). The algorithm is based on an statistical approach. Portfolio value is computed by keeping track of game events and cards. To set up the exchange visit the repo  [Figgie Testnet](https://github.com/0xDub/figgie-tournament-testnet).

Relevant files:
* `precomputed_generator.py`: script that precomputes relevant values to estimate goal suit probabilities.
* `GameController.py`: keeps track of all cards, players and so on.
* `GameStrategy.py`: performs the strategy  step by step.
* `PortfolioEval.py`: computes portfolio evaluation and relevant quotes. `Portfolio_Monocolor.py` and  `Portfolio_Monocolor2.py` implement different quoting strategies.

Contributions are welcomed :)





