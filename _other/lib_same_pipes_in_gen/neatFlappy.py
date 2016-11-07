from __future__ import print_function

from neat import nn, population, statistics
# from neat import visualize

import sys, pygame
import time
import random, math
from copy import deepcopy

pygame.init()

fitness = None
generation_n = 0
# ********************* FLAPPY ********************************

def setBird(n,BIRD_HEIGHT,BIRD_WIDTH):
	birdimg = "b"+str(n)+".png"
	bird = pygame.image.load(birdimg)
	bird = pygame.transform.scale(bird, (BIRD_WIDTH, BIRD_HEIGHT))
	return bird

def generatePipeLocations(n, SCREEN_HEIGHT):
	f = open('pipes','w')
	for i in range(n):
		midpt = random.randint(math.floor(SCREEN_HEIGHT * 0.25) , math.floor(SCREEN_HEIGHT * 0.75))
		print(str(midpt), file=f)

def createPipe(dist, SCREEN_HEIGHT, BIRD_HEIGHT, PIPE_WIDTH, midpt):
	temp1 = midpt - BIRD_HEIGHT/0.3
	temp2 = midpt + BIRD_HEIGHT/0.3

	pipe_top = pygame.Rect(dist,0,PIPE_WIDTH,temp1)
	pipe_bottom = pygame.Rect(dist,temp2,PIPE_WIDTH,SCREEN_HEIGHT - temp2)

	return [pipe_top, pipe_bottom, False]

def runFlappy(net):
	JUMP_DURATION = 5
	SCREEN_HEIGHT = 400
	SCREEN_WIDTH = 600

	BIRD_HEIGHT = 30
	BIRD_WIDTH = 35
	BIRD_INI_POS_X = 200
	BIRD_INI_POS_Y = 100

	PIPE_WIDTH = 30
	PIPE_GAP = 200
	pipe_no = 0

	size = width, height = SCREEN_WIDTH, SCREEN_HEIGHT
	speed = [0, 0]
	pipeSpeed = [-1.8 , 0]
	black = 0, 0, 0
	white = 255, 255, 255
	green = (0,255,0)
	blue = (0,0,255)
	gravity = 0.10

	isJumping = True
	jumpDuration = JUMP_DURATION
	jumpCounter = 0
	jumpVel = 1
	 
	# Drawing bird from image sprite
	screen = pygame.display.set_mode(size)

	bird = None
	birdrect = None
	birdSprite = 1
	bird = setBird(birdSprite,BIRD_HEIGHT,BIRD_WIDTH)
	birdrect = bird.get_rect()
	birdrect.y = BIRD_INI_POS_Y
	birdrect.x = BIRD_INI_POS_X

	pipes = []
	dist = SCREEN_WIDTH
	pipe_locations = []
	load_profile = open('pipes', "r")
	read_it = load_profile.read()
	pipe_locations = [float(p) for p in read_it.splitlines()]

	for i in range(0,5):
		pipes.append(createPipe(dist + PIPE_GAP* i, SCREEN_HEIGHT,  BIRD_HEIGHT, PIPE_WIDTH, pipe_locations[pipe_no]))
		pipe_no += 1

	score = 0
	ticks = 0
	flaps = 0

	birdDead = False
	global fitness
	fitness = 0
	global generation_n

	while 1:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: sys.exit()

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					isJumping = True
					flaps = flaps + 1

		screen.fill(white)

		birdrect = birdrect.move(speed)


		if isJumping:
			speed[1] = -(jumpVel*jumpCounter - 0.5 * gravity * jumpCounter * jumpCounter)
			jumpCounter = jumpCounter + 1
		else:
			speed[1] += gravity

		if jumpCounter == jumpDuration:
			jumpCounter = 0
			isJumping = False

		screen.blit(bird, birdrect)
		birdSprite = (birdSprite + 1)%3
		bird = setBird(birdSprite,BIRD_HEIGHT,BIRD_WIDTH)

		for pipe in pipes:
			pipe[0].move_ip(pipeSpeed)
			pipe[1].move_ip(pipeSpeed)
			pygame.draw.rect(screen, green, pipe[0], 0)
			pygame.draw.rect(screen, green, pipe[1], 0)


		# Bird fell below screen
		if birdrect.y > screen.get_rect().height:
			print("\nBird out!")
			birdDead = True
		# Brid touching ceiling
		if birdrect.y < 0:
			birdrect.y = 0
			# print("\nBird out!")

		for pipe in pipes:
			if pygame.Rect.colliderect(birdrect,pipe[0]):
				print ("\nHit Pipe : Game Over")
				birdDead = True
			if pygame.Rect.colliderect(birdrect,pipe[1]):
				print ("\nHit Pipe : Game Over")
				birdDead = True

		# Inputs for neural network
		bird_height = birdrect.y / SCREEN_HEIGHT
		next_pipe_height = None
		next_pipe_distance = None
		for pipe in pipes:
			if pipe[1].x <= birdrect.x:
				continue
			else:
				next_pipe_height   = (SCREEN_HEIGHT - pipe[1].y) / SCREEN_HEIGHT
				next_pipe_distance = pipe[1].x / SCREEN_WIDTH
				break
		
		# Score
		for pipe in pipes:
			if pipe[0].x <= BIRD_INI_POS_X and pipe[2] == False:
				pipe[2] = True
				score = score + 1
				print("\nBH : ",bird_height, " PH : ",next_pipe_height, " PD : ",next_pipe_distance)

		# Infinite pipes
		if pipes[0][0].x <= 0:
			pipes.remove(pipes[0])
			pipes.append(createPipe(pipes[len(pipes) - 1][0].x + PIPE_GAP, SCREEN_HEIGHT, BIRD_HEIGHT, PIPE_WIDTH, pipe_locations[pipe_no]))
			pipe_no += 1

		
		fitness = (ticks - 1.5 * flaps)
		print("Generation : ",generation_n," Score : ",score, "Fitness : ", fitness , "Flaps : " , flaps , end="\r")
		pygame.display.flip()
		ticks = ticks + 1
		
		if score >= 5:
			time.sleep(0.005)
		else:
			time.sleep(0)
		# time.sleep(0.0001)
		# time.sleep(0.0001)

		if birdDead:
			break

		output = net.serial_activate([bird_height, next_pipe_height, next_pipe_distance, 1])
		# print(output[0])
		if output[0] < 0.5:
			isJumping = True
			flaps = flaps + 1
