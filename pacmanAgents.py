# pacmanAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

#jc8121
#version 2.1

from pacman import Directions
from game import Agent
import random
#import numpy as np # unable to use numpy?? throws error
import math
#from heuristics import *

class World():
	#just a class used to store world conditions

	def __init__(self, state):
		# world is the instance from getFood() function. 
		self.startWorldMat = self.getWorldMatrix(state.getFood())
		self.start_state = state

	def getWorldMatrix(self,world_instance):
		# world is the instance from getFood() function. 
		i =0
		world = []
		try:
			# we don't know the size so need to use exceptions to build the world to matrix
			while 1:
				temp = world_instance[i]
				world.append(temp)
				i+=1
		except:
			return world

	def countPellets(self):
		pellet_count =0
		for row in self.startWorldMat:
			pellet_count+=row.count(True) # True is pellets
		return pellet_count

	def getDisTravelled(self,state):
		# return manhathan distance between start state and this state
		startloc = self.start_state.getPacmanPosition()
		currentloc = state.getPacmanPosition()
		return abs(startloc[0]-currentloc[0])+abs(startloc[1]-currentloc[1])

	def getSurroundingPellets(self,location, world_mat):
		#given location of pacman we want to see number of surrounding pellets
		#location is xy, 
		None

class CompetitionAgent(Agent):
	#SuperiorAStarAgent
	# a superior version to HW which tackles:
	# - pacman getting stuck in back and forth movement
	# - pacman getting stuck in local area with no nearby pellets - by forcing no backward movement is very effective. reset after unstuck
	# - pacman getting ambushed by ghosts
	# - fast perforamnce due to laxy evaluation
	# - efficient path planning?
	# - winning the game 99%

	#version which avoids ghost
	go_backchance=0.3

	visited = [] # storing visited states
	nextToVisit =[] #stores the state we should visit next. excluding previous state
	winningState = None #storing the winning state
	startState= None
	bestMoves =None
	moveIndex=0 
	finalStateScore=0

	count =0
	# Initialization Function: Called one time when the game starts
	def registerInitialState(self, state):
		self.generateAStarRoute(state) # generate A-star route
		return

	def resetStat(self):
		self.visited = [] # storing visited states
		self.nextToVisit =[] #stores the state we should visit next. excluding previous state
		self.winningState = None #storing the winning state
		self.startState= None
		self.bestMoves =None
		self.moveIndex=0

	def generateAStarRoute(self, state):
		print 'generate new route'
		self.resetStat()
		self.startState=state # starting state
		self.start_world = World(state)
		self.start_score = self.start_world.countPellets() # starting world pellets
		self.nextToVisit.append((state,[],self.start_score))

		#find max
		self.findWinState()
		if self.winningState is None:
			#winningState is not found. just find lowest fScore
			self.visited.sort(key=lambda x: x[2])#,len(x[1])))
			self.bestMoves= self.visited[0]
			self.bestMoves = self.bestMoves[1]
		else:
			#there is winning state
			self.bestMoves = self.winningState[1]
		return

	def goingBack(self,action,prevActions):
		#function to check if new direction will go back which is not what we want?
		#without this function, we reach far less optimal state? As more generatePacmanSuccessor calls are needed

		# if dont' want to use this function uncomment below:
		#return False

		if not prevActions:
			return False
		prevAction = prevActions[len(prevActions)-1]
		if (action == "West" and prevAction == "East") or (action == "East" and prevAction == "West") or (action == "North" and prevAction == "South") or (action == "South" and prevAction == "North"):
			# the next action is going back to previous location
			# let's give it some random chane to go back or not
			if random.random()>=self.go_backchance:
				return True
			else:
				return False 
		return False

	def findWinState(self):
		#go through all state to find the winning state
		while self.nextToVisit:

			#pop off the start as we are analysing it now
			nextState,prevActions,score = self.nextToVisit.pop(0)
			
			# we visited this state, so record it
			self.visited.append((nextState,prevActions,score))

			gscore = len(prevActions) +1 #  moves it took to get to here. adding 1 because it take 1 more move to get to next state
			gScore= 0 # setting it to 0 will give much better result here. 

			#get possible actions for this state
			for action in nextState.getLegalPacmanActions():

				if not self.goingBack(action,prevActions):
					possibleState = nextState.generatePacmanSuccessor(action)
					self.count+=1

					if possibleState is None:	
						# we ran out of calls
						# isWin state not found
						return;
					current_world  = World(possibleState)
					current_pellets = current_world.countPellets()
					hScore=self.start_score-current_pellets
					fScore = -hScore+gScore
					
					if possibleState.isWin():
						# we found the winningState, can exit
						newaction = list(prevActions)
						newaction.append(action)
						self.winningState=((possibleState,newaction,fScore))
						return;

					if not possibleState.isLose():
						#add to next to visit 
						newaction = list(prevActions)
						newaction.append(action)
						#self.finalStateScore=possibleState.getScore() # no longer used?
						self.nextToVisit.append((possibleState,newaction,fScore))

			#sort based on FScore which is at position 2
			self.nextToVisit.sort(key=lambda x: x[2])
				
		return;

	# GetAction Function: Called with every frame

	def getclosestGhost(self,state):
		#get average distance to cloests ghost
		ghosts = state.getGhostPositions()
		pacman = state.getPacmanPosition()

		distances =[]
		sum = 0
		for ghost in ghosts:
			dis = abs(pacman[0]-ghost[0])+abs(pacman[1]-ghost[1])
			sum+=dis
			distances.append(dis)

		averageDis = sum/len(distances)
		return averageDis

	def getAction(self, state):
		# we are looking for the state.isWin() == true		
		#check if there is danger
		#legalAction = state.getLegalPacmanActions()


		action = 'STOP'
		if self.moveIndex<len(self.bestMoves):
			action = self.bestMoves[self.moveIndex]
			self.moveIndex+=1

		averageGhostDis = self.getclosestGhost(state)
		if averageGhostDis<=3:
			#danger! many ghost nearby. high chance of ambush-- seek new path
			print 'danger!'
			self.generateAStarRoute(state)
			if self.moveIndex<len(self.bestMoves):
				action = self.bestMoves[self.moveIndex]
				self.moveIndex+=1

		possibleState= state.generatePacmanSuccessor(action)

		if possibleState is not None and possibleState.isLose():
			#the next move will kill pacman! avoid by recalculating Astar!
			self.generateAStarRoute(state)
			#print self.finalStateScore
			if self.moveIndex<len(self.bestMoves):
				action = self.bestMoves[self.moveIndex]
				self.moveIndex+=1

		if action == 'STOP':
			# the action list ran out. generate new path again
			print 'out of path'
			self.go_backchance=0 # to avoid getting stuck. force don't go back
			self.generateAStarRoute(state)
			if len(self.bestMoves)>1:
				# unstuck so reset
				print 'unstuck reset go_backchance'
				self.go_backchance=0.3
			#print self.bestMoves
			if self.moveIndex<len(self.bestMoves):
				action = self.bestMoves[self.moveIndex]
				self.moveIndex+=1


		return action

