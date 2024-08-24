import pygame
from typing import Union
from os import PathLike
FilePath = Union[str, bytes, PathLike]

pygame.init()
clock: pygame.time.Clock = pygame.time.Clock()

# SCREEN SETTING
SCREEN_SIZE: tuple[int, int] = (800, 600)
FPS: int = 60

# WORLD SETTING
PIXEL: int = 50
WORLD_GRID_COLOR: str = "WHITE"
WORLD_BORDER_COLOR: str = "YELLOW"

# CAMERA SETTING
CAMERA_PANNING_BORDER: dict = {'left': 100, 'right': 100, 'top': 100, 'bottom': 100}
CAMERA_PANNING_BORDER_COLOR: str = "YELLOW"
CAMERA_PANNING_BORDER_THICKNESS: int = 1

MOUSE_PANNING_SPEED: float = 10.0
KEY_PANNING_SPEED: float = 10.0

MOUSE_ZOOM_SPEED: float = 1.0
KEY_ZOOM_SPEED: float = 1.0

ZOOM_MIN: float = 0.2
ZOOM_MAX: float = 2.0

# BUTTON SETTING
BUTTON_SELECTED_COLOR: str = "GREEN"
BUTTON_SELECTED_COLOR_THICKNESS: int = 4

# FONT SETTING
FONT = None
DEBUG_LOG_FONT_STYLE_COLOR: str = "WHITE"

font: pygame.font = pygame.font.Font(FONT, 30)