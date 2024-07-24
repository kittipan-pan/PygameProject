from Mindustry_clone.Scripts.Data.Setting import *
import pygame
import numpy as np
from pygame.math import Vector2
from pygame.sprite import Sprite, Group

pygame.init()

def WorldToScreenCoordinate(world_position: Vector2) -> Vector2:
    """
    Convert world space --> screen space.

    :param world_position: World position
    :return: Screen coordinate relatives to its offset and scaling.
    """
    screen_x = (world_position[0] - camera.offset.x) * camera.scale
    screen_y = (world_position[1] - camera.offset.y) * camera.scale
    return Vector2((int(screen_x), int(screen_y)))

def ScreenToWorldCoordinate(mouse_position: Vector2) -> Vector2:
    """
    Convert screen space --> world space.

    :param mouse_position: Mouse position
    :return: Original world coordinate.
    """
    world_x = mouse_position[0] / camera.scale + camera.offset.x
    world_y = mouse_position[1] / camera.scale + camera.offset.y
    return Vector2((int(world_x), int(world_y)))

class Camera:
    def __init__(self):
        self.screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE)
        self.offset: Vector2 = Vector2()
        self.scale: float = 1.0
        self.start_panning: Vector2 = Vector2()
        self.mouse_scroll_y: int = 0

        self.screen_update: bool = True

        l: int = CAMERA_PANNING_BORDER['left']
        t: int = CAMERA_PANNING_BORDER['top']
        w: int = self.screen.get_size()[0] - CAMERA_PANNING_BORDER['left'] - CAMERA_PANNING_BORDER['right']
        h: int = self.screen.get_size()[1] - CAMERA_PANNING_BORDER['top'] - CAMERA_PANNING_BORDER['bottom']
        self.__direction: Vector2 = Vector2()
        self.__camera_border: pygame.Rect = pygame.Rect(l, t, w, h)

    def movement(self, mouse_position: Vector2):
        """
        Camera screen panning and zoom. Self-update its offset and scale.
        :param mouse_position: Mouse position
        """
        # Mouse pressed panning
        mouses = pygame.mouse.get_pressed()
        if mouses[2]:
            self.offset += (self.start_panning - mouse_position) // self.scale
            self.start_panning = mouse_position
            self.screen_update = True

        # # Mouse border panning
        # if pygame.mouse.get_focused():
        #     if mouse_position.x < self.__camera_border.left:
        #         self.__direction.x = -1
        #     elif mouse_position.x > self.__camera_border.right:
        #         self.__direction.x = 1
        #     else:
        #
        #         self.__direction.x = 0
        #     if mouse_position.y < self.__camera_border.top:
        #         self.__direction.y = -1
        #     elif mouse_position.y > self.__camera_border.bottom:
        #         self.__direction.y = 1
        #     else:
        #         self.__direction.y = 0
        #     self.offset += self.__direction * MOUSE_PANNING_SPEED
        #     self.screen_update = True

        # Key pressed panning
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.__direction.x = -1
            self.screen_update = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.__direction.x = 1
            self.screen_update = True
        else:
            self.__direction.x = 0

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.__direction.y = -1
            self.screen_update = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.__direction.y = 1
            self.screen_update = True
        else:
            self.__direction.y = 0

        self.offset += self.__direction * KEY_PANNING_SPEED // self.scale

        before_zoom = ScreenToWorldCoordinate(mouse_position)
        # Mouse scroll zoom
        if self.mouse_scroll_y < 0:
            self.scale += 0.1 * MOUSE_ZOOM_SPEED
            self.screen_update = True
            if self.scale > ZOOM_MAX:
                self.scale = ZOOM_MAX
                self.screen_update = False
        elif self.mouse_scroll_y > 0:
            self.scale -= 0.1 * MOUSE_ZOOM_SPEED
            self.screen_update = True
            if self.scale < ZOOM_MIN:
                self.scale = ZOOM_MIN
                self.screen_update = False

        # Key zoom
        if keys[pygame.K_q] or keys[pygame.K_LEFTBRACKET]:
            self.scale += 0.1 * KEY_ZOOM_SPEED
            self.screen_update = True
            if self.scale > ZOOM_MAX:
                self.scale = ZOOM_MAX
                self.screen_update = False
        elif keys[pygame.K_e] or keys[pygame.K_RIGHTBRACKET]:
            self.scale -= 0.1 * KEY_ZOOM_SPEED
            self.screen_update = True
            if self.scale < ZOOM_MIN:
                self.scale = ZOOM_MIN
                self.screen_update = False
        after_zoom = ScreenToWorldCoordinate(mouse_position)
        self.offset += before_zoom - after_zoom

        self.mouse_scroll_y = 0 # Reset value

    def draw_panning_border(self):
        """
        Display mouse panning border.
        """
        pygame.draw.rect(self.screen, CAMERA_PANNING_BORDER_COLOR, self.__camera_border, 5)