'''
testing purpose from below. not used for final submission but just idea that
- only generate new route if there is a better route than current route
- so far it yields worse result than previous version
- also testd MCTS with better heustric but Astar is superior so far
'''

class SuperiorAStarAgent3(Agent):
	#version that does not advoid ghosts
	#depreciated version

	visited = [] # storing visited states
	nextToVisit =[] #stores the state we should visit next. excluding previous state
	winningState = None #storing the winning state
	startState= None
	bestMoves =None
	moveIndex=0 
	finalStateScore=0

	count =0
	# Initialization Function: Called one time when the game starts
	def registerInitialState(self, state):
		self.generateAStarRoute(state)
		return

	def resetStat(self):
		self.visited = [] # storing visited states
		self.nextToVisit =[] #stores the state we should visit next. excluding previous state
		self.winningState = None #storing the winning state
		self.startState= None
		self.bestMoves =None
		self.moveIndex=0

	def generateAStarRoute(self, state):
		print 'generate new route'
		self.resetStat()
		self.startState=state # starting state
		self.start_world = World(state)
		self.start_score = self.start_world.countPellets() # starting world pellets
		self.nextToVisit.append((state,[],self.start_score))

		#find max
		self.findWinState()
		if self.winningState is None:
			#winningState is not found. just find lowest fScore
			self.visited.sort(key=lambda x: x[2])#,len(x[1])))
			self.bestMoves= self.visited[0]
			self.bestMoves = self.bestMoves[1]
		else:
			#there is winning state
			self.bestMoves = self.winningState[1]
		return

	def goingBack(self,action,prevActions):
		#function to check if new direction will go back which is not what we want?
		#without this function, we reach far less optimal state? As more generatePacmanSuccessor calls are needed

		# if dont' want to use this function uncomment below:
		#return False

		if not prevActions:
			return False
		prevAction = prevActions[len(prevActions)-1]
		if (action == "West" and prevAction == "East") or (action == "East" and prevAction == "West") or (action == "North" and prevAction == "South") or (action == "South" and prevAction == "North"):
			# the next action is going back to previous location
			# let's give it some random to go back or not
			#return True
			if random.random()>=0.3:
				return True
			else:
				return False 
		return False

	def findWinState(self):
		#go through all state to find the winning state
		while self.nextToVisit:

			#pop off the start as we are analysing it now
			nextState,prevActions,score = self.nextToVisit.pop(0)
			
			# we visited this state, so record it
			self.visited.append((nextState,prevActions,score))

			gscore = len(prevActions) +1 #  moves it took to get to here. adding 1 because it take 1 more move to get to next state
			gScore= 0 # setting it to 0 will give much better result here. 

			#get possible actions for this state
			for action in nextState.getLegalPacmanActions():

				if not self.goingBack(action,prevActions):
					possibleState = nextState.generatePacmanSuccessor(action)
					self.count+=1

					if possibleState is None:	
						# we ran out of calls
						# isWin state not found
						return;
					current_world  = World(possibleState)
					current_pellets = current_world.countPellets()
					hScore=self.start_score-current_pellets
					fScore = -hScore+gScore
					
					if possibleState.isWin():
						# we found the winningState, can exit
						newaction = list(prevActions)
						newaction.append(action)
						self.winningState=((possibleState,newaction,fScore))
						return;

					if not possibleState.isLose():
						#add to next to visit 
						newaction = list(prevActions)
						newaction.append(action)
						self.finalStateScore=possibleState.getScore()
						self.nextToVisit.append((possibleState,newaction,fScore))

			#sort based on FScore which is at position 2
			self.nextToVisit.sort(key=lambda x: x[2])
				
		return;

	# GetAction Function: Called with every frame
	def getAction(self, state):
		# we are looking for the state.isWin() == true		
		#check if there is danger
		legalAction = state.getLegalPacmanActions()


		action = 'STOP'
		if self.moveIndex<len(self.bestMoves):
			action = self.bestMoves[self.moveIndex]
			self.moveIndex+=1


		possibleState= state.generatePacmanSuccessor(action)
		if possibleState is not None and possibleState.isLose():
			#the next move will kill pacman! avoid by recalculating Astar!
			self.generateAStarRoute(state)
			print self.finalStateScore
			if self.moveIndex<len(self.bestMoves):
				action = self.bestMoves[self.moveIndex]
				self.moveIndex+=1
		if action == 'STOP':
			# the action list ran out. generate new path again
			print 'out of path'
			
			self.generateAStarRoute(state)
			print self.bestMoves
			if self.moveIndex<len(self.bestMoves):
				action = self.bestMoves[self.moveIndex]
				self.moveIndex+=1
		return action

