# AI Space Wars: A Multi-Agent, Monte Carlo Tree Search

# Introduction

As a fan of Real Time Strategy (RTS) games, my initial concept for a term project was a grand space battle featuring a team of 20 human spaceships utilizing AI, fighting a team of 20 alien spaceships taking random actions. Each ship would be able to fly to anywhere in the game world, as well as fire missiles and lasers. The first team to eliminate the other would win. 

As both the term and project progressed, I quickly realized that I had inadvertently chosen an exceedingly difficult subject matter in multi-agent AI, having many serious challenges that included:
* An extremely high branching factor and state-action space.
* A performance-intensive simulation that would limit the number of rollouts that were feasible.
* A complex reward system that could involve more than just a win/loss reward for each episode.
* With a large state-action space, exploration vs exploitation would have to be carefully balanced.
* The lack of an overall team strategy; in other words, making agents less selfish and more balanced for team play.

Because of the enormous state-action space, I decided to use a modified Monte Carlo Tree Search which I hoped would result in each agent (ship) choosing statistically advantageous actions for the team. This document outlines each of the challenges faced, and how they were overcome. This document also highlights a few interesting simulations that can be viewed directly inside your web browser.

# Simulation Code

Much of the code is related to the simulation itself; however, key pieces of code can be found in the following files:

* **mctsagent.py**: This contains the code specific to the Monte Carlo Tree Search and UCT algorithm and is inspired by the book “Deep Learning and the Game of Go” written by Max Pumperla and Kevin Ferguson.
* **spacewars.py**: This is the main entry point into the simulation which can be run like this:

```
python spacewars.py
```

* **world.py**: Most of the simulation / physics take place here.
* **gamestate.py**: The game state (which contains a copy of the world). This pattern was also inspired by “Deep Learning and the Game of Go”.
* **agentbase.py**: This is the base class for both the Random and MCTS agent. The reward system is also defined in this class, as a constant.

# A Harsh World

Before discussing the various challenges associated with this particular multi-agent implementation, it is important to first understand the specific rules that govern this simulation. Nearly all the rules set forth are controlled through startup configuration; however, I will discuss only the final rules that made it into the simulation after numerous tuning iterations.

