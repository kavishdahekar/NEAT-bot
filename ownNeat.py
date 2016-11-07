import math
import random
import os

# *****************************************************************
#	Synapse
# *****************************************************************
class Synapse(object):
	def __init__(self):
		self.inpuT = 0
		self.output = 0
		self.weight = 0.0
		self.enabled = True
		self.innovation = 0

	def clone(self):
		synapse = Synapse()
		synapse.inpuT = self.inpuT
		synapse.output = self.output
		synapse.weight = self.weight
		synapse.enabled = self.enabled
		synapse.innovation = self.innovation
		return synapse
	
	def printSynapse(self):
		print("input:", self.inpuT)
		print("output:", self.output)
		print("weight:", self.weight)
		print("enabled:", self.enabled)
		print("innvation:", self.innovation)

# *****************************************************************
#	Neuron
# *****************************************************************

class Neuron(object):
	def __init__(self):
		self.value = 0.0
		self.inputs = []
		
	@staticmethod
	def sigmoid(x):
		# try:
		# 	ret = 2.0 / (1.0 + math.exp(-4.9 * x)) - 1.0
		# except OverflowError:
		# 	print(x)
		ret = 0
		try:
			if x >= 709:
				x = 709
			ret = 2.0 / (1.0 + math.exp(-4.9 * x)) - 1.0
		except OverflowError:
			# print(x)
			pass
		return ret
	
	def printNeuron(self):
		print("value:", self.value)
		if len(self.inputs) == 0:
			print("no synapse in the input list")
		else:
			print("INPUT LIST")
			for synapse in self.inputs:
				print("SYNAPSE:")
				synapse.printSynapse()
		print()

# *****************************************************************
#	Species
# *****************************************************************

class Species(object):
	CROSSOVER = 0.75
	
	def __init__(self):
		self.genomes = []#ArrayList[Genome]()
		self.topFitness = 0.0
		self.averageFitness = 0.0
		self.staleness = 0
		
	def printSpecies(self):
		print("topFitness:", self.topFitness)
		print("averageFitness:", self.averageFitness)
		print("staleness:", self.staleness)
		if len(self.genomes) == 0:
			print("no genome in the genome list")
		else:
			print("GENOME LIST")
			for genome in self.genomes:
				print("GENOME:")
				#genome.printGenome()
				print(genome)
		print()
	
	def breedChild(self):
		if random.random() < Species.CROSSOVER:
			g1 = self.genomes[random.randint(0, len(self.genomes)-1)]
			g2 = self.genomes[random.randint(0, len(self.genomes)-1)]
			child = self.crossover(g1, g2)
		else:
			child = self.genomes[random.randint(0, len(self.genomes)-1)].clone()
		child.mutate()
		return child
	
	def calculateAverageFitness(self):
		total = 0.0
		for genome in self.genomes:
			total += genome.globalRank
		self.averageFitness = total / len(self.genomes)
		
	def crossover(self, g1, g2):
		if g2.fitness > g1.fitness:
			#######################################
			g1, g2 = g2, g1
			
		child = Genome()
		
		#while(1):
		##########################################################
		for gene1 in g1.genes:
			for gene2 in g2.genes:
				#if gotoOuterLoopFlag == True:
				#	break
					
				if gene1.innovation == gene2.innovation:
					if random.choice([True, False]) and gene2.enabled:
						child.genes.append(gene2.clone())
						#break
						#gotoOuterLoopFlag = True
						break
					else:
						break
			child.genes.append(gene1.clone())
		##########################################################		
		
		child.maxNeuron = max(g1.maxNeuron, g2.maxNeuron)

		for i in range(7):
			child.mutationRates[i] = g1.mutationRates[i]
		
		return child

