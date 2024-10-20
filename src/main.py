import pygame
from config import *
from engine import Engine

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Evolution Simulation")
    clock = pygame.time.Clock()

    engine = Engine()
    engine.initialize()

    font = pygame.font.Font(None, 32)
    button_width = 120
    button_height = 40
    button_y = HEIGHT - BUTTON_AREA_HEIGHT + 5
    restart_button = pygame.Rect(10, button_y, button_width, button_height)
    vision_button = pygame.Rect(140, button_y, button_width, button_height)
    next_gen_button = pygame.Rect(270, button_y, button_width, button_height)
    speed_button = pygame.Rect(400, button_y, button_width, button_height)
    pause_button = pygame.Rect(530, button_y, button_width, button_height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if restart_button.collidepoint(event.pos):
                        engine.restart()
                    elif vision_button.collidepoint(event.pos):
                        engine.toggle_vision()
                    elif next_gen_button.collidepoint(event.pos):
                        engine.force_next_generation()
                    elif speed_button.collidepoint(event.pos):
                        engine.increase_speed()
                    elif pause_button.collidepoint(event.pos):
                        engine.toggle_pause()
                    else:
                        engine.select_cell(event.pos)
                elif event.button == 3:  # Right click
                    if speed_button.collidepoint(event.pos):
                        engine.decrease_speed()

        engine.update()
        engine.draw(screen)

        # Draw buttons
        pygame.draw.rect(screen, GREY, restart_button)
        restart_text = font.render("Restart", True, WHITE)
        screen.blit(restart_text, (restart_button.x + 5, restart_button.y + 5))

        pygame.draw.rect(screen, GREY, vision_button)
        vision_text = font.render("Vision", True, WHITE)
        screen.blit(vision_text, (vision_button.x + 5, vision_button.y + 5))

        pygame.draw.rect(screen, GREY, next_gen_button)
        next_gen_text = font.render("Next Gen", True, WHITE)
        screen.blit(next_gen_text, (next_gen_button.x + 5, next_gen_button.y + 5))

        pygame.draw.rect(screen, GREY, speed_button)
        speed_text = font.render(f"{engine.speed}x", True, WHITE)
        screen.blit(speed_text, (speed_button.x + 5, speed_button.y + 5))

        pygame.draw.rect(screen, GREY, pause_button)
        pause_text = font.render("Resume" if engine.paused else "Pause", True, WHITE)
        screen.blit(pause_text, (pause_button.x + 5, pause_button.y + 5))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()