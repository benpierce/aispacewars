from agentbase import Agent 
from swtypes import Point 
from swtypes import MoveToCell
from swtypes import MoveFireLaser
from swtypes import MoveFireLeftMissile
from swtypes import MoveFireRightMissile
from swtypes import Cell 
from mcts import MCTSNode
import copy
import random

class MCTSAgent(Agent):
    def __init__(self, team, name, position=Point(0, 0), bearing=0):                
        super().__init__(team, name, position, bearing)
        self.num_rounds = 1
     
    def select_move(self, game_state):  
        gs = copy.deepcopy(game_state)  # So we don't mess with the existing gamestate

        root = MCTSNode(gs, self) 

        for i in range(self.num_rounds):
            node = root 
            while (not node.can_add_child()) and (not node.is_terminal()):
                node = self.select_child(node) 

            if node.can_add_child():
                node = node.add_random_child()             

            print('I''m {0} and I have {1} commands'.format(self.name, len(self.commands)))
            winner = self.simulate_random_game(node.game_state) 
            print('Winner {0} I''m {1} and I have {2} commands'.format(winner, self.name, len(self.commands)))

            while node is not None: 
                node.record_win(winner) 
                node = node.parent 

        best_move = None 
        best_pct = -1.0 

        for child in root.children:
            child_pct = child.winning_pct(self.team)  # My team
            if child_pct > best_pct:
                best_pct = child_pct 
                best_move = child.move 
        return best_move 

    def select_child(self, node):
        total_rollouts = sum(child.num_rollouts for child in node.children) 

        best_score = -1 
        best_child = None 
        for child in node.children:
            score = uct_score(total_rollouts, child.num_rollouts, child.winning_pct(self.team), self.temperature)
            if score > best_score:
                best_score = uct_score 
                best_child = child 
        return best_child 

    def uct_score(self, parent_rollouts, child_rollouts, win_pct, temperature):
        exploration = math.sqrt(math.log(parent_rollouts) / child_rollouts) 
        return win_pct + temperature * exploration 

    def simulate_random_game(self, game_state):
        while not game_state.is_over():
            for bot in [*game_state.world.human_ships, *game_state.world.alien_ships]:
                if bot.can_move():
                    bot_move = random.choice(game_state.legal_moves(bot))
                    if bot_move is not None:
                        game_state.apply_move(bot, bot_move) 

            # Saves the game state to the file and increments the world time
            game_state.next_world_tick()

        return game_state.winner()