# *****************************************************************
#	Pool
# *****************************************************************
class Pool(object):
	POPULATION	= 50
	STALE_SPECIES = 15
	INPUTS		= 4
	OUTPUTS	   = 1
	TIMEOUT	   = 20

	DELTA_DISJOINT  = 2.0
	DELTA_WEIGHTS   = 0.4
	DELTA_THRESHOLD = 1.0

	CONN_MUTATION	= 0.25
	LINK_MUTATION	= 2.0
	BIAS_MUTATION	= 0.4
	NODE_MUTATION	= 0.5
	ENABLE_MUTATION  = 0.2
	DISABLE_MUTATION = 0.4
	STEP_SIZE		= 0.1
	PERTURBATION	 = 0.9
	CROSSOVER		= 0.75

	#public static final Random rnd = new Random();

	#public static final List<Species> species	= new ArrayList<>();
	species = []
	generation = 0
	innovation = OUTPUTS
	maxFitness = 0.0
	
	@staticmethod
	def addToSpecies(child):
		for species in Pool.species:
			if child.sameSpecies(species.genomes[0]):
				species.genomes.append(child)
				return

		childSpecies = Species()
		childSpecies.genomes.append(child)
		Pool.species.append(childSpecies)
	
		
	@staticmethod
	def cullSpecies(cutToOne):
		for species in Pool.species:
			def getKey(custom):
				return custom.fitness

			species.genomes = sorted(species.genomes, key=getKey, reverse=True)
			##########################################################
			#species.genomes = sorted(species.genomes)
			##########################################################

			remaining = math.ceil(len(species.genomes) / 2.0)
			if cutToOne:
				remaining = 1.0

			while len(species.genomes) > remaining:
				species.genomes.pop()
				
	@staticmethod
	def initializePool():
		for i in range(Pool.POPULATION):
			basic = Genome()
			basic.maxNeuron = Pool.INPUTS
			basic.mutate()
			#basic.printGenome()
			Pool.addToSpecies(basic)

	@staticmethod
	def newGeneration():
		Pool.cullSpecies(False)
		Pool.rankGlobally()
		Pool.removeStaleSpecies()
		Pool.rankGlobally()
		
		for species in Pool.species:
			species.calculateAverageFitness()
		
		Pool.removeWeakSpecies()
		sumF = Pool.totalAverageFitness()
		#children = new ArrayList<Genome>();
		children= []

		for species in Pool.species:
			breed = math.floor(species.averageFitness / sumF * Pool.POPULATION) - 1.0
			for i in range(int(breed)):
				children.append(species.breedChild())
				
		Pool.cullSpecies(True)
		
		while len(children) + len(Pool.species) < Pool.POPULATION:
			species = Pool.species[random.randint(0, len(Pool.species)-1)]
			children.append(species.breedChild())
		
		for child in children:
			Pool.addToSpecies(child)
		
		Pool.generation += 1
	
	@staticmethod
	def rankGlobally():
		#final List<Genome> global = new ArrayList<Genome>();
		globalGenomes = []
		for species in Pool.species:
			for genome in species.genomes:
				globalGenomes.append(genome)
		
		def getKey(custom):
				return custom.fitness

		globalGenomes = sorted(globalGenomes, key=getKey, reverse=False)
		##########################################################
		#globalGenomes = sorted(globalGenomes)
		##########################################################

		for i in range(len(globalGenomes)):
			globalGenomes[i].globalRank = i
			
	@staticmethod
	def removeStaleSpecies():
		#final List<Species> survived = new ArrayList<Species>();
		survived = []
		for species in Pool.species:
			def getKey(custom):
				return custom.fitness

			species.genomes = sorted(species.genomes, key=getKey, reverse=True)
			##########################################################
			#species.genomes = sorted(species.genomes, key=compare)
			##########################################################

			if species.genomes[0].fitness > species.topFitness:
				species.topFitness = species.genomes[0].fitness
				species.staleness = 0
			else:
				species.staleness += 1

			if species.staleness < Pool.STALE_SPECIES or species.topFitness >= maxFitness:
				survived.append(species)

		Pool.species.clear()
		Pool.species.extend(survived)

	@staticmethod
	def removeWeakSpecies():
		#final List<Species> survived = new ArrayList<Species>();
		survived = []
		sumF = Pool.totalAverageFitness()
		for species in Pool.species:
			breed = math.floor(species.averageFitness / sumF * Pool.POPULATION)
			if breed >= 1.0:
				survived.append(species)

		Pool.species.clear()
		Pool.species.extend(survived)
	
	@staticmethod
	def totalAverageFitness():
		total = 0
		for species in Pool.species:
			total += species.averageFitness
		return total

