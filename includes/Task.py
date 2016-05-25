import math

class Task:

	def __init__(self, name) :
		self.name = name
		self.edges = []
		self.currentConfiguration = 1
		self.next = None

	# adds an edge to the
	def addEdge(self, edge) :
		self.edges.append(edge)

	# maximum number of configurations for this task
	# a configuration is a subset of all the edges that starts
	# from this task.
	def getMaxConfigurations(self) :
		return (math.pow(2, len(self.edges)) - 1)

	# gets the number of bits (edges) needed to represent the
	# configuration.
	def getNumberOfBits(self) :
		return len(self.edges)

	# returns a list of edges wrt the current configuration number.
	def getConfiguration(self) :
		configurationMask = list(bin(self.currentConfiguration)[2:].zfill(self.getNumberOfBits()))
		returnConfig = []
		i=0
		for edge in self.edges :
			if configurationMask[i]=='1' :
				returnConfig.append(edge)
			i=i+1
		return returnConfig

	# increments the configuration
	# returns true if configuration changed
	#         false if configuration not changed (max conf reached)
	def setNextConfiguration(self) :
		can = self.canIncrement()
		if can :
			self.currentConfiguration = self.currentConfiguration + 1
		return can


	# reset to configuration 1
	def resetConfiguration(self) :
		self.currentConfiguration = 1

	# tells if the
	def canIncrement(self) :
		return (self.currentConfiguration < self.getMaxConfigurations())

	# gets the first Task that can change in the Tasks linked list
	def getNextAvailable(self):
		if self.canIncrement():
			return self
		else:
			self.resetConfiguration()
			if self.next != None:
				return self.next.getNextAvailable()
			else:
				return None
