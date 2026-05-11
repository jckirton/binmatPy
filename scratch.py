# from binmat.classes import *
# from binmat.constants import *
# from binmat.errors import *
from binmat.game import Game

game = Game(2)

while True:
    game.do_turn()