# ************************************************************

def eval_fitness(genomes):
	global generation_n

	print("Size : ",len(genomes))

	generatePipeLocations(500, 400)

	for g in genomes:
		net = nn.create_feed_forward_phenotype(g)
		runFlappy(net)
		g.fitness = fitness

	generation_n += 1

pop = population.Population('flappy_config')
pop.run(eval_fitness, 300)

print('Number of evaluations: {0}'.format(pop.total_evaluations))

# Display the most fit genome.
winner = pop.statistics.best_genome()
print('\nBest genome:\n{!s}'.format(winner))

winner_net = nn.create_feed_forward_phenotype(winner)



# # Verify network output against training data.
# print('\nOutput:')
# winner_net = nn.create_feed_forward_phenotype(winner)
# for inputs, expected in zip(xor_inputs, xor_outputs):
#	 output = winner_net.serial_activate(inputs)
#	 print("expected {0:1.5f} got {1:1.5f}".format(expected, output[0]))

# Visualize the winner network and plot/log statistics.
# visualize.plot_stats(pop.statistics)
# visualize.plot_species(pop.statistics)
# visualize.draw_net(winner, view=True, filename="xor2-all.gv")
# visualize.draw_net(winner, view=True, filename="xor2-enabled.gv", show_disabled=False)
# visualize.draw_net(winner, view=True, filename="xor2-enabled-pruned.gv", show_disabled=False, prune_unused=True)
# statistics.save_stats(pop.statistics)
# statistics.save_species_count(pop.statistics)
# statistics.save_species_fitness(pop.statistics)