# *****************************************************************
#	Genome
# *****************************************************************
class Genome(object):
	def __init__(self):
		self.genes = []#ArrayList[Synapses]()
		self.fitness = 0.0
		self.maxNeuron = 0
		self.globalRank = 0
		self.mutationRates = [Pool.CONN_MUTATION, Pool.LINK_MUTATION, Pool.BIAS_MUTATION, \
						 Pool.NODE_MUTATION, Pool.ENABLE_MUTATION, Pool.DISABLE_MUTATION, Pool.STEP_SIZE]
		self.network = {}#Map<Integer, Neuron> network
		
	def printGenome(self):
		print("genes: ", self.genes)
		print("fitness: ", self.fitness)
		print("maxNeuron: ", self.maxNeuron)
		print("globalRank: ", self.globalRank)
		
		print("mutationRates: ", self.mutationRates)
		print("network: ",self.network)
		print()
	  
	def clone(self):
		genome = Genome()
		for gene in self.genes:
			genome.genes.append(gene.clone())
			
		genome.maxNeuron = self.maxNeuron
		for i in range(7):
			genome.mutationRates[i] = self.mutationRates[i]
		return genome

	def containsLink(self, link):
		for gene in self.genes:
			if gene.inpuT == link.inpuT and gene.output == link.output:
				return True
		return False
	
	def disjoint(self, genome):
		disjointGenes = 0.0
		for gene in self.genes:
			for otherGene in genome.genes:
				if gene.innovation == otherGene.innovation:
					break	
			disjointGenes += 1.0
			
		return disjointGenes / max(len(self.genes), len(genome.genes))

	def evaluateNetwork(self, inpuTT):
		for i in range(Pool.INPUTS):
			self.network[i].value = inpuTT[i]

		for key, val in self.network.items():
			if (key < Pool.INPUTS + Pool.OUTPUTS):
				continue
										
			neuron = val
			sumWV = 0.0
			for incoming in neuron.inputs:
				other = self.network[incoming.inpuT]
				sumWV += incoming.weight * other.value
			
			if len(neuron.inputs) != 0:
				neuron.value = Neuron.sigmoid(sumWV)

		for key, val in self.network.items():
			if key < Pool.INPUTS or key >= Pool.INPUTS + Pool.OUTPUTS:
				continue
			
			neuron = val
			sumWV = 0.0
			for incoming in neuron.inputs:			  
				other = self.network[incoming.inpuT]
				sumWV += incoming.weight * other.value
	
			if len(neuron.inputs) != 0:
				neuron.value = Neuron.sigmoid(sumWV)
					
		output = []
		for i in range(Pool.OUTPUTS):
			output.append(self.network[Pool.INPUTS + i].value)
										
		return output
	
	def generateNetwork(self):
		self.network = {}
		
		for i in range(Pool.INPUTS):
			self.network[i] = Neuron()
		
		for i in range(Pool.OUTPUTS):
			self.network[Pool.INPUTS + i] = Neuron()
		
		def getKey(custom):
			return custom.output
		
		self.genes = sorted(self.genes, key=getKey)
		
		for gene in self.genes:
			if gene.enabled:
				if gene.output not in self.network.keys():
					self.network[gene.output] = Neuron()
				neuron = self.network[gene.output]
				neuron.inputs.append(gene)
				if gene.inpuT not in self.network.keys():
					self.network[gene.inpuT] = Neuron()
	
	def mutate(self):
		for i in range(7):
			if random.choice([True, False]):
				self.mutationRates[i] *= 0.95 
			else:
				self.mutationRates[i] *= 1.05263

				
		if random.uniform(0,1) < self.mutationRates[0]:
			self.mutatePoint()

		prob = self.mutationRates[1]
		while (prob > 0):
			if random.uniform(0,1) < prob:
				self.mutateLink(False)
			prob -= 1

		prob = self.mutationRates[2]
		while (prob > 0):
			if random.uniform(0,1) < prob:
				self.mutateLink(True);
			prob -= 1

		prob = self.mutationRates[3]
		while (prob > 0):
			if random.uniform(0,1) < prob:
				self.mutateNode()
			prob -= 1

		prob = self.mutationRates[4]
		while (prob > 0):
			if random.uniform(0,1) < prob:
				self.mutateEnableDisable(True)
			prob -= 1

		prob = self.mutationRates[5]
		while (prob > 0):
			if random.uniform(0,1) < prob:
				self.mutateEnableDisable(False)
			prob -= 1
		
	def mutateEnableDisable(self, enable): 
		candidates = []
		for gene in self.genes:
			if gene.enabled != enable:
				candidates.append(gene)

		if len(candidates) == 0:
			return

		gene = candidates[random.randint(0, len(candidates)-1)]
		gene.enabled = not gene.enabled
	
	def mutateLink(self, forceBias):
		neuron1 = self.randomNeuron(False, True)
		neuron2 = self.randomNeuron(True, False)

		newLink = Synapse()
		newLink.inpuT = neuron1
		newLink.output = neuron2

		if forceBias:
			newLink.inpuT = Pool.INPUTS - 1;

		if self.containsLink(newLink):
			return
	
		Pool.innovation += 1
		newLink.innovation = Pool.innovation
		newLink.weight = random.uniform(0,1) * 4.0 - 2.0

		self.genes.append(newLink)

	def mutateNode(self):
		if len(self.genes) == 0:
			return

		gene = self.genes[random.randint(0, len(self.genes)-1)]
		if not gene.enabled:
			return
		gene.enabled = False

		self.maxNeuron += 1

		gene1 = gene.clone()
		gene1.output = self.maxNeuron
		gene1.weight = 1.0
		
		Pool.innovation += 1
		gene1.innovation = Pool.innovation
		
		gene1.enabled = True
		self.genes.append(gene1)

		gene2 = gene.clone()
		gene2.inpuT = self.maxNeuron
		
		Pool.innovation += 1
		gene2.innovation = Pool.innovation
		
		gene2.enabled = True
		self.genes.append(gene2)

	def mutatePoint(self):
		for gene in self.genes:
			if random.uniform(0,1) < Pool.PERTURBATION:
				gene.weight += random.uniform(0,1) * self.mutationRates[6] * 2.0 - self.mutationRates[6]
			else:
				gene.weight = random.uniform(0,1) * 4.0 - 2.0

	def randomNeuron(self, nonInput, nonOutput):
		#final List<Integer> neurons = new ArrayList<Integer>();
		neurons = []

		if not nonInput:
			for i in range(Pool.INPUTS):
				neurons.append(i)

		if not nonOutput:
			for i in range(Pool.OUTPUTS):
				neurons.append(Pool.INPUTS + i)

		for gene in self.genes:
			if (not nonInput or gene.inpuT >= Pool.INPUTS) and (not nonOutput or gene.inpuT >= Pool.INPUTS + Pool.OUTPUTS):
				neurons.append(gene.inpuT)
				
			if (not nonInput or gene.output >= Pool.INPUTS) and (not nonOutput or gene.output >= Pool.INPUTS + Pool.OUTPUTS):
				neurons.append(gene.output)
		return neurons[random.randint(0, len(neurons)-1)]

	
	def sameSpecies(self, genome):
		dd = Pool.DELTA_DISJOINT * self.disjoint(genome)
		dw = Pool.DELTA_WEIGHTS * self.weights(genome)
		return dd + dw < Pool.DELTA_THRESHOLD

	def weights(self, genome):
		sumW = 0.0
		coincident = 0.0
		for gene in self.genes:
			for otherGene in genome.genes:
				#print(gene, otherGene)
				if gene.innovation == otherGene.innovation:
					sumW += abs(gene.weight - otherGene.weight)
					coincident += 1.0
					#print(coincident)
					break
				#else:
				#	print(str(gene.innovation)+" : "+str(otherGene.innovation))
		if coincident == 0:
			return sumW
		return sumW / coincident