def findAstarPath(state):

	visited = [] # storing visited states
	nextToVisit =[] #stores the state we should visit next. excluding previous state
	winningState = None #storing the winning state
	startState= state
	bestMoves =None
	finalStateScore=0

	def goingBack(action,prevActions):
		#function to check if new direction will go back which is not what we want?
		#without this function, we reach far less optimal state? As more generatePacmanSuccessor calls are needed

		# if dont' want to use this function uncomment below:
		#return False

		if not prevActions:
			return False
		prevAction = prevActions[len(prevActions)-1]
		if (action == "West" and prevAction == "East") or (action == "East" and prevAction == "West") or (action == "North" and prevAction == "South") or (action == "South" and prevAction == "North"):
			# the next action is going back to previous location
			# let's give it some random to go back or not
			return True
			if random.random()>=0.3:
				return True
			else:
				return False 
		return False

	start_world = World(state)
	start_score = start_world.countPellets() # starting world pellets
	nextToVisit.append((state,[],start_score))

	#find max
	while nextToVisit:
		#pop off the start as we are analysing it now
		nextState,prevActions,score = nextToVisit.pop(0)
		
		# we visited this state, so record it
		visited.append((nextState,prevActions,score))

		#NOTE: there are 2 implementations. with gscore on, the pacman will get suck as next move is same score as previous. 
		#next state h will decrease by 1 g will increment by 1. so will not change f score
		
		#Comment unwanted one out
		gscore = len(prevActions) +1 #  moves it took to get to here. adding 1 because it take 1 more move to get to next state
		gScore= 0 # setting it to 0 will give much better result here. 

		#get possible actions for this state
		for action in nextState.getLegalPacmanActions():

			if not goingBack(action,prevActions):
				possibleState = nextState.generatePacmanSuccessor(action)

				if possibleState is None:	
					# we ran out of calls
					# isWin state not found
					break;
				current_world  = World(possibleState)
				current_pellets = current_world.countPellets()
				hScore=start_score-current_pellets
				fScore = -hScore+gScore
				
				if possibleState.isWin():
					# we found the winningState, can exit
					newaction = list(prevActions)
					newaction.append(action)
					winningState=((possibleState,newaction,fScore))
					break;

				if not possibleState.isLose():
					#add to next to visit 
					newaction = list(prevActions)
					newaction.append(action)
					finalStateScore=hScore
					nextToVisit.append((possibleState,newaction,fScore))

		#sort based on FScore which is at position 2
		nextToVisit.sort(key=lambda x: x[2])

	#print finalStateScore


	if winningState is None:
		#winningState is not found. just find lowest fScore
		visited.sort(key=lambda x: x[2])#,len(x[1])))
		bestMoves= visited[0]
		bestMoves = bestMoves[1]
	else:
		#there is winning state
		bestMoves = winningState[1]
	finalStateScore=visited[0][2]
	return bestMoves,finalStateScore,visited


