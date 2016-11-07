from __future__ import print_function

from neat import nn, population, statistics
# from neat import visualize

import sys, pygame
import time
import random, math
from copy import deepcopy

pygame.init()

# ********************* FLAPPY ********************************

def setBird(n,BIRD_HEIGHT,BIRD_WIDTH):
	birdimg = "b"+str(n)+".png"
	bird = pygame.image.load(birdimg)
	bird = pygame.transform.scale(bird, (BIRD_WIDTH, BIRD_HEIGHT))
	return bird

def createPipe(dist, SCREEN_HEIGHT, BIRD_HEIGHT, PIPE_WIDTH, n_birds):
	midpt = random.randint(math.floor(SCREEN_HEIGHT * 0.25) , math.floor(SCREEN_HEIGHT * 0.75))
	temp1 = midpt - BIRD_HEIGHT/0.3
	temp2 = midpt + BIRD_HEIGHT/0.3

	pipe_top = pygame.Rect(dist,0,PIPE_WIDTH,temp1)
	pipe_bottom = pygame.Rect(dist,temp2,PIPE_WIDTH,SCREEN_HEIGHT - temp2)

	return [pipe_top, pipe_bottom, [False]*n_birds]

def runFlappy(nets, n_birds, genomes):
	JUMP_DURATION = 5
	SCREEN_HEIGHT = 400
	SCREEN_WIDTH = 600

	BIRD_HEIGHT = 30
	BIRD_WIDTH = 35
	BIRD_INI_POS_X = 200
	BIRD_INI_POS_Y = 100

	PIPE_WIDTH = 30
	PIPE_GAP = 200
	 
	size = width, height = SCREEN_WIDTH, SCREEN_HEIGHT
	speeds = [[0, 0]] * n_birds
	pipeSpeed = [-1.8 , 0]
	black = 0, 0, 0
	white = 255, 255, 255
	green = (0,255,0)
	blue = (0,0,255)
	gravity = 0.10

	isJumping = [True] * n_birds
	for i in range(n_birds):
		isJumping[i] = bool(random.getrandbits(1))
	jumpDuration = JUMP_DURATION
	jumpCounter = [0] * n_birds
	jumpVel = 1
	 
	# Drawing bird from image sprite
	screen = pygame.display.set_mode(size)

	birds = [None] * n_birds
	birdrect = [None] * n_birds
	birdSprite = 1
	for i in range(n_birds):
		tempBird = setBird(birdSprite,BIRD_HEIGHT,BIRD_WIDTH)
		# print(i,tempBird,tempBird.get_rect())
		birds[i] = tempBird
		birdrect[i] = tempBird.get_rect()

	for i in range(n_birds):
		# birdrect[i].y = BIRD_INI_POS_Y
		birdrect[i].y = random.randint(0,SCREEN_HEIGHT)
		birdrect[i].x = BIRD_INI_POS_X

	pipes = []
	dist = SCREEN_WIDTH
	for i in range(0,5):
		pipes.append(createPipe(dist + PIPE_GAP* i, SCREEN_HEIGHT,  BIRD_HEIGHT, PIPE_WIDTH, n_birds))

	scores = [0] * n_birds
	ticks = [0] * n_birds
	flaps = [0] * n_birds

	birdDead = [False] * n_birds
	fitnesses = [0] * n_birds

	while 1:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: sys.exit()

			# if event.type == pygame.KEYDOWN:
			# 	if event.key == pygame.K_SPACE:
			# 		isJumping = True
			# 		flaps = flaps + 1

		screen.fill(white)

		for i in range(n_birds):
			if not birdDead[i]:
				birdrect[i] = birdrect[i].move(speeds[i])

		for i in range(n_birds):
			if not birdDead[i]:
				if isJumping[i]:
					speeds[i][1] = -(jumpVel*jumpCounter[i] - 0.5 * gravity * jumpCounter[i] * jumpCounter[i])
					jumpCounter[i] = jumpCounter[i] + 1
				else:
					speeds[i][1] += gravity

				if jumpCounter[i] == jumpDuration:
					jumpCounter[i] = 0
					isJumping[i] = False

		for i in range(n_birds):
			if not birdDead[i]:
				screen.blit(birds[i], birdrect[i])
				birdSprite = (birdSprite + 1)%3
				birds[i] = setBird(birdSprite,BIRD_HEIGHT,BIRD_WIDTH)

		for pipe in pipes:
			pipe[0].move_ip(pipeSpeed)
			pipe[1].move_ip(pipeSpeed)
			pygame.draw.rect(screen, green, pipe[0], 0)
			pygame.draw.rect(screen, green, pipe[1], 0)


		bird_heights = [0] * n_birds
		next_pipe_heights = [0] * n_birds
		next_pipe_distances = [0] * n_birds

		for i in range(n_birds):
			# Bird fell below screen
			if birdrect[i].y > screen.get_rect().height:
				# print("\nBird out!")
				birdDead[i] = True
			# Brid touching ceiling
			if birdrect[i].y < 0:
				birdrect[i].y = 0
				# print("\nBird out!")

			for pipe in pipes:
				if pygame.Rect.colliderect(birdrect[i],pipe[0]):
					# print ("\nHit Pipe : Game Over")
					birdDead[i] = True
				if pygame.Rect.colliderect(birdrect[i],pipe[1]):
					# print ("\nHit Pipe : Game Over")
					birdDead[i] = True

			# Inputs for neural network
			bird_heights[i] = birdrect[i].y / SCREEN_HEIGHT
			next_pipe_heights[i] = None
			next_pipe_distances[i] = None
			for pipe in pipes:
				if pipe[1].x <= birdrect[i].x:
					continue
				else:
					next_pipe_heights[i]   = (SCREEN_HEIGHT - pipe[1].y) / SCREEN_HEIGHT
					next_pipe_distances[i] = pipe[1].x / SCREEN_WIDTH
					break
		
			# Score
			for pipe in pipes:
				if pipe[0].x <= BIRD_INI_POS_X and pipe[2][i] == False:
					pipe[2][i] = True
					scores[i] = scores[i] + 1
					# print("\nBH : ",bird_height, " PH : ",next_pipe_height, " PD : ",next_pipe_distance)

			fitnesses[i] = (ticks[i] - 1.5 * flaps[i])
			# print("Score : ",score, "Fitness : ", fitness , "Flaps : " , flaps , end="\r")
			ticks[i] = ticks[i] + 1

		
		# Infinite pipes
		if pipes[0][0].x <= 0:
			pipes.remove(pipes[0])
			pipes.append(createPipe(pipes[len(pipes) - 1][0].x + PIPE_GAP, SCREEN_HEIGHT, BIRD_HEIGHT, PIPE_WIDTH, n_birds))

		
		pygame.display.flip()
		time.sleep(0.008)
		# time.sleep(0.0001)

		if all(isDead == True for isDead in birdDead):
		# if not any(birdDead):
			i=0
			print(fitnesses)
			for g in genomes:
				g.fitness = fitnesses[i]
				i+=1
			break

		outputs = [None] * n_birds
		for i in range(n_birds):
			output = nets[i].serial_activate([bird_heights[i], next_pipe_heights[i], next_pipe_distances[i], 1])
			# print(output[0])
			if output[0] > 0.5:
				isJumping[i] = True
				flaps[i] = flaps[i] + 1
			# print(i,bird_heights[i], next_pipe_heights[i], next_pipe_distances[i],output,isJumping[i])
# ************************************************************


def eval_fitness(genomes):
	print("Size : ",len(genomes))

	nets = []
	for g in genomes:
		nets.append(nn.create_feed_forward_phenotype(g))

	runFlappy(nets,len(genomes),genomes)

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