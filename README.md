# Evolution Simulator

## Overview
This Evolution Simulator is a Python-based project that models the behavior and evolution of simple organisms (cells) in a 2D environment. The simulation demonstrates principles of artificial life, neural networks, and genetic algorithms.

Key aspects of the simulation:

- Cells move around a 2D grid, seeking food and avoiding starvation.
- Each cell is controlled by a simple neural network that determines its actions.
- Cells consume energy in the form of food as they move and rotate, and gain energy by eating food.
- The environment is wrap-around, meaning cells that move off one edge appear on the opposite side.
- After a set time or when all cells die, the generation ends.
- Cells that survive longest and/or gather the most energy will create a new generation with small mutation in their "brains".
- This involves creating new cells with slightly mutated neural networks.
- Over generations, cells evolve to better navigate and survive in their environment.

Neural Network Structure:
- Inputs (8 neurons):
  - Current energy level
  - Current orientation
  - 3 "vision" inputs/vectors, each with:
    - Distance to nearest object (limited range)
    - Type of object for each vision vector
- Outputs (3 neurons):
  - Rotate clockwise
  - Rotate counter-clockwise
  - Move forward

Statistics tracked:
- Average lifespan of cells
- Average amount of food eaten per cell
- Average distance traveled by cells
- Remaining food at the end of each generation

Vision System:
Cells have a limited vision range, allowing them to detect objects - food (or map edges, but these were disabled in the current version of the simulation) - within a certain distance in three directions (front, front-left, front-right).

## Demo

### Simulation in Action
![Demo](demo.gif)

### Statistics Plot
![Statistics example](stats.png)

## Requirements
- Python 3.12.1

## Installation
1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the main simulation:
   ```
   python src/main.py
   ```
2. After running a simulation, you can visualize the statistics:
   ```
   python src/plot_logs.py
   ```

## Controls
- "Vision" button: Toggle cell vision lines
- "Next Gen" button: Force start of next generation
- "Speed" button: Adjust simulation speed (Left-click to increase, Right-click to decrease)
- "Pause/Resume" button: Pause or resume the simulation
- "Restart" button: Restart the entire simulation with new random cells

## Project Structure
- `src/`: Source code directory
  - `main.py`: Main entry point for the simulation
  - `engine.py`: Core simulation logic
  - `cell.py`: Cell class definition and neural network
  - `food.py`: Food class definition
  - `config.py`: Configuration settings
  - `plot_logs.py`: Script for visualizing simulation statistics
- `logs/`: Directory for simulation log files

## Contributing
Contributions to improve the simulation or add new features are welcome. Please fork the repository and create a pull request with your changes.
