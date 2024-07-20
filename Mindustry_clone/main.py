import pygame
import numpy as np
from pygame.math import Vector2
from pygame.sprite import Sprite, Group
from typing import Union
from os import PathLike

FilePath = Union[str, bytes, PathLike]

# WORLD SETTING
SCREEN_SIZE: tuple[int, int] = (800, 600)
PIXEL: int = 50

# CAMERA SETTING
CAMERA_PANNING_BORDER: dict = {'left': 100, 'right': 100, 'top': 100, 'bottom': 100}
MOUSE_PANNING_SPEED: float = 10.0
KEY_PANNING_SPEED: float = 10.0

ZOOM_MAX: float = 2.0
ZOOM_MIN: float = 0.5
MOUSE_ZOOM_SPEED: float = 1.0
KEY_ZOOM_SPEED: float = 0.2

# COLOR SETTING
GRID_COLOR: str = "WHITE"
CAMERA_PANNING_BORDER_COLOR: str = "YELLOW"

pygame.init()
FPS: int = 60
clock = pygame.time.Clock()

# ------------------------------------------------------------------------ #
#                                  CAMERA                                  #
# ------------------------------------------------------------------------ #
# Convert world space --> screen space
def WorldToScreenCoordinate(world_position) -> Vector2:
    """
    Return screen coordinate relatives to its offset and scaling.
    """
    screen_x = (world_position[0] - camera.offset.x) * camera.scale
    screen_y = (world_position[1] - camera.offset.y) * camera.scale
    return Vector2((int(screen_x), int(screen_y)))

# Convert screen space --> world space
def ScreenToWorldCoordinate(screen_position) -> Vector2:
    """
    Return original world coordinate.
    """
    world_x = screen_position[0] / camera.scale + camera.offset.x
    world_y = screen_position[1] / camera.scale + camera.offset.y
    return Vector2((int(world_x), int(world_y)))

class Camera:
    def __init__(self):
        # Public variables
        self.screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE)
        self.offset: Vector2 = Vector2()
        self.scale: float = 1.0
        self.start_panning: Vector2 = Vector2()
        self.mouse_scroll_y: int = 0

        # Private variables
        l: int = CAMERA_PANNING_BORDER['left']
        t: int = CAMERA_PANNING_BORDER['top']
        w: int = self.screen.get_size()[0] - CAMERA_PANNING_BORDER['left'] - CAMERA_PANNING_BORDER['right']
        h: int = self.screen.get_size()[1] - CAMERA_PANNING_BORDER['top'] - CAMERA_PANNING_BORDER['bottom']
        self.__direction: Vector2 = Vector2()
        self.__camera_border: pygame.Rect = pygame.Rect(l, t, w, h)

    def movement(self, mouse_position: Vector2):
        # Mouse pressed panning
        mouses = pygame.mouse.get_pressed()
        if mouses[0]:
            self.offset += self.start_panning - mouse_position
            self.start_panning = mouse_position

        # Mouse border panning
        if pygame.mouse.get_focused():
            if mouse_position.x < self.__camera_border.left:
                self.__direction.x = -1
            elif mouse_position.x > self.__camera_border.right:
                self.__direction.x = 1
            else:

                self.__direction.x = 0
            if mouse_position.y < self.__camera_border.top:
                self.__direction.y = -1
            elif mouse_position.y > self.__camera_border.bottom:
                self.__direction.y = 1
            else:
                self.__direction.y = 0
            self.offset += self.__direction * MOUSE_PANNING_SPEED

        # Key pressed panning
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.__direction.x = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.__direction.x = 1
        else:
            self.__direction.x = 0

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.__direction.y = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.__direction.y = 1
        else:
            self.__direction.y = 0
        self.offset += self.__direction * KEY_PANNING_SPEED

        before_zoom = ScreenToWorldCoordinate(mouse_position)

        # Mouse scroll zoom
        if self.mouse_scroll_y < 0:
            self.scale += 0.1 * MOUSE_ZOOM_SPEED
            if self.scale > ZOOM_MAX:
                self.scale = ZOOM_MAX
        elif self.mouse_scroll_y > 0:
            self.scale -= 0.1 * MOUSE_ZOOM_SPEED
            if self.scale < ZOOM_MIN:
                self.scale = ZOOM_MIN

        # Key zoom
        if keys[pygame.K_q] or keys[pygame.K_LEFTBRACKET]:
            self.scale += 0.1 * KEY_ZOOM_SPEED
            if self.scale > ZOOM_MAX:
                self.scale = ZOOM_MAX
        elif keys[pygame.K_e] or keys[pygame.K_RIGHTBRACKET]:
            self.scale -= 0.1 * KEY_ZOOM_SPEED
            if self.scale < ZOOM_MIN:
                self.scale = ZOOM_MIN

        after_zoom = ScreenToWorldCoordinate(mouse_position)

        self.offset += before_zoom - after_zoom

        self.mouse_scroll_y = 0 # Reset value

    def draw_panning_border(self):
        pygame.draw.rect(self.screen, CAMERA_PANNING_BORDER_COLOR, self.__camera_border, 5)

