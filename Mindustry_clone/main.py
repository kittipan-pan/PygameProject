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

pygame.init()
FPS: int = 60
clock = pygame.time.Clock()

# ------------------------------------------------------------------------ #
#                                  CAMERA                                  #
# ------------------------------------------------------------------------ #
class Camera:
    def __init__(self):
        # Public variables
        self.screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE)
        self.offset: Vector2 = Vector2()
        self.scale: float = 1.0
        self.start_panning: Vector2 = Vector2()
        self.mouse_scroll_y: int = 0

        self.need_update:bool = True
        self.screen_update: bool = False
        self.is_moving: bool = False

        # Private variables
        l: int = CAMERA_PANNING_BORDER['left']
        t: int = CAMERA_PANNING_BORDER['top']
        w: int = self.screen.get_size()[0] - CAMERA_PANNING_BORDER['left'] - CAMERA_PANNING_BORDER['right']
        h: int = self.screen.get_size()[1] - CAMERA_PANNING_BORDER['top'] - CAMERA_PANNING_BORDER['bottom']
        self.__direction: Vector2 = Vector2()
        self.__camera_border: pygame.Rect = pygame.Rect(l, t, w, h)

    def movement(self, mouse_position: Vector2):
        self.is_moving = False

        # Mouse pressed panning
        mouses = pygame.mouse.get_pressed()
        if mouses[2]:
            self.offset += (self.start_panning - mouse_position) // self.scale
            self.start_panning = mouse_position
            self.is_moving = True

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
        #     self.is_moving = True

        # Key pressed panning
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.__direction.x = -1
            self.is_moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.__direction.x = 1
            self.is_moving = True
        else:
            self.__direction.x = 0

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.__direction.y = -1
            self.is_moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.__direction.y = 1
            self.is_moving = True
        else:
            self.__direction.y = 0

        self.offset += self.__direction * KEY_PANNING_SPEED // self.scale

        before_zoom = ScreenToWorldCoordinate(mouse_position)
        # Mouse scroll zoom
        if self.mouse_scroll_y < 0:
            self.scale += 0.1 * MOUSE_ZOOM_SPEED
            self.is_moving = True
            if self.scale > ZOOM_MAX:
                self.scale = ZOOM_MAX
                self.is_moving = False
        elif self.mouse_scroll_y > 0:
            self.scale -= 0.1 * MOUSE_ZOOM_SPEED
            self.is_moving = True
            if self.scale < ZOOM_MIN:
                self.scale = ZOOM_MIN
                self.is_moving = False

        # Key zoom
        if keys[pygame.K_q] or keys[pygame.K_LEFTBRACKET]:
            self.scale += 0.1 * KEY_ZOOM_SPEED
            self.is_moving = True
            if self.scale > ZOOM_MAX:
                self.scale = ZOOM_MAX
                self.is_moving = False
        elif keys[pygame.K_e] or keys[pygame.K_RIGHTBRACKET]:
            self.scale -= 0.1 * KEY_ZOOM_SPEED
            self.is_moving = True
            if self.scale < ZOOM_MIN:
                self.scale = ZOOM_MIN
                self.is_moving = False

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
        self.rect.topleft = WorldToScreenCoordinate(self.position)
        self.image = pygame.transform.scale(self.original_image, (PIXEL * camera.scale, PIXEL * camera.scale))

Grass = Block('Images/Block_Images/Grass_001.png')
Grass.name = 'Grass'
Grass.id = 1
# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------ #
#                                 EDITOR                                   #
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

class Button(Sprite):
    def __init__(self, size:tuple[int, int], pos:tuple[int, int], value = None):
        super().__init__()
        self.size: tuple[int, int] = size
        self.image: pygame.Surface = pygame.Surface(size)
        self.image.fill('WHITE')
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)
        self.value = value

    def is_click(self):
        if pygame.Rect.collidepoint(self.rect, pygame.mouse.get_pos()):
            return True
        else:
            return False

class WorldEditor:
    def __init__(self, world_size:tuple[int, int]):
        self.world_size: tuple[int, int] = world_size
        self.__base_world_index: np.ndarray = np.zeros(world_size)

        self.background_sprite_group: Group = Group()
        self.background_sprite_dict: dict = {}

    def GetCurrentWorldIndex(self, position) -> (tuple[int, int] | tuple[None, None]):
        x, y = ScreenToWorldCoordinate(position) // PIXEL
        # Return None if the index is out of range of the grid_indices
        if (x < 0 or x > self.__base_world_index.shape[0] - 1) or (y < 0 or y > self.__base_world_index.shape[1] - 1):
            return None, None
        return int(x), int(y)

    def paint_block(self, index, obj: Block):
        x, y = index

        # Return if the index is out of range of the grid_indices
        if (x < 0 or x > self.__base_world_index.shape[0] - 1) or (y < 0 or y > self.__base_world_index.shape[1] - 1):
            return

        if str(index) in self.background_sprite_dict:
            existing_block = self.background_sprite_dict[str(index)]
            existing_block.kill()

        new_block = obj.copy()
        new_block.position = Vector2((x, y)) * PIXEL
        self.background_sprite_group.add(new_block)
        self.background_sprite_dict.update({str(index): new_block})

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
        self.background_sprite_group.update()
        self.background_sprite_group.draw(camera.screen)