# *****************************************************************
#	FLAPPY BIRD
# *****************************************************************
import sys, pygame
import time
import random, math
from copy import deepcopy

pygame.init()

SCREEN_HEIGHT = 400
SCREEN_WIDTH = 600
WINDOW_X = 100
WINDOW_Y = 100

GRAVITY = 0.10
BIRD_JUMP_VEL = 1
JUMP_DURATION = 5

BIRD_HEIGHT = 30
BIRD_WIDTH = 75
BIRD_INI_POS_X = 200
BIRD_INI_POS_Y = 100

PIPE_WIDTH = 30
PIPE_GAP = 200
PIPE_GAP_WIDTH_FACTOR = 0.3
# FRAME_SLEEP_TIME = 0.009
FRAME_SLEEP_TIME = 0

# set window position
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (WINDOW_X,WINDOW_Y)

class Bird(object):

	BIRD_HEIGHT = 30
	BIRD_WIDTH = 35
	JUMP_DURATION = 5

	def __init__(self,pos_x,pos_y,genome):
		self.isAlive = True

		self.genome = genome

		self.birdImg = "img/0.jpg"
		self.spriteNo = 0

		tempBird = pygame.image.load(self.birdImg)
		self.drawBird = pygame.transform.scale(tempBird, (BIRD_WIDTH, BIRD_HEIGHT))
		self.rect = self.drawBird.get_rect()

		self.iniPosX = pos_x
		self.iniPosY = pos_y
		self.rect.y = pos_y
		self.rect.x = pos_x

		self.speed = [0, 0]

		self.isJumping = True
		self.jumpCounter = 0

		self.height = None
		self.nextPipeHeight = None
		self.nextPipeDist = None

		self.pipesCrossed = []
		self.score = 0
		self.fitness = 0
		self.flaps = 0

	def setSprite(self):
		self.spriteNo = self.spriteNo + 1
		self.spriteNo = self.spriteNo % 4
		self.birdImg = "img/"+str(self.spriteNo)+".jpg"
		tempBird = pygame.image.load(self.birdImg)
		self.drawBird = pygame.transform.scale(tempBird, (BIRD_WIDTH, BIRD_HEIGHT))
		# self.rect = self.drawBird.get_rect()

	def setRectSpeed(self, speed):
		self.rect = self.rect.move(speed)

	def checkJump(self):
		if self.isJumping:
			self.speed[1] = -(BIRD_JUMP_VEL*self.jumpCounter - 0.5 * GRAVITY * self.jumpCounter * self.jumpCounter)
			self.jumpCounter = self.jumpCounter + 1
		else:
			self.speed[1] += GRAVITY

		if self.jumpCounter == JUMP_DURATION:
			self.jumpCounter = 0
			self.isJumping = False
			self.flaps = self.flaps + 1

	def checkCollision(self,screen_height,pipes):
		# Bird fell below screen
		if self.rect.y > screen_height:
			self.isAlive = False
			return False
		# Brid touching ceiling
		if self.rect.y < 0:
			self.rect.y = 0

		for pipe in pipes:
			if pygame.Rect.colliderect(self.rect,pipe.topRect):
				self.isAlive = False
				return False
			if pygame.Rect.colliderect(self.rect,pipe.bottomRect):
				self.isAlive = False
				return False

	def hasCrossed(self,pipe_id):
		if pipe_id in self.pipesCrossed:
			return True
		else:
			return False

	def setInputs(self, pipes):
		self.height = None
		self.nextPipeHeight = None
		self.nextPipeDist = None

		# Inputs for neural network
		self.height = self.rect.y / SCREEN_HEIGHT
		for pipe in pipes:
			if pipe.bottomRect.x <= self.rect.x:
				continue
			else:
				self.nextPipeHeight = (SCREEN_HEIGHT - pipe.bottomRect.y) / SCREEN_HEIGHT
				self.nextPipeDist   = pipe.bottomRect.x / SCREEN_WIDTH
				break


