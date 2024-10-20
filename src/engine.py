import pygame
import random
import numpy as np
from config import *
from wall import Wall
from food import Food
from cell import Cell

class Engine:
    def __init__(self):
        self.width = (WIDTH - INFO_PANEL_WIDTH) // CELL_SIZE
        self.height = (HEIGHT - LABEL_HEIGHT - BUTTON_AREA_HEIGHT) // CELL_SIZE
        self.walls = set()
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

    def add_wall(self, x, y):
        self.walls.add((x, y))

    def add_food(self, x, y):
        if (x, y) not in self.walls and (x, y) not in self.cell_positions:
            self.foods.add(Food(x, y))
            self.food_positions[(x, y)] = True
        else:
            self.add_food(random.randint(1, self.width - 2), random.randint(1, self.height - 2))

    def add_cell(self, x, y):
        if (x, y) not in self.walls and (x, y) not in self.food_positions:
            cell = Cell(x, y)
            self.cells.append(cell)
            self.cell_positions[(int(x), int(y))] = cell
        else:
            self.add_cell(random.randint(1, self.width - 2), random.randint(1, self.height - 2))

    def update(self):
        if not self.paused:
            self.time += 1 / FPS * self.speed
            new_cells = []
            self.cell_positions.clear()

            for cell in self.cells:
                if cell.update(self, self.speed):
                    new_cells.append(cell)
                    new_pos = (int(cell.x), int(cell.y))
                    self.cell_positions[new_pos] = cell
                    
                    if new_pos in self.food_positions:
                        cell.energy = min(CELL_ENERGY_MAX, cell.energy + FOOD_ENERGY)
                        self.foods = {food for food in self.foods if (food.x, food.y) != new_pos}
                        self.food_positions.pop(new_pos)
                        if RESPAWN_FOOD:
                            self.add_food(random.randint(1, self.width - 2), random.randint(1, self.height - 2))
                else:
                    self.dead_cells.append(cell)  # Add dead cells to the dead_cells list

            self.cells = new_cells

            if self.time >= GENERATION_TIME or len(self.cells) == 0:
                self.next_generation()

    def draw(self, screen):
        # Draw background
        screen.fill(LIGHT_BLUE)
        pygame.draw.rect(screen, WHITE, (0, LABEL_HEIGHT, WIDTH - INFO_PANEL_WIDTH, HEIGHT - LABEL_HEIGHT - BUTTON_AREA_HEIGHT))

        # Draw simulation elements
        for wall in self.walls:
            pygame.draw.rect(screen, BLACK, (wall[0] * CELL_SIZE, wall[1] * CELL_SIZE + LABEL_HEIGHT, CELL_SIZE, CELL_SIZE))
        for food in self.foods:
            pygame.draw.rect(screen, DARK_BLUE, (food.x * CELL_SIZE, food.y * CELL_SIZE + LABEL_HEIGHT, CELL_SIZE, CELL_SIZE))
        for cell in self.cells:
            color = tuple(int(c * (1 - cell.energy / CELL_ENERGY_MAX) + g * (cell.energy / CELL_ENERGY_MAX)) for c, g in zip(RED, GREEN))
            pygame.draw.circle(screen, color, (int(cell.x * CELL_SIZE + CELL_SIZE // 2), 
                                               int(cell.y * CELL_SIZE + CELL_SIZE // 2) + LABEL_HEIGHT), CELL_SIZE // 2)
            if self.show_vision:
                for angle in [-30, 0, 30]:
                    vision_angle = (cell.orientation + angle) % 360
                    end_x = cell.x * CELL_SIZE + np.cos(np.radians(vision_angle)) * VISION_RANGE * CELL_SIZE
                    end_y = cell.y * CELL_SIZE + np.sin(np.radians(vision_angle)) * VISION_RANGE * CELL_SIZE
                    pygame.draw.line(screen, GREY, 
                                     (int(cell.x * CELL_SIZE + CELL_SIZE // 2), int(cell.y * CELL_SIZE + CELL_SIZE // 2) + LABEL_HEIGHT),
                                     (int(end_x + CELL_SIZE // 2), int(end_y + CELL_SIZE // 2) + LABEL_HEIGHT), 1)

        # Draw info text
        font = pygame.font.Font(None, 36)
        info_text = f"Cells: {len(self.cells)} | Food: {len(self.foods)} | Generation: {self.generation} | Time: {self.time:.1f}"
        text_surface = font.render(info_text, True, BLACK)
        screen.blit(text_surface, (10, 10))

        self.draw_info_panel(screen)

    def draw_info_panel(self, screen):
        panel_rect = pygame.Rect(WIDTH - INFO_PANEL_WIDTH, 0, INFO_PANEL_WIDTH, HEIGHT)
        pygame.draw.rect(screen, LIGHT_BLUE, panel_rect)

        if self.selected_cell:
            self.draw_cell_info(screen, self.selected_cell)
            self.draw_neural_network(screen, self.selected_cell)

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
        x = (x - CELL_SIZE // 2) // CELL_SIZE
        y = (y - LABEL_HEIGHT - CELL_SIZE // 2) // CELL_SIZE
        self.selected_cell = self.cell_positions.get((x, y))

    def initialize(self):
        for x in range(self.width):
            self.add_wall(x, 0)
            self.add_wall(x, self.height - 1)
        for y in range(self.height):
            self.add_wall(0, y)
            self.add_wall(self.width - 1, y)

        for _ in range(INITIAL_CELLS):
            self.add_cell(random.randint(1, self.width - 2), random.randint(1, self.height - 2))

        for _ in range(INITIAL_FOOD):
            self.add_food(random.randint(1, self.width - 2), random.randint(1, self.height - 2))

    def next_generation(self):
        self.generation += 1
        self.time = 0

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

        self.cells = new_cells
        self.dead_cells = []  # Clear the dead cells list
        self.cell_positions = {(int(cell.x), int(cell.y)): cell for cell in self.cells}

        # Reset food
        self.foods.clear()
        self.food_positions.clear()
        for _ in range(INITIAL_FOOD):
            self.add_food(random.randint(1, self.width - 2), random.randint(1, self.height - 2))

    def is_wall(self, x, y):
        return (x, y) in self.walls

    def is_food(self, x, y):
        return (x, y) in self.food_positions

    def toggle_vision(self):
        self.show_vision = not self.show_vision

    def force_next_generation(self):
        self.next_generation()

    def toggle_pause(self):
        self.paused = not self.paused

    def increase_speed(self):
        speeds = [0.5, 1, 2, 4, 8]
        current_index = speeds.index(self.speed)
        self.speed = speeds[min(current_index + 1, len(speeds) - 1)]

    def decrease_speed(self):
        speeds = [0.5, 1, 2, 4, 8]
        current_index = speeds.index(self.speed)
        self.speed = speeds[max(current_index - 1, 0)]
    
    def restart(self):
        self.generation = 1
        self.time = 0
        self.cells.clear()
        self.dead_cells.clear()
        self.cell_positions.clear()
        self.foods.clear()
        self.food_positions.clear()
        self.selected_cell = None
        self.initialize()
