# NEAT-bot
Unassisted game playing bot using NEAT.

It is a neuro-evolutionary game playing bot which learns to play games by itself 
* This implementation can be used to model any game playing bot, given the input and output of the neural network controlling the bot
* To demonstrate the use of NEAT we made a simple 2D helicopter flying game and used our implementation to power the bot
* In the first few generation the bot starts playing the game like a newbie, colliding with the walls every now and then
* The fitness of a bot depends on number of pipes it crosses without colliding. 
* On the basis of evaluation using this fitness function, it produces better off-springs after every generation
* It also evolves the structure of the neural network over every generation based on the fitness
* In every generation the neural networks trains itself and learns when to  lift the helicopter up/down in order to avoid collision. 
* Thus, the bot gets better and better with every new generation as it realises what to do and what not to do from its experience of previous generations. 
* After few generations, the bot starts playing the game like an expert

This project was a part of the CS561 Artificial Intelligence course at IIT Guwahati.

Video demo : <a href="https://www.youtube.com/watch?v=RsuPtCvKYCE" target="_blank"> youtube </a>

Requirements for running the script :

 1. Python3+
 2. PyGame1.9+

Most of the core NEAT code is inspired from the Java implementation by NeatMonster.

His project is here : https://github.com/NeatMonster/NEATFlappyBird