camera = Camera()
# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------ #
#                                 BLOCK                                    #
# ------------------------------------------------------------------------ #
class Block(Sprite):
    def __init__(self, image_source: FilePath = ""):
        super().__init__()
        self.image_source: str = image_source
        if not len(self.image_source):
            self.original_image: pygame.Surface = pygame.image.load('Images/NOT_FOUND.png').convert_alpha()
        else:
            self.original_image: pygame.Surface = pygame.image.load(self.image_source).convert_alpha()

        self.name: str = ""
        self.id: int = 0
        self.image: pygame.Surface = self.original_image
        self.rect: pygame.Rect = self.image.get_rect()
        self.position: Vector2 = Vector2()

    def copy(self):
        cloned_block = Block(self.image_source)
        cloned_block.name = self.name
        cloned_block.id = self.id
        cloned_block.image = self.image.copy()
        cloned_block.rect = self.rect.copy()
        cloned_block.position = self.position
        return cloned_block

    def update(self):
        self.rect.topleft = WorldToScreenCoordinate(self.position * PIXEL)
        self.image = pygame.transform.scale(self.original_image, (PIXEL * camera.scale, PIXEL * camera.scale))

Grass = Block('Images/Block_Images/Grass_001.png')
Grass.name = 'Grass'
Grass.id = 1
# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------ #
#                                  MAP                                     #
# ------------------------------------------------------------------------ #
class WorldEditor:
    def __init__(self, world_size:tuple[int, int]):
        self.world_size: tuple[int, int] = world_size
        self.__base_world_index: np.ndarray = np.zeros(world_size)

        self.ground_sprite_group: Group = Group()
        self.ground_sprite_dict: dict = {}

    def ScreenToWorldIndex(self, position) -> (tuple[int, int] | tuple[None, None]):
        x, y = ScreenToWorldCoordinate(position) // PIXEL
        # Return None if the index is out of range of the grid_indices
        if (x < 0 or x > self.__base_world_index.shape[0] - 1) or (y < 0 or y > self.__base_world_index.shape[1] - 1):
            return None, None
        return int(x), int(y)

    def draw_grid(self):
        x_line = np.linspace(0, self.world_size[0], self.world_size[0] + 1)
        y_line = np.linspace(0, self.world_size[1], self.world_size[1] + 1)
        for x in x_line:
            pygame.draw.line(camera.screen, GRID_COLOR, WorldToScreenCoordinate((x * PIXEL, y_line[0]) * PIXEL),
                             WorldToScreenCoordinate((x * PIXEL, y_line[-1] * PIXEL)))
        for y in y_line:
            pygame.draw.line(camera.screen, GRID_COLOR, WorldToScreenCoordinate((x_line[0] * PIXEL, y* PIXEL)),
                             WorldToScreenCoordinate((x_line[-1] * PIXEL, y * PIXEL)))

    def draw_sprites(self):
        self.ground_sprite_group.update()

        self.ground_sprite_group.draw(camera.screen)

    def paint(self, position, obj):
        x, y = self.ScreenToWorldIndex(position)
        index = (x, y)
        if index == (None, None):
            return

        if isinstance(obj, Block):
            if str(index) in self.ground_sprite_dict:
                existing_block = self.ground_sprite_dict[str(index)]
                existing_block.kill()

            new_block = obj.copy()
            new_block.position = Vector2((x, y))
            self.ground_sprite_group.add(new_block)
            self.ground_sprite_dict.update({str(index): new_block})
# ------------------------------------------------------------------------ #

class Main:
    def __init__(self):
        self.editor = WorldEditor((16, 16))

    def handle_draw(self):
        camera.screen.fill('black')

        self.editor.draw_sprites()
        self.editor.draw_grid()
        camera.draw_panning_border()

        pygame.display.update()

    def run(self):
        # Start frame
        mouse_position = Vector2((camera.screen.get_size()[0] // 2, camera.screen.get_size()[1] // 2))

        # Update fame
        while True:
            for event in pygame.event.get():
                # Exit the game.
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # Start using the panning mouse.
                if event.type == pygame.MOUSEBUTTONDOWN:
                    camera.start_panning = mouse_position
                # Mouse scroll zoom
                if event.type == pygame.MOUSEWHEEL:
                    camera.mouse_scroll_y = event.y

            # TEST PLACE A BLOCK IN THE WORLD SPACE
            keys = pygame.key.get_pressed()
            if keys[pygame.K_b]:
                self.editor.paint(mouse_position, Grass)

            camera.movement(mouse_position)

            self.handle_draw()

            clock.tick(FPS)
            pygame.display.set_caption(f'{clock.get_fps():.2f}') # Display FPS
            mouse_position = Vector2(pygame.mouse.get_pos()) # Updating mouse position

if __name__ == '__main__':
    Main().run()