class Block(Sprite):
    def __init__(self, image_source: FilePath = ""):
        super().__init__()
        self.image_source: str = image_source
        self.name: str = ""
        self.id: int = None

        if not len(self.image_source):
            self.original_image: pygame.Surface = pygame.image.load('Images/NOT_FOUND.png').convert_alpha()
        else:
            self.original_image: pygame.Surface = pygame.image.load(self.image_source).convert_alpha()

        self.image: pygame.Surface = self.original_image
        self.rect: pygame.Rect = self.image.get_rect()
        self.position: Vector2 = Vector2()

    def copy(self):
        """
        Return a new class Block that has the same variable data.

        :return: Self-copied block
        """
        cloned_block = Block(self.image_source)
        cloned_block.name = self.name
        cloned_block.id = self.id
        cloned_block.image = self.image.copy()
        cloned_block.rect = self.rect.copy()
        cloned_block.position = self.position
        return cloned_block

    def update(self):
        """
        Self-display image corresponds to the camera.
        """
        self.rect.topleft = WorldToScreenCoordinate(self.position)
        self.image = pygame.transform.scale(self.original_image, (PIXEL * camera.scale, PIXEL * camera.scale))


class Layer:
    def __init__(self, size: tuple[int, int]):
        self.indices: np.ndarray = np.zeros(size)
        self.sprite_group: Group[Block] = Group()
        self.sprite_dict: dict[tuple[int,int], Block] = {}

    def draw(self):
        """
        Draw sprites on the screen.
        """
        self.sprite_group.update()
        self.sprite_group.draw(camera.screen)

    def add(self, index: tuple[int, int], block: Block):
        """
        Update layer data; block id in 'self.indices',
        block sprite in 'self.sprite_group' and index in 'self.sprite_dict'.

        :param index: Index where to draw the block data
        :param block: Block
        """
        if block is None:
            return

        x, y = index
        # Return if the index is out of range.
        if (x < 0 or x > self.indices.shape[0] - 1) or (y < 0 or y > self.indices.shape[1] - 1):
            return

        # Return if it already has the same block in the index
        if self.indices[x][y] == block.id:
            return
        else:
            # Remove previous index data
            self.remove(index)

        new_block = block.copy()
        new_block.position = Vector2((x, y)) * PIXEL

        self.sprite_group.add(new_block)
        self.sprite_dict.update({index: new_block})
        self.indices[index[0]][index[1]] = new_block.id
        camera.screen_update = True
        # print(f'Successfully draw \'{block.name}\' in {index}')

    def remove(self, index):
        """
        Remove all data in the index.

        :param index: Current index to remove
        """
        if index in self.sprite_dict:
            existence_block = self.sprite_dict.pop(index)
            self.indices[index[0]][index[1]] = 0
            self.sprite_group.remove(existence_block)
            camera.screen_update = True

            # print(f'Successfully remove \'{existence_block.name}\' at {index}')


class WorldEditor:
    def __init__(self, world_size:tuple[int, int]):
        self.__world_size: tuple[int, int] = world_size
        self.__base_world_index: np.ndarray = np.zeros(world_size)

        self.background_layer: Layer = Layer(world_size)

    def GetCurrentWorldIndex(self, mouse_position: Vector2) -> (tuple[int, int] | tuple[None, None]):
        """
        Return to the world index where the mouse's position is at.

        :param mouse_position: Mouse position
        :return: Current world index
        """
        x, y = ScreenToWorldCoordinate(mouse_position) // PIXEL
        # Return None the index is out of world base index range.
        if (x < 0 or x > self.__base_world_index.shape[0] - 1) or (y < 0 or y > self.__base_world_index.shape[1] - 1):
            return None, None
        return int(x), int(y)

    def draw_grid(self):
        """
        Display world grid.
        """
        x_line = np.linspace(0, self.__world_size[0], self.__world_size[0] + 1)
        y_line = np.linspace(0, self.__world_size[1], self.__world_size[1] + 1)
        for x in x_line:
            pygame.draw.line(camera.screen, GRID_COLOR, WorldToScreenCoordinate((x * PIXEL, y_line[0]) * PIXEL),
                             WorldToScreenCoordinate((x * PIXEL, y_line[-1] * PIXEL)))
        for y in y_line:
            pygame.draw.line(camera.screen, GRID_COLOR, WorldToScreenCoordinate((x_line[0] * PIXEL, y* PIXEL)),
                             WorldToScreenCoordinate((x_line[-1] * PIXEL, y * PIXEL)))

    def draw_layer(self):
        """
        Display layer.
        """
        self.background_layer.draw()


camera = Camera()
world_editor = WorldEditor(WORLD_SIZE)