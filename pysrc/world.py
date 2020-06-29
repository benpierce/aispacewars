from swtypes import Point
from swtypes import Cell
from swtypes import MoveToCell 
from swtypes import Action
from swtypes import CommandChangeBearing
from swtypes import CommandMoveForward
from swtypes import CommandFireLeftMissile
from swtypes import CommandFireRightMissile
from swtypes import CommandFireLaser
from swtypes import CollisionSetting
from swtypes import MoveFireLaser
from swtypes import MoveFireLeftMissile
from swtypes import MoveFireRightMissile
from laser import Laser
from missile import Missile 
from debuginfo import DebugInfo 
import math 
import datetime 

class World():
    def __init__(self, height, width, debug_info, human_ships = [], alien_ships = [], collisions = CollisionSetting.OnlyEnemyShips, cell_size = 40):
        self.height = height 
        self.width = width 
        self.cell_size = cell_size  
        self.human_ships = human_ships 
        self.alien_ships = alien_ships
        self.missiles = []
        self.lasers = []
        self.collisions = collisions 
        self.world_tick = 0
        self.actions = []
        self.debug_info = debug_info 
        self.last_update_time = datetime.datetime.now()
        self.smoke_count = 0

        # Constants
        self.ROTATION_SPEED_PER_TICK = 25.0
        self.THRUST_SPEED_PER_TICK = 25.0
        self.MISSILE_SPEED = 35.0   # How fast are missiles?
        self.LASER_SPEED = 75.0     # How fast is a laser shot?

        self.__init_ships__()   # Initialize ship positions

    # Returns the number of rows in the world
    def row_count(self):
        return self.height / self.cell_size

    # Returns the number of columns in the world
    def col_count(self):
        return self.width / self.cell_size

    # Returns True if the cell is in the gameworld, otherwise false.
    def cell_in_world(self, cell):
        if cell.row < 1 or cell.row > self.row_count():
            return False 

        if cell.col < 1 or cell.col > self.col_count():
            return False 

        return True 

    # Returns the game world center point for a particular cell
    def get_center_point(self, row, col):        
        x = (col * self.cell_size) - (self.cell_size / 2.0)
        y = (row * self.cell_size) - (self.cell_size / 2.0)
        
        return Point(x, y)
    
    def get_cell_from_point(self, point):
        row = math.ceil(point.y / self.cell_size)
        col = math.ceil(point.x / self.cell_size)

        return Cell(row, col)

    def get_ship_count(self):
        return self.get_human_ship_count() + self.get_alien_ship_count()

    def get_human_ship_count(self):
        cnt = 0
        for ship in [*self.human_ships]:
            if not ship.dead:
                cnt += 1

        return cnt 

    def get_alien_ship_count(self):
        cnt = 0
        for ship in [*self.alien_ships]:
            if not ship.dead:
                cnt += 1

        return cnt 

    def get_laser_count(self):
        cnt = 0
        for laser in self.lasers:
            if not laser.dead:
                cnt += 1 
        
        return cnt 

    def get_missile_count(self):
        cnt = 0
        for missile in self.missiles:
            if not missile.dead:
                cnt += 1 
        
        return cnt         

    def apply_move(self, agent, move):
        if isinstance(move, MoveToCell):
            self.__apply_movetocell__(agent, move)
        elif isinstance(move, MoveFireLeftMissile):
            self.__apply_firemissile__(agent, move, True)
        elif isinstance(move, MoveFireRightMissile):
            self.__apply_firemissile__(agent, move, False)
        elif isinstance(move, MoveFireLaser):            
            self.__apply_firelaser__(agent, move)

    # This method will calculate one step of physics in the gameworld.
    def update_step(self, world_tick):
        self.actions = [] # Reset all actions
        self.world_tick = world_tick 

        # Adjust laser and missile positions.
        self.step_laser()  
        self.step_missile()

        for ship in [*self.human_ships, *self.alien_ships]:              
            cmd = ship.current_command()
            if isinstance(cmd, CommandChangeBearing):
                self.step_rotation(ship, cmd)
            elif isinstance(cmd, CommandMoveForward):
                self.step_thrust(ship, cmd)
            elif isinstance(cmd, CommandFireLaser):
                self.process_laser(ship, cmd)
            elif isinstance(cmd, CommandFireLeftMissile):
                self.process_left_missile(ship, cmd) 
            elif isinstance(cmd, CommandFireRightMissile):
                self.process_right_missile(ship, cmd)      

        # Collision detection
        self.check_collisions()

        # Check to see if the game has ended
        self.check_gameover()

        # Kill off any out of bounds projectiles to reduce the replay file size.
        self.remove_outofbounds()

        # Update debug info 
        delta = datetime.datetime.now() - self.last_update_time 
        processingtime = int(delta.total_seconds() * 1000) 
        self.debug_info.update_ship_count(self.get_human_ship_count(), self.get_alien_ship_count())
        some_info = ['World Tick: {0}'.format(self.world_tick), 'Tick Processing Time (ms): {0}'.format(processingtime)]
        self.debug_info.update_additional_info(some_info)
        self.last_update_time = datetime.datetime.now()

    def remove_outofbounds(self):
        for laser in self.lasers:
            if not self.cell_in_world(self.get_cell_from_point(laser.position)):
                laser.kill()
        
        for missile in self.missiles:
            if not self.cell_in_world(self.get_cell_from_point(missile.position)):
                missile.kill()
    
    def check_gameover(self):
        message = ""

        if self.is_gameover():
            if self.get_ship_count() == 0:
                message = 'Both Sides Have Been Defeated!'
            elif self.get_human_ship_count() == 0:
                message = 'Aliens ({0}) Win!'.format(self.debug_info.alienAI)
            elif self.get_alien_ship_count() == 0:
                message = 'Humans ({0}) Win!'.format(self.debug_info.humanAI)

            self.actions.append(Action("message", None, None, None, message))

    def is_gameover(self):
        return self.get_human_ship_count() == 0 or self.get_alien_ship_count() == 0

    def check_collisions(self):
        for ship in [*self.human_ships, *self.alien_ships]:
            if ship.dead:
                continue 

            if self.collisions != CollisionSetting.CollisionsOff:
                for other in [*self.human_ships, *self.alien_ships]:
                    if ship.name == other.name:
                        continue 
                    if other.dead:
                        continue 
                    if ship.team == other.team and self.collisions == CollisionSetting.OnlyEnemyShips:
                        continue 
                    #if self.get_cell_from_point(ship.position) == self.get_cell_from_point(other.position):
                    if ship.is_touched(other.position):
                        self.actions.append(Action("explosion", ship.name, ship.position.x, ship.position.y, None))
                        ship.kill()
                        other.kill()

            # Did any lasers hit a ship?
            for laser in self.lasers:
                if laser.team == ship.team:   # Can only be hit by enemy laser, no friendly fire
                    continue 

                if laser.dead:
                    continue
                
                if ship.is_touched(laser.position):
                    laser.kill()
                    ship.health -= laser.damage
                    if ship.health <= 0:                    
                        self.actions.append(Action("explosion", ship.name, ship.position.x, ship.position.y, None))
                        ship.kill()
                    else:              
                        self.smoke_count += 1         
                        self.actions.append(Action("smoke", 'smoke{0}'.format(self.smoke_count), ship.position.x, ship.position.y, None))

            # Did any missiles hit a ship?
            for missile in self.missiles:
                if missile.dead:
                    continue 

                if ship.name == missile.owner:  # Your own missile can't hit you.
                    continue 

                if ship.is_touched(missile.position):
                    missile.kill()
                    ship.health -= missile.damage 
                    if ship.health <= 0:                    
                        self.actions.append(Action("explosion", ship.name, ship.position.x, ship.position.y, None))
                        ship.kill()
                                
    def step_rotation(self, agent, command):
        if command.is_clockwise:      
            if agent.bearing + self.ROTATION_SPEED_PER_TICK >= 360:
                overflow = 360 - (agent.bearing + self.ROTATION_SPEED_PER_TICK)      
                agent.bearing = 0 + overflow 
            else:
                agent.bearing += self.ROTATION_SPEED_PER_TICK
        else:            
            if agent.bearing - self.ROTATION_SPEED_PER_TICK < 0:
                overflow = 0 - (agent.bearing - self.ROTATION_SPEED_PER_TICK)
                agent.bearing = 360 - overflow
            else:
                agent.bearing -= self.ROTATION_SPEED_PER_TICK

        # If we're within a world tick of the rotation, just set us there and remove this command.
        if self.rotation_diff(agent.bearing, command.target_bearing) < self.ROTATION_SPEED_PER_TICK:
            agent.bearing = command.target_bearing 
            agent.command_finished()

    def rotation_diff(self, angle1, angle2):
        phi = abs(angle2 - angle1) % 360 
        if phi > 180:
            return 360 - phi 
        else:
            return phi                    
        
    def step_thrust(self, agent, command):
        target = self.get_center_point(command.target_cell.row, command.target_cell.col)

        distance = math.sqrt(math.pow(target.x - agent.position.x, 2) + math.pow(target.y - agent.position.y, 2))

        if distance > self.THRUST_SPEED_PER_TICK:
            dx = (target.x - agent.position.x) / distance 
            dy = (target.y - agent.position.y) / distance 
            agent.position.x += (dx * self.THRUST_SPEED_PER_TICK)
            agent.position.y += (dy * self.THRUST_SPEED_PER_TICK)
        else:
            agent.position.x = target.x 
            agent.position.y = target.y 
            agent.command_finished()    

    def process_laser(self, agent, command):        
        agent.last_laser_world_tick = self.world_tick 
        name = 'laser{0}'.format(len(self.lasers) + 1)
        start_pos = self.relative_position(agent, Point(agent.position.x, (agent.position.y - 20)))
        #start_pos = Point(agent.position.x, agent.position.y)

        laser = Laser(agent.team, name, start_pos, agent.bearing)        
        self.lasers.append(laser)
        agent.command_finished()

    def process_left_missile(self, agent, command):
        name = 'missile{0}'.format(len(self.missiles) + 1)
        start_pos = agent.left_missile_position()
        missile = Missile(agent.team, name, agent.name, start_pos, agent.bearing) 
        self.missile_action(agent)
        self.missiles.append(missile) 
        agent.left_missile = False 
        agent.command_finished()

    def process_right_missile(self, agent, command):
        name = 'missile{0}'.format(len(self.missiles) + 1)
        start_pos = agent.right_missile_position()
        missile = Missile(agent.team, name, agent.name, start_pos, agent.bearing) 
        self.missile_action(agent)
        self.missiles.append(missile) 
        agent.right_missile = False 
        agent.command_finished()

    def missile_action(self, agent):
        if agent.team.upper() == 'HUMAN':
            self.actions.append(Action("firehumanmissile", agent.name, agent.position.x, agent.position.y, None))
        else:
            self.actions.append(Action("firealienmissile", agent.name, agent.position.x, agent.position.y, None))

    # Loops through each laser and increments the position or destroys the object if it's off screen.
    def step_laser(self):
        for laser in self.lasers:
            x = self.LASER_SPEED * math.cos(math.radians(laser.bearing - 90))
            y = self.LASER_SPEED * math.sin(math.radians(laser.bearing - 90)) 
            laser.position.x += x 
            laser.position.y += y 

    def step_missile(self):
        for missile in self.missiles:
            x = self.MISSILE_SPEED * math.cos(math.radians(missile.bearing - 90))
            y = self.MISSILE_SPEED * math.sin(math.radians(missile.bearing - 90)) 
            missile.position.x += x 
            missile.position.y += y                         

    # Gets the x,y coordinates relative to a ship's center and rotation.
    def relative_position(self, ship, dst):
        x = dst.x
        y = dst.y

        angle = (ship.bearing) * (math.pi/180);   # Convert to radians
        rotatedX = math.cos(angle) * (x - ship.position.x) - math.sin(angle) * (y - ship.position.y) + ship.position.x;
        rotatedY = math.sin(angle) * (x - ship.position.x) + math.cos(angle) * (y - ship.position.y) + ship.position.y;

        return Point(rotatedX, rotatedY)

    def __apply_movetocell__(self, agent, move):
        bearingcmd = self.__getbearingcmd__(agent, move.target_cell)
        forwardcmd = CommandMoveForward(move.target_cell)

        agent.add_command(bearingcmd)
        agent.add_command(forwardcmd)

    def __apply_firemissile__(self, agent, move, left_missile):
        if left_missile and agent.can_fire_left_missile():             
            self.__init_missile__(move, agent, left_missile)
        elif not left_missile and agent.can_fire_right_missile():
            self.__init_missile__(move, agent, left_missile)

    # Can only fire one laser unless the cooldown is over.
    def __apply_firelaser__(self, agent, move):
        if agent.last_laser_world_tick + agent.LASER_COOLDOWN < self.world_tick:
            self.__init_laser__(agent, move)

    # Instantiate a missile, set it's rotation and trajectory and let it rip.
    def __init_missile__(self, move, agent, left_missile):
        bearingcmd = self.__getbearingcmd__(agent, move.target_cell)
        if left_missile:
            missilecmd = CommandFireLeftMissile() 
        else:
            missilecmd = CommandFireRightMissile() 

        agent.add_command(bearingcmd) 
        agent.add_command(missilecmd)

    # Instantiate the correct laser
    def __init_laser__(self, agent, move):
        bearingcmd = self.__getbearingcmd__(agent, move.target_cell)
        lasercmd = CommandFireLaser() 

        agent.add_command(bearingcmd)
        agent.add_command(lasercmd)

    # Calculates what the new bearing should be, given an agent's target cell
    def __getbearingcmd__(self, agent, target_cell):
        current_position = agent.position 
        target_position = self.get_center_point(target_cell.row, target_cell.col) 

        dx = target_position.x - current_position.x 
        dy = target_position.y - current_position.y                 
        theta = math.atan2(dy, dx)
        theta %= 2*math.pi 
        target_bearing = math.degrees(theta) + 90
        
        is_clockwise = self.get_best_rotation_direction(agent.bearing, target_bearing)
        return CommandChangeBearing(target_bearing, is_clockwise)            

    def get_best_rotation_direction(self, current_angle, target_angle):
        d1 = (target_angle - current_angle) % 360 
        d2 = (current_angle - target_angle) % 360 
        if d1 <= d2:
            return True 
        else:
            return False 

    # Creates initial ship positions, with Humans on the left and Aliens on the right. 
    def __init_ships__(self):
       assert len(self.human_ships) <= self.col_count(), "Can only place {0} human ships.".format(self.col_count()) 
       assert len(self.alien_ships) <= self.col_count(), "Can only place {0} alien ships.".format(self.col_count()) 

       # Ship placement starts in the middle (for one ship) and scales out evenly.
       # Humans first
       middle_cell = math.ceil((self.col_count() / 2.0))
       ships_placed = 0
       col = 0
       for ship in self.human_ships:           
           if ships_placed % 2 == 1:
               col = middle_cell + math.ceil(ships_placed / 2.0)
           else:
               col = middle_cell - math.ceil(ships_placed / 2.0)

           ship.position = self.get_center_point(self.row_count(), col)
           ship.bearing = 0
           ships_placed += 1

       # Aliens
       ships_placed = 0 
       for ship in self.alien_ships:
           if ships_placed % 2 == 1:
               col = middle_cell + math.ceil(ships_placed / 2.0)
           else:
               col = middle_cell - math.ceil(ships_placed / 2.0)

           ship.position = self.get_center_point(1, col)
           ship.bearing = 180
           ships_placed +=1                 



