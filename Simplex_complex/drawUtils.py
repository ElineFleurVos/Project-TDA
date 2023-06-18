import pygame
from pygame import Vector2



def to_screen(p: Vector2, camera):
    return (p - camera.center) * camera.zoom + (camera.screen_size / 2)


def get_datapoint_index_color(index):
    return pygame.Color(index * 125 % 255, index * 1231 % 255, index * 7 % 255)


pygame.init()
font_clock = pygame.font.Font('Arial.ttf', 50)

# source: https://stackoverflow.com/questions/20842801/how-to-display-text-in-pygame
def text_to_screen(screen, text, x, y, color, font):
    try:
        text = str(text)
        text = font.render(text, True, color)
        screen.blit(text, (x, y))

    except Exception as e:
        print('Font Error, saw it coming')
        raise e



