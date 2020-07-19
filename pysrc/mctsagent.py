from agentbase import Agent 
from swtypes import Point 
from swtypes import MoveToCell
from swtypes import MoveFireLaser
from swtypes import MoveFireLeftMissile
from swtypes import MoveFireRightMissile
from swtypes import Cell 
from profile import Profile
from mcts import MCTSNode
import copy
import random
import math 

class MCTSAgent(Agent):
    def __init__(self, team, name, position=Point(0, 0), bearing=0):                
        super().__init__(team, name, position, bearing, True)
        self.num_rounds = 5000        # Number of random simulations so that we can find a good candidate move.
        self.temperature = 5.0        # Larger number means more exploration of unvisited nodes, while lower numbers will stick to the best nodes found thus far
        self.DEBUG = False
        self.DUMP = True        

    def select_move(self, game_state):          
        possible_moves = game_state.legal_moves(self)
        nodes = []
        cur_round = 0

        if self.DEBUG:
            print('******************************************************************************************')
            print('MCTSAgent {0} thinking about move on world tick {1}.'.format(self.name, game_state.world_tick))
            print('...There are {0} moves that can be explored in {1} rounds.'.format(len(possible_moves), self.num_rounds))

        # Init all possible moves that can be explored 
        for possible_move in possible_moves:
            nodes.append(MCTSNode(possible_move))

        for cur_round in range(1, self.num_rounds + 1):
            simulation_node = self.select_child(nodes) 
            agent_score = self.simulate_random_game(game_state, simulation_node.move, 50)
            if self.DEBUG:
                print('......Explored move {0} which scored {1}.'.format(simulation_node.move, agent_score))
            simulation_node.num_rollouts += 1 
            simulation_node.total_score += agent_score  

        # Now we need to pick from the best moves (in the case of a tie, we just choose a random one)
        best_score = -99999999
        best_moves = []
        
        for node in nodes: 
            if node.num_rollouts > 0:  # Only choose a move if we've done a simulation on it.
                if (not best_moves) or node.avg_score() > best_score:
                    best_moves = [node.move]
                    best_score = node.avg_score() 
                elif node.avg_score() == best_score:  # This is as good as our previous best move
                    best_moves.append(node.move) 

        if self.DUMP: 
            print('******************************************************************************************')
            unique_rollouts = 0
            print('................. DUMP...................')
            print('MCTSAgent {0} thinking about move on world tick {1}.'.format(self.name, game_state.world_tick))
            for node in nodes:                
                print('...Action {0} was explored {1} times with avg score of {2}'.format(node.move, node.num_rollouts, node.avg_score()))
                if node.num_rollouts > 0:
                    unique_rollouts += 1
            print('.........................................')
            print('')
            print('MCTSAgent {0} finished thinking about move on world tick {1}.'.format(self.name, game_state.world_tick))
            print('   -> Found {0} possible moves within {1} unique rollouts, having a score of {2}'.format(len(best_moves), unique_rollouts, best_score))
            if len(best_moves) == 1:
                print('   -> Best move was {0} for a score of {1}.'.format(best_moves[0], best_score))
                print('   -> Ships remaining: {0}'.format(game_state.world.get_ship_count()))
            else:
                print('   -> Multiple best moves: {0}'.format(len(best_moves)))
                print('   -> Ships remaining: {0}'.format(game_state.world.get_ship_count()))
            print('******************************************************************************************')
            print('')

        if len(best_moves) == 0:
            return None                 
        
        # For variety, randomly select among all equally good moves.
        return random.choice(best_moves)

    def select_child(self, nodes):
        total_rollouts = sum(node.num_rollouts for node in nodes) 
        choices = []

        best_score = -1 
        for node in nodes:
            score = self.uct_score(total_rollouts, node.num_rollouts, node.avg_score(), self.temperature)                

            if (not choices) or score > best_score:
                choices = [node]
                best_score = score 
            elif score == best_score:
                choices.append(node)

        if len(choices) == 0:
            return None 

        # If we have equally good moves to explore, return a random one so we don't get uniform results.
        return random.choice(choices) 

    def uct_score(self, parent_rollouts, child_rollouts, avg_score, temperature):
        exploration = math.sqrt(math.log((parent_rollouts + 1)) / (child_rollouts + 1)) 
        return avg_score + temperature * exploration 

    def simulate_random_game(self, game_state, move, sim_world_ticks):        
        cloned_game_state = game_state.clone()  # So we don't mess with the existing gamestate
        cur_agent = cloned_game_state.world.get_ship_by_name(self.name)
        cloned_game_state.apply_move(cur_agent, move, True)
        start_world_tick = cloned_game_state.world_tick 
        
        tick = 1
        while not cloned_game_state.is_over() and tick <= sim_world_ticks:
            for bot in [*cloned_game_state.world.alien_ships, *cloned_game_state.world.human_ships]:                
                if bot.can_move():
                    bot_move = random.choice(cloned_game_state.legal_moves(bot))                    
                    if bot_move is not None:
                        cloned_game_state.apply_move(bot, bot_move) 

            # Saves the game state to the file and increments the world time
            cloned_game_state.next_world_tick()

            tick +=1

        #if start_world_tick > 1:
        #    print('')
        #    print('Move = {0}'.format(move))
        #    cloned_game_state.world.get_ship_by_name(self.name).print_rewards(start_world_tick)
        #    print('')

        return cloned_game_state.get_agent_score_since(self.name, start_world_tick)
    