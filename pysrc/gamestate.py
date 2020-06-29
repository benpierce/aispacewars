from world import World 
from swtypes import Point
import os
import copy

class GameState():
    def __init__(self, world, replay_filename):
        self.world = world 
        self.world_tick = 1        
        self.replay_filename = replay_filename 

    def apply_move(self, agent, move):                
        next_world = copy.deepcopy(self.world)
        next_world.apply_move(agent, move)

        return GameState(next_world, self.replay_filename)

    @classmethod 
    def new_game(cls, height, width, humans, aliens, debug_info, replay_filename):
        world = World(height, width, debug_info, humans, aliens)          
        return GameState(world, replay_filename)

    def is_over(self):
        return self.world.is_gameover()

    def next_world_tick(self):
        self.world_tick += 1
        self.world.update_step(self.world_tick)

    def init_replay_file(self):        
        try:
            os.remove(self.replay_filename) 
            with open(self.replay_filename, 'a') as replay_file:
                replay_file.write('[\n')                
        except:
            pass

    def close_replay_file(self):
        with open(self.replay_filename, 'a') as replay_file:
            replay_file.write('\n]')

    # This method will serialize the gamestate of the entire world to the replay file.
    def serialize_gamestate(self):
        ship_count = self.world.get_ship_count()
        laser_count = self.world.get_laser_count()
        missile_count = self.world.get_missile_count()
        action_count = len(self.world.actions)
        info_count = len(self.world.debug_info.additionalInfo)
        ship_idx = 1
        laser_idx = 1
        missile_idx = 1
        action_idx = 1
        info_idx = 1

        with open(self.replay_filename, 'a') as replay_file:
            if self.world_tick > 1:
                replay_file.write(',\n')
            replay_file.write('   {\n')
            replay_file.write('      "tick": {0},\n'.format(self.world_tick))
            replay_file.write('      "object_state":\n')
            replay_file.write('      [\n')
                    
            # Lasers             
            for laser in self.world.lasers:
                if not laser.dead:
                    replay_file.write('         {\n')
                    replay_file.write('            "id": "{0}",\n'.format(laser.name))
                    replay_file.write('            "type": "{0}Laser",\n'.format(laser.team))
                    replay_file.write('            "x": "{0}",\n'.format(laser.position.x))
                    replay_file.write('            "y": "{0}",\n'.format(laser.position.y))
                    replay_file.write('            "r": "{0}"\n'.format(laser.bearing))
                    if ship_count > 0 or laser_idx != laser_count:
                        replay_file.write('         },\n')
                    else:
                        replay_file.write('         }\n')
                    laser_idx += 1

            # Missiles 
            for missile in self.world.missiles:
                if not missile.dead:
                    replay_file.write('         {\n')
                    replay_file.write('            "id": "{0}",\n'.format(missile.name))
                    replay_file.write('            "type": "{0}Missile",\n'.format(missile.team))
                    replay_file.write('            "x": "{0}",\n'.format(missile.position.x))
                    replay_file.write('            "y": "{0}",\n'.format(missile.position.y))
                    replay_file.write('            "r": "{0}"\n'.format(missile.bearing))
                    if ship_count > 0 or missile_idx != missile_count:
                        replay_file.write('         },\n')
                    else:
                        replay_file.write('         }\n')
                    missile_idx += 1

            for ship in [*self.world.human_ships, *self.world.alien_ships]:
                if not ship.dead:
                    if ship.left_missile:
                        replay_file.write('         {\n')
                        replay_file.write('            "id": "{0}LeftMissile",\n'.format(ship.name))
                        replay_file.write('            "type": "{0}Missile",\n'.format(ship.team))
                        replay_file.write('            "x": "{0}",\n'.format(ship.left_missile_position().x))
                        replay_file.write('            "y": "{0}",\n'.format(ship.left_missile_position().y))
                        replay_file.write('            "r": "{0}"\n'.format(ship.bearing))
                        replay_file.write('         },\n')
                    if ship.right_missile:
                        replay_file.write('         {\n')
                        replay_file.write('            "id": "{0}RightMissile",\n'.format(ship.name))
                        replay_file.write('            "type": "{0}Missile",\n'.format(ship.team))
                        replay_file.write('            "x": "{0}",\n'.format(ship.right_missile_position().x))
                        replay_file.write('            "y": "{0}",\n'.format(ship.right_missile_position().y))
                        replay_file.write('            "r": "{0}"\n'.format(ship.bearing))
                        replay_file.write('         },\n')
                    
                    replay_file.write('         {\n')
                    replay_file.write('            "id": "{0}",\n'.format(ship.name))
                    replay_file.write('            "type": "{0}Ship",\n'.format(ship.team))
                    replay_file.write('            "x": "{0}",\n'.format(ship.position.x))
                    replay_file.write('            "y": "{0}",\n'.format(ship.position.y))
                    replay_file.write('            "r": "{0}"\n'.format(ship.bearing))
                    if ship_idx == ship_count:
                        replay_file.write('         }\n')
                    else:
                        replay_file.write('         },\n')                                            
                    ship_idx += 1                        

            if action_count == 0:
                replay_file.write('      ]\n')              
            else:
                replay_file.write('      ],\n')
            
            if action_count > 0:
                replay_file.write('      "actions":\n')
                replay_file.write('      [\n')
                for action in [*self.world.actions]:
                    replay_file.write('         {\n')
                    replay_file.write('            "type": "{0}",\n'.format(action.type))
                    replay_file.write('            "id": "{0}",\n'.format(action.id))
                    replay_file.write('            "x": "{0}",\n'.format(action.x))
                    replay_file.write('            "y": "{0}",\n'.format(action.y))
                    replay_file.write('            "text": "{0}"\n'.format(action.text))
                    if action_idx == action_count:
                        replay_file.write('         }\n')
                    else:
                        replay_file.write('         },\n')                                            
                    action_idx += 1
                replay_file.write('      ]\n')  

            # Debug Info                 
            replay_file.write('      ,"debug_info":\n')
            replay_file.write('       {\n')
            replay_file.write('          "humanai": "{0}",\n'.format(self.world.debug_info.humanAI))
            replay_file.write('          "alienai": "{0}",\n'.format(self.world.debug_info.alienAI))
            replay_file.write('          "humanships": "{0}",\n'.format(self.world.debug_info.humanShips))
            replay_file.write('          "alienships": "{0}",\n'.format(self.world.debug_info.alienShips))            
            replay_file.write('          "additionalInfo":\n')
            replay_file.write('          [\n')
            if not self.world.debug_info.additionalInfo == None:
                for info in self.world.debug_info.additionalInfo:
                    replay_file.write('             {\n')
                    replay_file.write('                "info": "{0}"\n'.format(info))
                    if info_idx == info_count:
                        replay_file.write('             }\n')
                    else:
                        replay_file.write('             },\n')
                    info_idx += 1

            replay_file.write('          ]\n')
            replay_file.write('       }\n')
            
            replay_file.write('   }')                  
