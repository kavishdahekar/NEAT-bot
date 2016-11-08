# NEAT-bot
Unassisted game playing bot using NEAT.

This project was a part of the CS561 Artificial Intelligence course at IIT Guwahati.

Video demo : <a href="https://www.youtube.com/watch?v=RsuPtCvKYCE" target="_blank"> youtube </a>

Requirements for running the script :

 1. Python3+
 2. PyGame1.9+

Most of the core NEAT code is inspired from the Java implementation by NeatMonster.
His project is here : https://github.com/NeatMonster/NEATFlappyBird

## How it works

This neuro-evolutionary game playing bot is capable of learning to play simple games by itself.

 - This implementation can be used to model any game playing bot, given the input and output of the neural network controlling the game inputs and an appropriate fitness function.
 - To demonstrate the use of NEAT we made a simple 2D helicopter flying game and used our implementation to power the bot.
 - In the first few generation the bot is terrbile at playing the game, colliding with the walls every now and then. All initial movement is a result of a randomly generated neural network.
 - The fitness of the bot depends on number of pipes it crosses without colliding. 
 - Better off-springs are generated after every generation on the basis of this fitness function.
 - The structure of the neural network changes over every generation based on the fitness as better performing individuals are mated into the next generation.
 - In every generation the neural networks train themselves and eventually learn when to lift the helicopter up/down in order to avoid collision.
 - The results eventually converge to a point where the bot is almost unbeatable at the game.
