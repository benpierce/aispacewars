import random 
import math 
from agentbase import Agent 
from swtypes import Point 
from swtypes import MoveToCell
from swtypes import MoveFireLaser
from swtypes import MoveFireLeftMissile
from swtypes import MoveFireRightMissile
from swtypes import Cell 

class RandomBot(Agent):
    def __init__(self, team, name, position=Point(0, 0), bearing=0):        
        super().__init__(team, name, position, bearing)

    def select_move(self, game_state): 
        return random.choice(game_state.legal_moves(self))