class Pipe(object):

	def __init__(self,pos_x,pipeid):

		self.id = pipeid

		midpt = random.randint(math.floor(SCREEN_HEIGHT * 0.25) , math.floor(SCREEN_HEIGHT * 0.75))
		temp1 = midpt - BIRD_HEIGHT/PIPE_GAP_WIDTH_FACTOR
		temp2 = midpt + BIRD_HEIGHT/PIPE_GAP_WIDTH_FACTOR

		self.topRect    = pygame.Rect(pos_x,0,PIPE_WIDTH,temp1)
		self.bottomRect = pygame.Rect(pos_x,temp2,PIPE_WIDTH,SCREEN_HEIGHT - temp2)

		self.color = (0,0,255)
		self.speed = [-1.8 , 0]

	def setRectSpeed(self, speed):
		self.topRect.move_ip(speed)
		self.bottomRect.move_ip(speed)

	def drawPipe(self, screen):
		pygame.draw.rect(screen, self.color, self.topRect, 0)
		pygame.draw.rect(screen, self.color, self.bottomRect , 0)


def initializeGame():

	size = width, height = SCREEN_WIDTH, SCREEN_HEIGHT
	screen = pygame.display.set_mode(size)

	birds = []

	for species in Pool.species:
		for genome in species.genomes:
			genome.generateNetwork()
			birds.append(Bird(BIRD_INI_POS_X,BIRD_INI_POS_Y,genome))

	# Generate pipes
	pipes = []
	distance = SCREEN_WIDTH
	for i in range(0,5):
		pipes.append(Pipe(distance + PIPE_GAP* i, i))

	ticks = 0
	allDead = False

	while not allDead:

		# Event handling
		for event in pygame.event.get():
			if event.type == pygame.QUIT: sys.exit()

			# if event.type == pygame.KEYDOWN:
			# 	if event.key == pygame.K_SPACE:
			# 		birds[0].isJumping = True
			# 	if event.key == pygame.K_LEFTBRACKET:
			# 		birds[1].isJumping = True
		
		# color screen full shite
		screen.fill((255,255,255)) # White background

		for bird in birds:
			if bird.isAlive == True:
				
				# if bird.score >= 5:
				# 	# set sprite
				# 	bird.setSprite()

				# set bird speed
				bird.setRectSpeed(bird.speed)
				# check if bird is jumping
				bird.checkJump()
				# Draw bird on screen
				screen.blit(bird.drawBird, bird.rect)

		# draw pipes
		for pipe in pipes:
			pipe.setRectSpeed(pipe.speed)
			pipe.drawPipe(screen)

		for bird in birds:
			if bird.isAlive == True:
				# check collision of bird
				bird.checkCollision(screen.get_rect().height,pipes)
				# generate inputs from bird
				bird.setInputs(pipes)
		
		for bird in birds:
			if bird.isAlive == True:
				# Calculate score
				for pipe in pipes:
					if pipe.topRect.x <= bird.iniPosX and bird.hasCrossed(pipe.id) == False:
						bird.pipesCrossed.append(pipe.id)
						bird.score += 1

				# Calculate fitness
				bird.fitness = (ticks - 1.5 * bird.flaps)

		# Infinite pipes
		if pipes[0].topRect.x <= 0:
			pipes.remove(pipes[0])
			pipes.append(Pipe(pipes[len(pipes) - 1].topRect.x + PIPE_GAP, pipes[len(pipes) - 1].id + 1))

		
		# for bird in birds:
		# 	if bird.isAlive == True:
		# 		print("Score : ",bird.score, "Fitness : ", bird.fitness , "Flaps : " , bird.flaps)


		# NNet output
		for bird in birds:
			if bird.isAlive == True:
				output = bird.genome.evaluateNetwork([bird.height, bird.nextPipeHeight, bird.nextPipeDist, 1])
				if output[0] > 0.5:
					bird.isJumping = True

		pygame.display.flip()
		ticks = ticks + 1
		time.sleep(FRAME_SLEEP_TIME)

		aliveStatus = []
		for bird in birds:
			aliveStatus.append(bird.isAlive)

		if all(isAlive == False for isAlive in aliveStatus):
			allDead = True
		else:
			allDead = False

		# Calculate maximum fitness
		max_fitness = 0
		max_score = 0
		mortality = 0
		for bird in birds:
			if bird.fitness > max_fitness:
				max_fitness = bird.fitness
			if bird.score > max_score:
				max_score = bird.score
			if bird.score < 1:
				mortality += 1

	return [birds, max_fitness, max_score, mortality]


# First generation *****************************************
generation_no = 0
print("**************************************")
print("Generation  : ", generation_no)

Pool.initializePool()
op = initializeGame()
birds = op[0]
max_fitness = op[1]
max_score = op[2]
mortality = op[3]

print("Maximum Fitness : ",max_fitness)
print("Maximum Score : ",max_score)
print("Mortality : ",mortality)

for bird in birds:
	bird.genome.fitness = bird.fitness

	if bird.fitness > Pool.maxFitness:
		Pool.maxFitness = bird.fitness


# Repeat generations ****************************************
while 1:

	generation_no += 1
	print("**************************************")
	print("Generation  : ", generation_no)

	Pool.newGeneration()
	op = initializeGame()
	birds = op[0]
	max_fitness = op[1]
	max_score = op[2]
	mortality = op[3]

	print("Maximum Fitness : ",max_fitness)
	print("Maximum Score : ",max_score)
	print("Mortality : ",mortality)

	for bird in birds:
		bird.genome.fitness = bird.fitness

		if bird.fitness > Pool.maxFitness:
			Pool.maxFitness = bird.fitness