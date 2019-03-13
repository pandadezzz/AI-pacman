# AI-pacman

## SuperiorAStarAgent:
AStar is effective to allow pacman to have a longer and less random path to reach pellets on other side of the map without needing ghost to give it a push as seen from other methods. The downside is that it is not effective in calculating non-deterministic nature of the ghosts. However, with some simple modification, it works surprisingly well given the default map.
### 1. Start off by generating path of AStar which is a list of actions that leads to best fscore which comprises of:
gScore = action leading to state from beginning
hScore = number of pellets consumed

Attempt as using state.getScore() did not yield good result.
In choosing next path to visit, if it’s going back there is 70% chance this proposal is rejected.

### 2. Every iteration, pick the next action from the list of actions generated prior unless the following:
a. Next action will get pacman killed
b. Out of list of actions
c. There are many nearby ghosts
In which case, generate AStar again

### 3. To prevent pacman getting stuck and looping. go_backchance is set to 0% until we unstuck pacman.
Benefit:
• Easy to implement
• Very fast performance as lazy evaluation.
• Rarely get stuck when surrounding is void of pellets as initial Astar path help create efficient route to all pellets
• Majority win 99%
Disadvantage:
• Ghosts can corner pacman
• May not work well in large map?
• Power pellets not taken into account
To improve:
• Take into account power pellets
• Forward model of ghost movement