![A Harsh World](https://github.com/benpierce/aispacewars/blob/master/images/figure1.png)

(*Figure 1.1 - A harsh intergalactic battleground*)

## Teams

There are always two teams: humans, who start at the bottom of the world and are represented by grey ships, and aliens who always start at the top of the world and are represented by black ships. The starting number of ships on each team is always equal, and this starting number is controlled by an application variable. Most simulations were 20vs20, but some simulations were generated with a smaller number of ships in order to speed up testing and validation. 

## Agents

Each individual agent (ship) is controlled by either a Random AI, or a Monte Carlo AI. The simulation does not allow teams to mix AI types, so there were no simulations where part of a team was random and the other part Monte Carlo. Most of the simulations were setup such that the human team (grey ships) used the Monte Carlo AI, while the alien team (black ships) used a Random AI. This was done as a control method, as one would expect the Monte Carlo AI to beat the Random AI most of the time. It is also important to note that each ship, regardless of AI, is still bound by the physics of the game world such that no team has an unfair advantage in terms of abilities. 

## Actions

Each ship is always in one of two states: executing an action or choosing an action. If a ship is in the process of executing an action, it cannot cancel the existing action and must wait for the action animation to play out before it chooses a new action. When choosing an action, an agent has 3 options: move, fire a missile, or shoot a laser. 

**Move**: Each individual ship is capable of moving to any area of the world. Movement involves a ship changing its bearing (rotating towards its destination coordinates) and then thrusting straight until it arrives. Each ship is limited by a static thrust speed; thus, travel speed is the same for all agents. A ship travelling from one corner of the game world to the opposite corner could take a few seconds.

**Missiles**: Each ship starts with two missiles attached to it. Missiles are immensely powerful and can destroy a ship with one direct hit. The disadvantages of missiles are that they are finite (each ship only has 2 non-regenerating missiles), they can hit friendly agents, and they are relatively slow: only 40% faster than ship thrust speed. For these reasons, we would expect an optimal strategy to encompass conservation of missiles until direct hits could be guaranteed without the risk of friendly fire.

**Lasers**: Lasers are less powerful projectiles in that it takes 3 direct laser hits to kill a ship. Their advantages are that ships have an infinite number of laser shots, they cannot hit friendly agents, and they are extremely fast, travelling 3x as fast as a ship and double the speed of a missile. Lasers also have a 2 second cooldown, so agents must be careful in taking their shots. 

**Death**: The game world is harsh, and death can come in a number of ways, including:
1. Ship Collisions: A ship can fly through friendly ships, but if it touches an enemy ship, both ships are destroyed. Optimal strategies here may vary, as ships can themselves be used as weapons.
1. Missiles: A direct hit with a missile is instant death. It is important to note that missiles do not discriminate between ships. Friendly fire is a very serious reality. 
1. Lasers: 3 direct enemy laser hits are enough to destroy a ship. Friendly laser fire passes straight through friendly ships, so laser fire is more forgiving.

## Winning and Losing

The game is over when all ships on one of the teams have been eliminated. In some rare cases it is possible for a tie to occur if all ships are eliminated at the same time.
Feel free to view some sample simulations, [Here](https://benpierce.github.io/aispacewars/) if you'd like to watch the above simulation rules in action.

# Challenges and Solutions

## High Branching Factor and Action-State Space

One of the primary challenges encountered in this project was that the large number of agents along with all possible actions meant that the branching factor was nearly infinite, given a long enough episode. To get a sense of this, consider a conservative simulation with 40 agents that execute roughly 10 actions before the episode ends. Now consider that each of the 3 actions (move, missile, laser) can be targeted against any coordinate in an 800x600 world:

**{A,S}** = 40 agents X 10 actions X 3 possible actions X 480,000 coordinates = **570 million**

Clearly the action-state space is far too large for a Monte Carlo Tree Search to competently find a statistically relevant move. 

To reduce the action-state space, the world was divided into a 20x15 grid and agents were coded to execution actions against coordinate approximations rather than discrete coordinates. Thus, 480,000 unique coordinates were then compressed into 300 approximate coordinates. 

![Gridworld](https://github.com/benpierce/aispacewars/blob/master/images/figure2.png)

(*Figure 1.2 – Reduction of pixel coordinates to cell-based coordinates*)

The new compressed branching factor thus changed to:

**{A,S}** = 40 agents X 10 actions X 3 possible actions X 300 coordinates = **360,000**

A further reduction in branching factor was later achieved by limiting the tree depth to a maximum of 50 world ticks, as opposed to a potentially larger depth that would encompass an entire episode.

## Performance

Simulation performance was another significant challenge encountered throughout the project, and many times I had to take a step back and spend days performance tuning code so that episodes could be completed faster. Faster episode completion meant that more rollouts could be performed, and thus better node statistics were available, allowing each agent to select statistically better moves. 

For brevity’s sake, this report won’t go too deep into the performance tuning that was done; however, it's worth mentioning that the hotspots were able to be identified with a new '*Profile*' class that was developed and inserted into the codebase to measure runtimes in various blocks of code. Surprisingly, one of the biggest hotspots ended up being the calculation of legal moves available to agents, and this is where most of the optimization time was spent, pre-computing moves.

## Optimizing the Reward System

With a smaller branching factor and more rollouts able to be performed each turn, the Monte Carlo Tree  Search team started to win more often; however, the ships made a number of curious choices that were eventually tied back to the rewards system being too simple: +1 for a team win, 0 for a tie, -1 for a team loss. Curious observations made with this simplistic reward system included:

* Monte Carlo ships were more than happy to sacrifice themselves via kamikaze if it meant taking an enemy ship with it. 
* Too many Monte Carlo ships were needlessly destroyed by friendly missile fire. Agents showed no consideration for their teammates and were too quick to rely on their most devastating weapon, regardless of the consequences. 

While these might constitute valid strategies in a "win at any cost" mentality, it was hard to spot the "intelligence" and, in any event, it made for dull episodes. Thus, a slightly more advanced reward strategy was built into the simulation that was eventually tuned to the following:

Action | Description | Score
------------ | ------------- | -------------
Kamikaze | Running into an enemy ship and sacrificing the agent’s own ship. | -6
Team Lost	| All the agent’s team’s ships were destroyed; thus the episode was lost. | -4
Agent Died |Agent’s ship was destroyed, but the episode was not necessarily lost.	| -1
Hit by Laser | Agent’s ship was hit by laser fire (but not necessarily destroyed). | -0.33
Friendly Fire |	Agent destroyed a teammate’s ship via missile fire. | -4
Lasered Enemy	| Agent scored a laser hit against an enemy ship. | 2
Killed Enemy | Agent killed an enemy through laser fire, missile, or kamikaze. | 1
Survived | Agent survived the entire episode. | 4
Team Won | Agent’s team won the episode (although the agent did not have to survive to receive this score). | 4

While the above rewards did not completely eliminate moves that one might consider 'stupid', it did significantly improve the strategies taken by Monte Carlo agents from an aesthetic perspective.

One other important note about the reward system is that a time scaled 'gamma' parameter was introduced to the reward system. This value was set at 0.9 and biased the agent’s decisions towards those actions that would provide more immediate rewards. The goal with this parameter was to cut down on situations where agents were ignoring obvious actions (such as shooting an enemy right beside them) in favor of a non-guaranteed, longer-term reward, that might not come.

## Exploration vs Exploitation

There are approximately 1200 potential actions that an agent can take on any given turn:

*{move, laser, left missile, right missile} * 300 grid cells = **1200** possible actions*

In order to make the best decision using the Monte Carlo Tree Search, a balance needed to be found in terms of gathering more accurate statistics on promising rollouts vs exploring for better potential actions. To accommodate this exploration vs exploitation balance, an Upper Confidence Tree (UCT) formula was used, with the implementation as follows:

```python
def uct_score(self, parent_rollouts, child_rollouts, avg_score, temperature):
   exploration = math.sqrt(math.log((parent_rollouts + 1)) / (child_rollouts + 1))
 
   return avg_score + temperature * exploration 
```
Based on the specific reward system used in this project, hyperparameter tuning of the temperature variable to *5.0* seemed to yield good results where most nodes were explored, but promising nodes were explored in much more detail. Below is a screenshot of some of the nodes explored during one agent's turn: as you can see the node MoveToCell(8,19) is explored 121 times because it has the **highest** average reward, whereas other nodes such as MoveToCell(8,18) and MoveToCell(8,20) are still explored, but less time is spent on them because they have a lower average reward yield.

![Exploration](https://github.com/benpierce/aispacewars/blob/master/images/figure3.png)

(*Figure 1.3 – Monte Carlo exploration of the action space*)

## Lack of Overall Team Strategy
	
For all the challenges listed in this report, lack of a cohesive team strategy was the most difficult to solve for; and indeed, the final result only shows small gleams of overall team strategy. During initial simulations using only a simplified team win or team loss reward system, agents had no regard for their own safety or the safety of their compatriots. Far too often friendly fire and self-destruction by kamikaze were observed, and consequently the team consisting of random agents would sometimes win. 

As previously mentioned, friendly fire, kamikazes and dying were given negative rewards and this gave the facade of better team work; however, true team work would likely require additional work involving the implementation of a multi-level AI, whereby team-based AI would first generalize on strategies for the entire team, or groups of agents on the team, and then each agent's AI would then be further constrained to the allowable actions that the team-based AI had given it. For instance, it's entirely conceivable that a team-based AI could order a group of 3 agents to flank an enemy, and the AI of those 3 agents would then be constrained to move somewhere above or below the targeted enemy, but not fire until the order was given from the team-based AI.

Unfortunately, time constraints prevented a multi-level solution from being implemented.

# Watching the Scenarios Unfold

All of the simulations discussed in this report can be viewed in real-time from this URL: [https://benpierce.github.io/aispacewars/](https://benpierce.github.io/aispacewars/)

Below is a brief description of 7 simulations that had interesting elements.

## Game 1: 1v1 (Monte Carlo vs Random)

**URL**: [https://benpierce.github.io/aispacewars/?replay=0](https://benpierce.github.io/aispacewars/?replay=0)

This is a full 20v20 battle between Monte Carlo agents (Human) and Random AI (Aliens). With a tuned reward system in place, agents effectively avoid kamikazes, friendly fire, and other dangerous moves. This simulation is typical of all the final simulations, in that the Monte Carlo team would normally win by a safe margin, despite suffering some losses.

![20v20](https://github.com/benpierce/aispacewars/blob/master/images/figure4.png)

(*Figure 1.4 – A typical episode where the Monte Carlo team would win by a safe margin*)

## Game 2: 1v1 (Monte Carlo vs Random)

**URL**: [https://benpierce.github.io/aispacewars/?replay=1](https://benpierce.github.io/aispacewars/?replay=1)
Another full 20v20 battle between Monte Carlo agents (Human) and Random AI (Aliens). The Monte Carlo team wins with only 4 ships remaining, which was one of the closer final simulations performed. Despite the close result, the Monte Carlo team is effective in the early part of the match in establishing relatively safe positioning, with many of the Random agents falling victim to missile fire in the center of the map.	

## Game 3: 20v20 (Monte Carlo vs Random) – Basic Rewards

**URL**: [https://benpierce.github.io/aispacewars/?replay=2](https://benpierce.github.io/aispacewars/?replay=2)
In this scenario the reward system is simply +1 for a team win, and -1 for a team loss. As you can see, there's very little hint of intelligence with the Monte Carlo team and they eventually lose against random agents. In order to rectify this, I added additional rewards and penalties to encourage 'good behavior', which eventually led to much stronger Monte Carlo agents.

## Game 4: 10v10 (Monte Carlo vs Random)

**URL**: [https://benpierce.github.io/aispacewars/?replay=3](https://benpierce.github.io/aispacewars/?replay=3)
When tuning the rewards system, I often used 10v10 simulations to quickly see how well the Monte Carlo team performed. In this simulation, the Human ships do a good job at avoiding collisions early on; however, friendly fire is still a problem. At the end of the game, one of the Human agents determines that it will receive a larger reward for the overall win, despite the negative reward penalty for a kamikaze.

## Game 5: 1v1 (Monte Carlo vs Random)

**URL**: [https://benpierce.github.io/aispacewars/?replay=4](https://benpierce.github.io/aispacewars/?replay=4)

I used many 1v1 scenarios to test the Monte Carlo AI to see how effective individual agents were. In this simulation, you can see that the Monte Carlo ship quickly wins against the random ship, by determining that a well-aimed missile strike is the statistically optimal move.

## Game 6: 3v3 (Monte Carlo vs Random)

**URL**: [https://benpierce.github.io/aispacewars/?replay=5](https://benpierce.github.io/aispacewars/?replay=5)

Another smaller simulation I used to test the Monte Carlo Tree Search. In this simulation, the negative reward for a Kamikaze was too significant, so you can observe the Human ships flying as far away as possible from the Alien ships.

## Game 7: 20v20 (Monte Carlo vs Monte Carlo)

**URL**: [https://benpierce.github.io/aispacewars/?replay=6](https://benpierce.github.io/aispacewars/?replay=6)

This 20v20 simulation with both teams equipped with Monte Carlo Tree Search agents is probably my favourite. Both sides are evenly matched and in the final seconds of the simulation, one of the Human agents calculates that the best move is self-sacrifice for the narrow win.

## Game 8: 5v5 (Monte Carlo vs Monte Carlo)

**URL**: [https://benpierce.github.io/aispacewars/?replay=7](https://benpierce.github.io/aispacewars/?replay=7)

In this 5v5 simulation, both teams are equipped with Monte Carlo Tree Search agents and the short battle is quite entertaining, with both sides making fairly accurate shots against each other.

## A Note about the Viewer

All simulations were created in Python and, due to the average number of rollouts per simulation (up to 12 million for 40 agents), could take hours to generate. The Python simulation would produce a JSON file that described the game state at each "world tick", with 5 ticks representing 1 second of simulation time. The viewer [https://benpierce.github.io/aispacewars/](https://benpierce.github.io/aispacewars/) itself is simply a JavaScript page that was programmed to be able to replay these JSON files. Because world ticks are an abstract concept in the simulation, fast-forward, slow-motion, and pause were extremely easy to implement in the viewer simply by changing the number of world ticks per second. Slow-motion and pause, especially, were both critical in being able to visually debug problems with the physics or with agent AI. 

**Important**: The viewer was tested in Chrome and may not work on other browsers.

# Conclusion

While the Monte Carlo Tree Search algorithm is an easy and effective way to create a successful agent,  having it perform well in a multi-agent environment consisting of a huge action-state space presents significant challenges, including management of large branching factors, simulation performance, reward system optimization, exploration vs exploitation, and team strategy & cooperation. 

Many of these challenges can be addressed through performance tuning, hyperparameter tuning, and approximation; however, a cohesive team strategy would likely require one or more higher-level planning algorithms which would then govern lower-level, agent-specific, behavior. 

In lieu of these higher-level, team-specific algorithms, careful tuning of the individual agent reward system must be undertaken to approximate a good team strategy by ensuring agents avoid taking selfish actions that have a negative effect on their teammates, such as friendly fire.  
