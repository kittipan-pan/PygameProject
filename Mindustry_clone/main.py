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
ZOOM_MIN: float = 0.2
MOUSE_ZOOM_SPEED: float = 1.0
KEY_ZOOM_SPEED: float = 0.2

# COLOR SETTING
GRID_COLOR: str = "WHITE"
CAMERA_PANNING_BORDER_COLOR: str = "YELLOW"

FPS: int = 60
pygame.init()
clock: pygame.time.Clock = pygame.time.Clock()

# ------------------------------------------------------------------------ #
#                                  CAMERA                                  #
# ------------------------------------------------------------------------ #
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

camera = Camera()
# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------ #
#                                 BLOCK                                    #
# ------------------------------------------------------------------------ #
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

Grass = Block('Images/Block_Images/Grass_001.png')
Grass.name = 'Grass'
Grass.id = 1

Rock = Block('Images/Block_Images/Rock_002.png')
Rock.name = 'Rock'
Rock.id = 2

Sand = Block('Images/Block_Images/Sand_003.png')
Sand.name = 'Sand'
Sand.id = 3

Water = Block('Images/Block_Images/Water_004.png')
Water.name = 'Water'
Water.id = 4
# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------ #
#                                 EDITOR                                   #
# ------------------------------------------------------------------------ #
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

class Button(Sprite):
    def __init__(self, size: tuple[int, int], position: tuple[int, int],
                 value = None, image_source: FilePath = ""):
        super().__init__()
        self.image_source: str = image_source
        if not len(self.image_source):
            self.original_image: pygame.Surface = pygame.image.load('Images/NOT_FOUND.png').convert_alpha()
        else:
            self.original_image: pygame.Surface = pygame.image.load(self.image_source).convert_alpha()

        self.size: tuple[int, int] = size
        self.position: Vector2 = Vector2(position)
        self.image = pygame.transform.scale(self.original_image, self.size)
        self.rect: pygame.Rect = self.image.get_rect(topleft=self.position)
        self.value = value

    def is_mouse_click(self) -> bool:
        """
        Check if mouse has clicked the button
        """
        return pygame.Rect.collidepoint(self.rect, pygame.mouse.get_pos())

    def update(self, offset: Vector2):
        """
        Self-display image relatives to the offset.

        :param offset: A relative offset, for example, menu offset or camera offset.
        """
        self.rect.topleft = self.position + offset


class Menu:
    def __init__(self, table: tuple[int, int], cell_size: int):
        self.button_group: Group = Group()
        self.button_dict: dict = {}

        i: int = 1
        for y in range(table[1]):
            for x in range(table[0]):
                button = Button((cell_size, cell_size), (x * cell_size, y * cell_size))
                self.button_group.add(button)
                self.button_dict.update({i: button})
                i += 1

        self.rect: pygame.Rect = pygame.Rect((0, 0), (table[0] * cell_size, table[1] * cell_size))
        self.visible: bool = True
        self.rect_visible: bool = True

        self.start_panning: Vector2 = Vector2()
        self.offset: Vector2 = Vector2()
        self.is_move_tab: bool = False

    def draw(self):
        """
        Display the image table of buttons.
        """
        if not self.visible:
            return

        self.button_group.update(self.offset)
        self.button_group.draw(camera.screen)

        self.rect.topleft = self.offset
        if self.rect_visible:
            pygame.draw.rect(camera.screen, 'RED', self.rect, 1)

    def toggle_tab(self):
        """
        Toggle menu.
        """
        self.visible = not self.visible
        camera.screen_update = True

    # def start_move_tab(self):
    #     if not self.visible:
    #         return
    #
    #     self.start_panning = pygame.mouse.get_pos()
    #     self.is_move_tab = True
    #
    # def clear_move_tab(self):
    #     if not self.visible:
    #         return
    #
    #     self.is_move_tab = False
    #
    # def move_tab(self, mouse_position):
    #     if not self.visible or not self.is_move_tab:
    #         return
    #
    #     mouses = pygame.mouse.get_pressed()
    #     if mouses[0]:
    #         self.offset -= self.start_panning - mouse_position
    #         self.start_panning = mouse_position
    #         camera.screen_update = True

    def _add_button_value(self, value_list: list):
        """
        Update each button value.

        :param value_list: List of value
        """
        if not isinstance(value_list, list):
            value_list = [value_list]

        if len(value_list) > len(self.button_dict):
            raise IndexError(f'The value_list has elements greater than the total button. \n'
                             f'The total amount of button values is {len(self.button_dict)}, but got \'{len(value_list)}\'.')

        button: Button
        for index, value in enumerate(value_list):
            button = self.button_dict[index+1]
            button.value = value

    def _add_button_image(self,image_source_list: list[FilePath]):
        """
        Update each button image source.

        :param image_source_list: List of image file path
        """
        if not isinstance(image_source_list, list):
            image_source_list = [image_source_list]

        if len(image_source_list) > len(self.button_dict):
            raise IndexError(f'The image_source_list has elements greater than the total button. \n'
                             f'The total amount of button values is {len(self.button_dict)}, but got \'{len(image_source_list)}\'.')

        button: Button
        for index, image_source in enumerate(image_source_list):
            if image_source == "":
                continue

            button = self.button_dict[index+1]
            button.image_source = image_source
            button.original_image = pygame.image.load(image_source).convert_alpha()
            button.image = pygame.transform.scale(button.original_image, button.size)

    def _get_current_button(self):
        """
        Return current button value.

        :return: Button value
        """
        if not self.visible:
            return

        button: Button
        for button in self.button_group:
            if button.is_mouse_click():
                return button.value


