from typing import Union
from os import PathLike

FilePath = Union[str, bytes, PathLike]

# WORLD SETTING
SCREEN_SIZE: tuple[int, int] = (800, 600)
WORLD_SIZE: tuple[int, int] = (64, 64)
PIXEL: int = 50

# CAMERA SETTING
CAMERA_PANNING_BORDER: dict = {'left': 100, 'right': 100, 'top': 100, 'bottom': 100}
MOUSE_PANNING_SPEED: float = 10.0
KEY_PANNING_SPEED: float = 10.0

ZOOM_MAX: float = 2.0
ZOOM_MIN: float = 0.2
MOUSE_ZOOM_SPEED: float = 1.0
KEY_ZOOM_SPEED: float = 0.2

# COLOR SETTING
GRID_COLOR: str = "WHITE"
CAMERA_PANNING_BORDER_COLOR: str = "YELLOW"

BUTTON_SELECTED_COLOR: str = "GREEN"
BUTTON_SELECTED_COLOR_THICKNESS: int = 4