class SuperiorAStarAgent2(Agent):

	visited = [] # storing visited states
	nextToVisit =[] #stores the state we should visit next. excluding previous state
	winningState = None #storing the winning state
	startState= None
	bestMoves =None
	moveIndex=0 
	finalStateScore=0

	count =0
	# Initialization Function: Called one time when the game starts
	def registerInitialState(self, state):
		
		self.generateAStarRoute(state)
		return

	def resetStat(self):
		self.visited = [] # storing visited states
		self.nextToVisit =[] #stores the state we should visit next. excluding previous state
		self.winningState = None #storing the winning state
		self.startState= None
		self.bestMoves =None
		self.moveIndex=0

	def generateAStarRoute(self, state):
		#print 'generate new route'
		
		self.startState=state # starting state
		self.start_world = World(state)
		self.start_score = self.start_world.countPellets() # starting world pellets
		self.nextToVisit.append((state,[],self.start_score))

		#find max
		self.findWinState()
		if self.winningState is None:
			#winningState is not found. just find lowest fScore
			self.visited.sort(key=lambda x: x[2])#,len(x[1])))
			self.bestMoves= self.visited[0]
			self.bestMoves = self.bestMoves[1]
		else:
			#there is winning state
			self.bestMoves = self.winningState[1]
		return

	def goingBack(self,action,prevActions):
		#function to check if new direction will go back which is not what we want?
		#without this function, we reach far less optimal state? As more generatePacmanSuccessor calls are needed

		# if dont' want to use this function uncomment below:
		#return False

		if not prevActions:
			return False
		prevAction = prevActions[len(prevActions)-1]
		if (action == "West" and prevAction == "East") or (action == "East" and prevAction == "West") or (action == "North" and prevAction == "South") or (action == "South" and prevAction == "North"):
			# the next action is going back to previous location
			# let's give it some random to go back or not
			#return True
			if random.random()>=0.3:
				return True
			else:
				return False 
		return False

	def findWinState(self):
		#go through all state to find the winning state
		while self.nextToVisit:

			#pop off the start as we are analysing it now
			nextState,prevActions,score = self.nextToVisit.pop(0)
			
			# we visited this state, so record it
			self.visited.append((nextState,prevActions,score))

			#NOTE: there are 2 implementations. with gscore on, the pacman will get suck as next move is same score as previous. 
			#next state h will decrease by 1 g will increment by 1. so will not change f score
			
			#Comment unwanted one out
			gscore = len(prevActions) +1 #  moves it took to get to here. adding 1 because it take 1 more move to get to next state
			gScore= 0 # setting it to 0 will give much better result here. 

			#get possible actions for this state
			for action in nextState.getLegalPacmanActions():

				if not self.goingBack(action,prevActions):
					possibleState = nextState.generatePacmanSuccessor(action)
					self.count+=1

					if possibleState is None:	
						# we ran out of calls
						# isWin state not found
						return;
					current_world  = World(possibleState)
					current_pellets = current_world.countPellets()
					hScore=self.start_score-current_pellets
					fScore = -hScore+gScore
					
					if possibleState.isWin():
						# we found the winningState, can exit
						newaction = list(prevActions)
						newaction.append(action)
						self.winningState=((possibleState,newaction,fScore))
						return;

					if not possibleState.isLose():
						#add to next to visit 
						newaction = list(prevActions)
						newaction.append(action)
						#self.finalStateScore=hScore
						self.nextToVisit.append((possibleState,newaction,fScore))

			#sort based on FScore which is at position 2
			self.nextToVisit.sort(key=lambda x: x[2])
				
		return;

	# GetAction Function: Called with every frame
	def getAction(self, state):
		# we are looking for the state.isWin() == true		
		#check if there is danger
		legalAction = state.getLegalPacmanActions()
		#print self.visited[0]
		self.finalStateScore=self.visited[0][2]

		tempMoves, score,visited = findAstarPath(state)
		#check if there is a better path
		#score>self.finalStateScore
		if score>self.finalStateScore:
			#there is better path
			print 'found better route:  ',score,self.finalStateScore
			self.resetStat()
			self.bestMoves=tempMoves
			self.finalStateScore=score
			self.visited=visited


		action = 'STOP' #default
		if self.moveIndex<len(self.bestMoves):
			action = self.bestMoves[self.moveIndex]
			self.moveIndex+=1

		possibleState= state.generatePacmanSuccessor(action)
		if possibleState is not None and possibleState.isLose():
			#the next move will kill pacman! avoid by recalculating Astar!
			self.resetStat()
			self.generateAStarRoute(state)
			#print self.finalStateScore
			if self.moveIndex<len(self.bestMoves):
				action = self.bestMoves[self.moveIndex]
				self.moveIndex+=1
		return action