class Layer:
    def __init__(self, size: tuple[int, int]):
        self.indices: np.ndarray = np.zeros(size)
        self.sprite_group: Group = Group()
        self.sprite_dict: dict = {}

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


class BrushTool:
    def __init__(self):
        # Pen head lists
        pen1 = np.array([
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0],
        ])
        pen2 = np.array([
            [0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0],
            [0, 0, 1, 0, 0],
        ])
        pen3 = np.array([
            [0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0],
        ])
        pen4 = np.array([
            [0, 0, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 0, 0],
        ])
        pen5 = np.array([
            [0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 1, 1, 1, 0, 0, 0],
        ])
        pen6 = np.array([
            [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
        ])
        self.__pen_list = [pen1, pen2, pen3, pen4, pen5, pen6]
        self.__pen_head_size: int = 1

        self.brush_current: str = ""
        self.block_current: Block = None

        # Handle on-off the brush copy
        self.is_holding_copy_brush: bool = False

    @staticmethod
    def __bucket_fill(arr: np.ndarray, index: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Bucket filling algorithm.

        :param arr: An 2D array
        :param index: Target index
        :return: A list of the same index values of group indices
        """
        direction: list[tuple[int, int]] = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        col: int = arr.shape[0]
        row: int = arr.shape[1]

        value = arr[index[0]][index[1]]

        is_stop: bool = False
        group: list = [index]

        visited_group: list = [index]
        while not is_stop:
            is_stop = True
            new_visited_group: list = []
            for current_index in visited_group:
                X, Y = current_index
                for dx, dy in direction:
                    x, y = X + dx, Y + dy
                    if not 0 <= x < col or not 0 <= y < row:
                        continue
                    if arr[x][y] == value:
                        if (x, y) in group:
                            continue

                        new_visited_group.append((x, y))
                        group.append((x, y))
                        is_stop = False

            visited_group = new_visited_group
        return group

    def __get_pen_index_area(self, index: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Return a list of indices area corresponds to its current pen size.
        This method will automatically remove negative indices and keep only positive.

        :param index: An index where it will be the center of pen size
        :return: An area of the list of indices where the pen brush has filled
        """
        if self.__pen_head_size == 1:
            return [index]

        __pen_head_size = self.__pen_list[self.__pen_head_size - 2]
        index_list = []
        for x in range(__pen_head_size.shape[0]):
            for y in range(__pen_head_size.shape[1]):
                if __pen_head_size[x][y]:
                    i = (y - __pen_head_size.shape[0] // 2 + index[0], x - __pen_head_size.shape[1] // 2 + index[1])
                    if i[0] < 0 or i[1] < 0:
                        continue
                    index_list.append(i)
        return index_list

    def __pen_draw(self, layer: Layer, mouse_position: Vector2):
        """
        Draw block on the layer.

        :param layer: Current layer
        :param mouse_position: Mouse position
        """
        index = world_editor.GetCurrentWorldIndex(mouse_position)
        if index == (None, None):
            return

        indices = self.__get_pen_index_area(index)
        if self.block_current is None:
            for i in indices:
                layer.remove(i)
        else:
            for i in indices:
                layer.add(i, self.block_current)

    def __pen_erase(self, layer: Layer, mouse_position: Vector2):
        """
        Remove data on the layer.

        :param layer: Current layer
        :param mouse_position: Mouse position
        """
        index = world_editor.GetCurrentWorldIndex(mouse_position)
        if index == (None, None):
            return

        indices = self.__get_pen_index_area(index)
        for i in indices:
            layer.remove(i)

    def change_pen_head_size(self, event: pygame.event):
        """
        Hotkeys change pen head size. Change 'pen' and 'erase' brush size.
        """
        if not self.brush_current in ['pen', 'erase']:
            return

        if event.key == pygame.K_1:
            self.__pen_head_size = 1
        elif event.key == pygame.K_2:
            self.__pen_head_size = 2
        elif event.key == pygame.K_3:
            self.__pen_head_size = 3
        elif event.key == pygame.K_4:
            self.__pen_head_size = 4
        elif event.key == pygame.K_5:
            self.__pen_head_size = 5
        elif event.key == pygame.K_6:
            self.__pen_head_size = 6
        elif event.key == pygame.K_7:
            self.__pen_head_size = 7

        print(f'Pen head size: {self.__pen_head_size}')

    def __fill(self, layer: Layer, mouse_position: Vector2):
        """
        Bucket filling area on the layer.

        :param layer: Current layer
        :param mouse_position: Mouse position
        """
        index = world_editor.GetCurrentWorldIndex(mouse_position)
        if index == (None, None):
            return

        indices = self.__bucket_fill(layer.indices, index)
        if self.block_current is None:
            for i in indices:
                layer.remove(i)
        else:
            for i in indices:
                layer.add(i, self.block_current)

    def __copy_block(self, layer: Layer, mouse_position: Vector2):
        """
        Copying the current index block on the layer.

        :param layer: Current layer
        :param mouse_position: Mouse position
        """
        index = world_editor.GetCurrentWorldIndex(mouse_position)
        if index == (None, None):
            return

        if layer.indices[index[0]][index[1]] == 0:
            brush_tool.block_current = None
            print('Copied \'None\'')
        else:
            # Copy current block data
            block = layer.sprite_dict[index]
            self.block_current = block
            print(f'Copied \'{block.name}\'')

        print(f'Change brush: \'pen\'')
        self.is_holding_copy_brush = False

    def __change_brush_type(self):
        """
        Change brush 'copy' -> 'pen' after copied the block.
        """
        if not self.is_holding_copy_brush:
            self.brush_current = 'pen'

    def paint(self, layer: Layer, mouse_position: Vector2):
        """
        Paint block on the layer corresponds to brush type.

        :param layer: Current layer
        :param mouse_position: Mouse position
        """
        mouses = pygame.mouse.get_pressed()
        if mouses[0]:
            if self.brush_current == 'pen':
                self.__pen_draw(layer, mouse_position)
            elif self.brush_current == 'erase':
                self.__pen_erase(layer, mouse_position)
            elif self.brush_current == 'fill':
                self.__fill(layer, mouse_position)
            elif self.brush_current == 'copy':
                if self.is_holding_copy_brush:
                    self.__copy_block(layer, mouse_position)
        else:
            if self.brush_current == 'copy':
                self.__change_brush_type()


class BrushMenu(Menu):
    def __init__(self):
        super().__init__((1, 4), 50)
        self._add_button_value(['pen', 'erase', 'fill', 'copy'])
        self._add_button_image(['Images/Interfaces/brush_interface/pen.png',
                               'Images/Interfaces/brush_interface/erase.png',
                               'Images/Interfaces/brush_interface/fill.png',
                               'Images/Interfaces/brush_interface/copy.png'
                               ])

    def brush_select(self):
        """
        Select brush type on the brush menu.

        This method automatically updates the 'brush.current' in the BrushTool.
        """
        brush_select = self._get_current_button()
        if brush_select is None:
            return

        if brush_tool.brush_current == brush_select:
            brush_tool.brush_current = ""
            brush_tool.is_holding_copy_brush = False
            print(f'Cancel \'{brush_select}\'')
        else:
            brush_tool.brush_current = brush_select
            print(f'Brush: {brush_select}')

        if brush_select == 'copy':
            brush_tool.is_holding_copy_brush = True


class BlockMenu(Menu):
    def __init__(self):
        super().__init__((4, 1), 25)
        self.offset = Vector2((700, 0))

        block_list = [
            Grass, Rock, Sand, Water,
        ]

        self._add_button_value(block_list)
        self._add_button_image([block.image_source for block in block_list])

    def block_select(self):
        """
        Select a block on the block menu.

        This method automatically updates the 'block.current' in the BrushTool.
        """
        block_select = self._get_current_button()

        if block_select is None:
            return

        # Check if 'block_current' has a block
        if isinstance(brush_tool.block_current, Block):
            if brush_tool.block_current.name == block_select.name:
                brush_tool.block_current = None
                print(f'Canceled block \'{block_select.name}\'')
            else:
                brush_tool.block_current = block_select
                print(f'Block selected : {block_select.name}')
            return

        # If 'block_current' is None, update the variable
        brush_tool.block_current = block_select
        print(f'Block selected : {block_select.name}')

world_editor = WorldEditor((32, 32))
brush_tool = BrushTool()

# Menu Tabs
brush_menu = BrushMenu()
block_menu = BlockMenu()

def mouse_on_menu_tabs(mouse_position: Vector2) -> bool:
    menus: list[Menu] = [brush_menu, block_menu]

    menu: Menu
    for menu in menus:
        if not menu.visible:
            continue
        if pygame.Rect.collidepoint(menu.rect, mouse_position):
            return False
    return True
# ------------------------------------------------------------------------ #
class Main:
    def __init__(self):
        ...

    def handle_event(self, mouse_position):
        for event in pygame.event.get():
            # Exit the game.
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # MOUSE DOWN
            # Start using the panning mouse.
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    brush_menu.brush_select()
                    block_menu.block_select()
                if event.button == 3:  # Right click
                    camera.start_panning = mouse_position

            # Mouse scroll zoom
            if event.type == pygame.MOUSEWHEEL:
                camera.mouse_scroll_y = event.y

            # KEY DOWN
            if event.type == pygame.KEYDOWN:
                # Change 'pen' and 'erase' brush size
                brush_tool.change_pen_head_size(event)

                # Toggle brush menu
                if event.key == pygame.K_b:
                    brush_menu.toggle_tab()
                    block_menu.toggle_tab()

        camera.movement(mouse_position)

        if mouse_on_menu_tabs(mouse_position):
            brush_tool.paint(world_editor.background_layer, mouse_position)

    def handle_draw(self):
        if camera.screen_update:
            camera.screen.fill('black')
            world_editor.draw_layer()
            world_editor.draw_grid()

            brush_menu.draw()
            block_menu.draw()

            camera.draw_panning_border()

            pygame.display.update()

        camera.screen_update = False

    def run(self):
        # Start frame
        # Avoid move camera offset
        mouse_position = Vector2((camera.screen.get_size()[0] // 2, camera.screen.get_size()[1] // 2))

        # Update frame
        while True:
            self.handle_event(mouse_position)
            self.handle_draw()

            clock.tick(FPS)
            pygame.display.set_caption(f'{clock.get_fps():.2f}') # Display FPS
            mouse_position = Vector2(pygame.mouse.get_pos()) # Updating mouse position

if __name__ == '__main__':
    Main().run()