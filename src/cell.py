import pygame
import numpy as np
from config import *

class Cell:
    def __init__(self, x, y, weights=None):
        self.x = x
        self.y = y
        self.energy = CELL_ENERGY_MAX
        self.orientation = np.random.rand() * 360
        self.brain = NeuralNetwork(8, 3, weights)
        self.lifetime = 0
        self.last_inputs = None
        self.last_outputs = None

    def draw(self, screen):
        color = tuple(int(c * (1 - self.energy / CELL_ENERGY_MAX) + g * (self.energy / CELL_ENERGY_MAX)) for c, g in zip(RED, GREEN))
        pygame.draw.circle(screen, color, (int(self.x * CELL_SIZE + CELL_SIZE // 2), 
                                           int(self.y * CELL_SIZE + CELL_SIZE // 2)), CELL_SIZE // 2)

    def draw_vision(self, screen):
        for angle in [-30, 0, 30]:
            vision_angle = (self.orientation + angle) % 360
            end_x = self.x * CELL_SIZE + np.cos(np.radians(vision_angle)) * VISION_RANGE * CELL_SIZE
            end_y = self.y * CELL_SIZE + np.sin(np.radians(vision_angle)) * VISION_RANGE * CELL_SIZE
            pygame.draw.line(screen, GREY, 
                             (int(self.x * CELL_SIZE + CELL_SIZE // 2), int(self.y * CELL_SIZE + CELL_SIZE // 2)),
                             (int(end_x + CELL_SIZE // 2), int(end_y + CELL_SIZE // 2)), 1)

    def update(self, environment, speed):
        self.lifetime += 1
        self.energy -= CELL_IDLE_COST * speed
        self.last_inputs = self.get_inputs(environment)
        self.last_outputs = self.brain.forward(self.last_inputs)
        self.process_outputs(self.last_outputs, environment, speed)
        return self.energy > 0
    
    def get_info(self):
        return {
            "Position": f"({self.x:.2f}, {self.y:.2f})",
            "Energy": f"{self.energy:.2f}",
            "Orientation": f"{self.orientation:.2f}°",
            "Lifetime": str(self.lifetime)
        }

    def get_neuron_activations(self):
        input_labels = ["Energy", "Orient", "V1 Dist", "V1 Type", "V2 Dist", "V2 Type", "V3 Dist", "V3 Type"]
        output_labels = ["Rotate CW", "Rotate CCW", "Move"]
        return {
            "inputs": list(zip(input_labels, self.last_inputs)) if self.last_inputs is not None else [],
            "outputs": list(zip(output_labels, self.last_outputs)) if self.last_outputs is not None else []
        }

    def get_inputs(self, environment):
        inputs = np.array([self.energy / CELL_ENERGY_MAX, self.orientation / 360])
        vision_inputs = np.zeros(6)
        for i, angle in enumerate([-30, 0, 30]):
            vision_angle = (self.orientation + angle) % 360
            dx = np.cos(np.radians(vision_angle))
            dy = np.sin(np.radians(vision_angle))
            for j in range(1, VISION_RANGE + 1):
                check_x = int(self.x + dx * j)
                check_y = int(self.y + dy * j)
                if environment.is_wall(check_x, check_y):
                    vision_inputs[i*2:i*2+2] = [j / VISION_RANGE, 0]
                    break
                elif environment.is_food(check_x, check_y):
                    vision_inputs[i*2:i*2+2] = [j / VISION_RANGE, 1]
                    break
            else:
                vision_inputs[i*2:i*2+2] = [-1, -1]
        return np.concatenate([inputs, vision_inputs])

    def process_outputs(self, outputs, environment, speed):
        rotate_cw, rotate_ccw, move = outputs

        if rotate_cw > 0.5:
            self.orientation += 10 * speed
            self.energy -= CELL_ROTATE_COST * speed
        if rotate_ccw > 0.5:
            self.orientation -= 10 * speed
            self.energy -= CELL_ROTATE_COST * speed
        if move > 0.5:
            dx = np.cos(np.radians(self.orientation)) * 0.1 * speed
            dy = np.sin(np.radians(self.orientation)) * 0.1 * speed
            new_x = self.x + dx
            new_y = self.y + dy
            if not environment.is_wall(int(new_x), int(new_y)):
                self.x = new_x
                self.y = new_y
                self.energy -= CELL_MOVE_COST * speed

        self.orientation %= 360
        self.energy = max(CELL_ENERGY_MIN, min(CELL_ENERGY_MAX, self.energy))

    def reproduce(self):
        child_weights = self.brain.weights.copy()
        mask = np.random.random(child_weights.shape) < MUTATION_RATE
        child_weights[mask] += np.random.normal(0, MUTATION_AMOUNT, mask.sum())
        return Cell(self.x, self.y, child_weights)

class NeuralNetwork:
    def __init__(self, input_size, output_size, weights=None):
        if weights is None:
            self.weights = np.random.randn(input_size, output_size)
        else:
            self.weights = weights

    def forward(self, X):
        return np.tanh(np.dot(X, self.weights))

    def get_weights(self):
        return self.weights