class BrushTool:
    def __init__(self):
        self.brush_current: str = ""

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

        self.pen_list = [pen1, pen2, pen3, pen4, pen5, pen6]
        self.current_pen_size: int = 1

    def __pen_draw(self, mouse_position, obj:Block):
        index_center = world_editor.GetCurrentWorldIndex(mouse_position)

        if index_center == (None, None):
            return

        if self.current_pen_size == 1:
            world_editor.paint_block(index_center, obj)
            return

        fill_area = self.pen_list[self.current_pen_size - 2]

        index_list = []
        for x in range(fill_area.shape[0]):
            for y in range(fill_area.shape[1]):
                if fill_area[x][y]:
                    index = (y - fill_area.shape[0] // 2 + index_center[0], x - fill_area.shape[1] // 2 + index_center[1])
                    index_list.append(index)

        for i in index_list:
            world_editor.paint_block(i, obj)

    def __pen_erase(self, mouse_position):
        index_center = world_editor.GetCurrentWorldIndex(mouse_position)

        if index_center == (None, None):
            return

        if self.current_pen_size == 1:
            if str(index_center) in world_editor.background_sprite_dict:
                world_editor.background_sprite_dict[str(index_center)].kill()
                return

        fill_area = self.pen_list[self.current_pen_size - 2]

        index_list = []
        for x in range(fill_area.shape[0]):
            for y in range(fill_area.shape[1]):
                if fill_area[x][y]:
                    index = (
                    y - fill_area.shape[0] // 2 + index_center[0], x - fill_area.shape[1] // 2 + index_center[1])
                    index_list.append(index)

        for i in index_list:
            if str(i) in world_editor.background_sprite_dict:
                world_editor.background_sprite_dict[str(i)].kill()

    def change_pen_size(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            self.current_pen_size = 1
        elif keys[pygame.K_2]:
            self.current_pen_size = 2
        elif keys[pygame.K_3]:
            self.current_pen_size = 3
        elif keys[pygame.K_4]:
            self.current_pen_size = 4
        elif keys[pygame.K_5]:
            self.current_pen_size = 5
        elif keys[pygame.K_6]:
            self.current_pen_size = 6
        elif keys[pygame.K_7]:
            self.current_pen_size = 7

    def draw(self, mouse_position , obj:Block):
        mouses = pygame.mouse.get_pressed()
        if mouses[0]:
            if self.brush_current == 'pen':
                self.__pen_draw(mouse_position, obj)
                camera.screen_update = True
            elif self.brush_current == 'erase':
                self.__pen_erase(mouse_position)
                camera.screen_update = True

        if self.brush_current in ['pen', 'erase']:
            self.change_pen_size()

class BrushMenu:
    def __init__(self):
        super().__init__()
        brush_type_button1 = Button((50, 50), (0, 0), 'pen')
        brush_type_button2 = Button((50, 50), (0, 50), 'erase')
        brush_type_button3 = Button((50, 50), (0, 100), 'fill')
        brush_type_button4 = Button((50, 50), (0, 150), 'copy')
        self.brush_type_group = Group(brush_type_button1,
                                      brush_type_button2,
                                      brush_type_button3,
                                      brush_type_button4)

        self.rect: pygame.Rect = pygame.Rect((0, 0), (50, 200))
        self.visible: bool = False

    def draw(self):
        if self.visible:
            self.brush_type_group.draw(camera.screen)

            pygame.draw.rect(camera.screen, 'RED', self.rect, 1)

    def get_current_brush(self):
        brush: Button
        for brush in self.brush_type_group:
            if brush.is_click():
                return brush.value

        return ""

world_editor = WorldEditor((64, 64))
brush_tool = BrushTool()
brush_menu = BrushMenu()
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
                    # Brush select
                    if brush_menu.visible:
                        new_brush = brush_menu.get_current_brush()
                        if not (new_brush == ""):
                            # if pick the same brush, cancel.
                            if new_brush == brush_tool.brush_current:
                                brush_tool.brush_current = ""
                                print(f'cancel \'{new_brush}\'')
                            else:
                                brush_tool.brush_current = new_brush
                                print(f'brush: {new_brush}')

                if event.button == 3:  # Right click
                    camera.start_panning = mouse_position

            # Mouse scroll zoom
            if event.type == pygame.MOUSEWHEEL:
                camera.mouse_scroll_y = event.y

            # KEY DOWN
            # Toggle brush menu
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    brush_menu.visible = not brush_menu.visible
                    camera.screen_update = True

        camera.movement(mouse_position)

        if not pygame.Rect.collidepoint(brush_menu.rect, mouse_position):
            brush_tool.draw(mouse_position, Grass)

    def handle_draw(self):
        if camera.is_moving or camera.screen_update:
            camera.need_update = True

        if camera.need_update:
            camera.screen.fill('black')
            world_editor.draw_sprites()
            world_editor.draw_grid()
            brush_menu.draw()
            camera.draw_panning_border()

            pygame.display.update()

        camera.need_update = False
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