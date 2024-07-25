from typing import Union
from os import PathLike

FilePath = Union[str, bytes, PathLike]

# WORLD SETTING
WORLD_SIZE: tuple[int, int] = (32, 32)
PIXEL: int = 50
WORLD_BORDER_COLOR: str = "YELLOW"
WORLD_GRID_COLOR: str = "WHITE"

# CAMERA SETTING
SCREEN_SIZE: tuple[int, int] = (800, 600)
CAMERA_PANNING_BORDER: dict = {'left': 100, 'right': 100, 'top': 100, 'bottom': 100}
MOUSE_PANNING_SPEED: float = 10.0
KEY_PANNING_SPEED: float = 10.0
ZOOM_MAX: float = 2.0
ZOOM_MIN: float = 0.2
MOUSE_ZOOM_SPEED: float = 1.0
KEY_ZOOM_SPEED: float = 1.0
CAMERA_PANNING_BORDER_COLOR: str = "YELLOW"

# BUTTON SETTING
BUTTON_SELECTED_COLOR_THICKNESS: int = 4
BUTTON_SELECTED_COLOR: str = "GREEN"

# FONT SETTING
FONT: FilePath = None
DEBUG_LOG_STYLE_COLOR: str = "WHITE"