import random 

class MCTSNode(object):
    def __init__(self, game_state, agent, parent=None, move=None):
        self.game_state = game_state 
        self.parent = parent 
        self.move = move         
        self.win_counts = {
            "Human": 0,
            "Alien": 0
        }
        self.num_rollouts = 0
        self.children = []
        self.agent = agent 
        self.unvisited_moves = game_state.legal_moves(agent)

    def add_random_child(self):
        index = random.randint(0, len(self.unvisited_moves) - 1)
        new_move = self.unvisited_moves.pop(index) 
        new_game_state = self.game_state.apply_move(self.agent, new_move) 
        new_node = MCTSNode(new_game_state, self.agent, self, new_move)
        self.children.append(new_node) 
        return new_node 

    def record_win(self, winner):
        if not (winner == None):
            self.win_counts[winner] += 1

        self.num_rollouts += 1 

    def can_add_child(self):
        return len(self.unvisited_moves) > 0 

    def is_terminal(self):
        return self.game_state.is_over() 

    def winning_pct(self, team):
        return float(self.win_counts[team]) / float(self.num_rollouts) 

    