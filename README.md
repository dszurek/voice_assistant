This is a project I worked on for The University of Alabama EcoCAR. 
This repository contains the early version of a voice assistant for the competition car, with a working voice assistant powered by a large language model, and an interaction service that allows the program to interact with other software and features of the EcoCAR competition car. The interaction service is barebones in this repository on purpose to provide a good starting point, and is built in a way that is easy to understand and change for specific needs. 
Requirements are listed in the pyproject.toml file, I recommend to work on this program within a poetry virtual environment so it is possible to use the built in commands to download the dependencies and automatically add them to the virtual environment requirements. 

Other requirements include:
PyTorch
CUDA 12.4
Ollama
