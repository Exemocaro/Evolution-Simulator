import pygame
import random
import numpy as np
import os
import datetime
from config import *
from wall import Wall
from food import Food
from cell import Cell

class Engine:
    def __init__(self):
        self.width = (WIDTH - INFO_PANEL_WIDTH) // CELL_SIZE
        self.height = (HEIGHT - LABEL_HEIGHT - BUTTON_AREA_HEIGHT) // CELL_SIZE
        self.foods = set()
        self.cells = []
        self.dead_cells = []
        self.generation = 1
        self.time = 0
        self.show_vision = False
        self.speed = 1
        self.cell_positions = {}
        self.food_positions = {}
        self.selected_cell = None
        self.paused = False
        self.stats = {"avg_lifespan": 0, "avg_food_eaten": 0, "avg_distance": 0, "remaining_food": 0}
        self.log_file = self.create_log_file()
        self.real_time = 0  # track real time
        self.simulated_time = 0  # track simulated time

    def create_log_file(self):
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return open(os.path.join(log_dir, f"simulation_{timestamp}.log"), "w")

    def add_food(self, x, y):
        food = Food(x, y)
        self.foods.add(food)
        self.food_positions[(int(x), int(y))] = food

    def add_cell(self, x, y):
        cell = Cell(x, y)
        cell.birth_time = self.simulated_time
        self.cells.append(cell)
        self.cell_positions[(int(x), int(y))] = cell

    def is_food(self, x, y):
        return (int(x) % self.width, int(y) % self.height) in self.food_positions

    def update(self):
        if not self.paused:
            self.real_time += 1 / FPS
            self.simulated_time += (1 / FPS) * self.speed
            new_cells = []
            self.cell_positions.clear()

            for cell in self.cells:
                if cell.update(self, self.speed):
                    new_cells.append(cell)
                    new_pos = (int(cell.x) % self.width, int(cell.y) % self.height)
                    self.cell_positions[new_pos] = cell
                    
                    if new_pos in self.food_positions:
                        cell.energy = min(CELL_ENERGY_MAX, cell.energy + FOOD_ENERGY)
                        cell.food_eaten += 1
                        food_to_remove = self.food_positions.pop(new_pos)
                        self.foods.remove(food_to_remove)
                        if RESPAWN_FOOD:
                            self.add_food(random.randint(0, self.width - 1), random.randint(0, self.height - 1))
                else:
                    cell.die(self.simulated_time)
                    self.dead_cells.append(cell)
                    if cell == self.selected_cell:
                        self.selected_cell = None

            self.cells = new_cells

            if self.simulated_time >= GENERATION_TIME or len(self.cells) == 0:
                self.calculate_stats()
                self.log_stats()
                self.next_generation()

    def calculate_stats(self):
        all_cells = self.cells + self.dead_cells
        if all_cells:
            self.stats["avg_lifespan"] = sum(cell.get_lifespan(self.simulated_time) for cell in all_cells) / len(all_cells)
            self.stats["avg_food_eaten"] = sum(cell.food_eaten for cell in all_cells) / len(all_cells)
            self.stats["avg_distance"] = sum(cell.distance_traveled for cell in all_cells) / len(all_cells)
        else:
            self.stats["avg_lifespan"] = 0
            self.stats["avg_food_eaten"] = 0
            self.stats["avg_distance"] = 0
        self.stats["remaining_food"] = len(self.foods)

    def log_stats(self):
        log_entry = f"Generation {self.generation}: "
        log_entry += f"Avg Lifespan: {self.stats['avg_lifespan']:.2f}, "
        log_entry += f"Avg Food Eaten: {self.stats['avg_food_eaten']:.2f}, "
        log_entry += f"Avg Distance: {self.stats['avg_distance']:.2f}, "
        log_entry += f"Remaining Food: {self.stats['remaining_food']}\n"
        self.log_file.write(log_entry)
        self.log_file.flush()

    def draw(self, screen):
        screen.fill(WHITE)
        for food in self.foods:
            pygame.draw.rect(screen, DARK_BLUE, (food.x * CELL_SIZE, food.y * CELL_SIZE + LABEL_HEIGHT, CELL_SIZE, CELL_SIZE))
        for cell in self.cells:
            color = tuple(int(c * (1 - cell.energy / CELL_ENERGY_MAX) + g * (cell.energy / CELL_ENERGY_MAX)) for c, g in zip(RED, GREEN))
            cell_center = (int(cell.x * CELL_SIZE + CELL_SIZE // 2) % (self.width * CELL_SIZE), 
                           int(cell.y * CELL_SIZE + CELL_SIZE // 2) % (self.height * CELL_SIZE) + LABEL_HEIGHT)
            pygame.draw.circle(screen, color, cell_center, CELL_SIZE // 2)
            
            # Draw a black circle around the selected cell
            if cell == self.selected_cell:
                pygame.draw.circle(screen, BLACK, cell_center, CELL_SIZE * 0.75 + 2, 2)
                
            if self.show_vision:
                for angle in [-30, 0, 30]:
                    vision_angle = (cell.orientation + angle) % 360
                    end_x = (cell.x + np.cos(np.radians(vision_angle)) * VISION_RANGE) % self.width
                    end_y = (cell.y + np.sin(np.radians(vision_angle)) * VISION_RANGE) % self.height
                    
                    # Calculate intermediate points for drawing
                    steps = 20  # Increase the number of steps for smoother lines
                    for i in range(steps):
                        start_x = (cell.x + i * np.cos(np.radians(vision_angle)) * VISION_RANGE / steps) % self.width
                        start_y = (cell.y + i * np.sin(np.radians(vision_angle)) * VISION_RANGE / steps) % self.height
                        end_x = (cell.x + (i+1) * np.cos(np.radians(vision_angle)) * VISION_RANGE / steps) % self.width
                        end_y = (cell.y + (i+1) * np.sin(np.radians(vision_angle)) * VISION_RANGE / steps) % self.height
                        
                        # Check if the line segment crosses the map boundary
                        if (abs(end_x - start_x) < self.width / 2 and 
                            abs(end_y - start_y) < self.height / 2):
                            pygame.draw.line(screen, GREY, 
                                            (int(start_x * CELL_SIZE + CELL_SIZE // 2), 
                                            int(start_y * CELL_SIZE + CELL_SIZE // 2) + LABEL_HEIGHT),
                                            (int(end_x * CELL_SIZE + CELL_SIZE // 2), 
                                            int(end_y * CELL_SIZE + CELL_SIZE // 2) + LABEL_HEIGHT), 1)

        font = pygame.font.Font(None, 36)
        info_text = f"Cells: {len(self.cells)} | Food: {len(self.foods)} | Generation: {self.generation} | Time: {self.simulated_time:.1f}"
        text_surface = font.render(info_text, True, GREY)
        screen.blit(text_surface, (10, 10))

        self.draw_info_panel(screen)

    def draw_info_panel(self, screen):
        panel_rect = pygame.Rect(WIDTH - INFO_PANEL_WIDTH, 0, INFO_PANEL_WIDTH, HEIGHT)
        pygame.draw.rect(screen, LIGHT_BLUE, panel_rect)

        if self.selected_cell:
            self.draw_cell_info(screen, self.selected_cell)
            self.draw_neural_network(screen, self.selected_cell)

        # Draw stats
        font = pygame.font.Font(None, 24)
        y = HEIGHT - 120
        for stat, value in self.stats.items():
            text = font.render(f"{stat.replace('_', ' ').title()}: {value:.2f}", True, BLACK)
            screen.blit(text, (WIDTH - INFO_PANEL_WIDTH + 10, y))
            y += 30

    def draw_neural_network(self, screen, cell):
        activations = cell.get_neuron_activations()
        weights = cell.brain.get_weights()

        input_y = 200
        output_y = 200
        input_x = WIDTH - INFO_PANEL_WIDTH + 50
        output_x = WIDTH - 50

        for i, (label, value) in enumerate(activations["inputs"]):
            color = tuple(int(255 * abs(value)) for _ in range(3))
            pygame.draw.circle(screen, color, (input_x, input_y + i * 30), 10)
            text = pygame.font.Font(None, 20).render(label, True, BLACK)
            screen.blit(text, (input_x - 40, input_y + i * 30 - 5))

        for j, (label, value) in enumerate(activations["outputs"]):
            color = tuple(int(255 * abs(value)) for _ in range(3))
            pygame.draw.circle(screen, color, (output_x, output_y + j * 100), 10)
            text = pygame.font.Font(None, 20).render(label, True, BLACK)
            screen.blit(text, (output_x + 15, output_y + j * 100 - 5))

        for i in range(len(activations["inputs"])):
            for j in range(len(activations["outputs"])):
                weight = weights[i, j]
                width = int(abs(weight) * 5)
                color = tuple(int(255 * (abs(activations["inputs"][i][1]) + abs(activations["outputs"][j][1])) / 2) for _ in range(3))
                pygame.draw.line(screen, color, (input_x + 10, input_y + i * 30), 
                                 (output_x - 10, output_y + j * 100), width)
    def draw_cell_info(self, screen, cell):
        font = pygame.font.Font(None, 24)
        y = 10
        for key, value in cell.get_info().items():
            text = font.render(f"{key}: {value}", True, BLACK)
            screen.blit(text, (WIDTH - INFO_PANEL_WIDTH + 10, y))
            y += 30

    def select_cell(self, mouse_pos):
        x, y = mouse_pos
        grid_x = x // CELL_SIZE
        grid_y = (y - LABEL_HEIGHT) // CELL_SIZE
        
        nearest_cell = None
        nearest_distance = float('inf')

        # Check cells in a 5x5 area around the clicked position
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                check_x = (grid_x + dx) % self.width
                check_y = (grid_y + dy) % self.height
                if (check_x, check_y) in self.cell_positions:
                    cell = self.cell_positions[(check_x, check_y)]
                    distance = (cell.x - grid_x)**2 + (cell.y - grid_y)**2
                    if distance < nearest_distance:
                        nearest_cell = cell
                        nearest_distance = distance

        self.selected_cell = nearest_cell

    def initialize(self):
        for _ in range(INITIAL_CELLS):
            self.add_cell(random.uniform(0, self.width), random.uniform(0, self.height))

        for _ in range(INITIAL_FOOD):
            self.add_food(random.uniform(0, self.width), random.uniform(0, self.height))

    def next_generation(self):
        self.generation += 1
        self.real_time = 0
        self.simulated_time = 0
        self.selected_cell = None

        # Combine living and recently dead cells
        all_cells = self.cells + self.dead_cells
        if all_cells:
            all_cells.sort(key=lambda c: (c.lifetime, c.energy), reverse=True)
            top_cells = all_cells[:max(INITIAL_CELLS // 10, 1)]
        else:
            top_cells = [Cell(random.randint(1, self.width - 2), random.randint(1, self.height - 2))]

        new_cells = []
        while len(new_cells) < INITIAL_CELLS - 2:  # Leave space for 2 random cells
            parent = random.choice(top_cells)
            child = parent.reproduce()
            child.x = random.randint(1, self.width - 2)
            child.y = random.randint(1, self.height - 2)
            new_cells.append(child)

        # Add 2 completely new random cells
        for _ in range(2):
            new_cell = Cell(random.randint(1, self.width - 2), random.randint(1, self.height - 2))
            new_cells.append(new_cell)

        # reset the brith time of each cell
        for cell in new_cells:
            cell.birth_time = self.simulated_time

        self.cells = new_cells
        self.dead_cells = []  # Clear the dead cells list
        self.cell_positions = {(int(cell.x), int(cell.y)): cell for cell in self.cells}

        # Reset food
        self.foods.clear()
        self.food_positions.clear()
        for _ in range(INITIAL_FOOD):
            self.add_food(random.randint(1, self.width - 2), random.randint(1, self.height - 2))

    def toggle_vision(self):
        self.show_vision = not self.show_vision

    def force_next_generation(self):
        self.next_generation()

    def toggle_pause(self):
        self.paused = not self.paused

    def increase_speed(self):
        current_index = SIMULATION_SPEEDS.index(self.speed)
        self.speed = SIMULATION_SPEEDS[(current_index + 1) % len(SIMULATION_SPEEDS)]

    def decrease_speed(self):
        current_index = SIMULATION_SPEEDS.index(self.speed)
        self.speed = SIMULATION_SPEEDS[(current_index - 1) % len(SIMULATION_SPEEDS)]
    
    def restart(self):
        self.generation = 1
        self.real_time = 0
        self.simulated_time = 0
        self.selected_cell = None
        self.cells.clear()
        self.dead_cells.clear()
        self.cell_positions.clear()
        self.foods.clear()
        self.food_positions.clear()
        self.selected_cell = None
        self.log_file.close()
        self.log_file = self.create_log_file()
        self.initialize()

    def __del__(self):
        if hasattr(self, 'log_file'):
            self.log_file.close()
