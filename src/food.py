import pygame
from config import GREEN, CELL_SIZE, FOOD_ENERGY

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = FOOD_ENERGY

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
