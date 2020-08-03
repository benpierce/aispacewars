import naive 
import mctsagent 
from gamestate import GameState 
from debuginfo import DebugInfo 
from profile import Profile 
import datetime 
import types 
import os

def main():
    start_time = datetime.datetime.now()
    worldTick = 0
    humans = []
    aliens = []
    for i in range(20):    
        humans.append(mctsagent.MCTSAgent('Human', 'Human ' + str(i + 1)))
        aliens.append(naive.RandomBot('Alien', 'Alien ' + str(i + 1)))
        #aliens.append(mctsagent.MCTSAgent('Alien', 'Alien ' + str(i + 1)))

    humanAI = clean_class_name(str(type(humans[0])))
    alienAI = clean_class_name(str(type(aliens[0])))
    debug_info = DebugInfo(humanAI, alienAI, len(humans), len(aliens), [])

    game = GameState.new_game(600, 800, humans, aliens, debug_info, "../replays/replay2.json")
    game.init_replay_file()
    game.serialize_gamestate()

    iter = 1
    while not game.is_over():
        for bot in [*aliens, *humans]: 
            if bot.can_move():
                bot_move = bot.select_move(game) 
                if bot_move is not None:
                    game.apply_move(bot, bot_move) 
        
        iter += 1
        # Saves the game state to the file and increments the world time
        game.next_world_tick() 
        game.serialize_gamestate()
    
    game.close_replay_file() 

    Profile.dump()

    delta = datetime.datetime.now() - start_time 
    print('TOTAL RUN TiME: {0}'.format(delta.total_seconds() * 1000))

# Transforms a class string to something a little more friendly.
# <class 'naive.RandomBot'> -> RandomBot
def clean_class_name(name):
    n = name[name.index('.') + 1:]
    n = n[0:n.index("'")]

    return n

if __name__ == '__main__':
    main() 