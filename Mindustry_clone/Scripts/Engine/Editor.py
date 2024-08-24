from Scripts.Setting.BlockSetting import *
import numpy as np
import pandas as pd

class Layer:
    def __init__(self, size: tuple[int, int]):
        self.index_position: np.ndarray = np.zeros(size)
        self.sprite_group: pygame.sprite.Group[Block] = pygame.sprite.Group()
        self.sprite_dict: dict[tuple[int,int], Block] = {}

    def draw(self):
        """
        Draw sprites on the screen.
        """
        self.sprite_group.update()
        self.custom_draw()

    def custom_draw(self):
        block: Block
        for block in self.sprite_group:
            if not block.visible:
                continue
            block.image = pygame.transform.scale(block.original_image, (PIXEL * camera.scale, PIXEL * camera.scale))
            camera.screen.blit(block.image, block.rect)


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
        if (x < 0 or x > self.index_position.shape[0] - 1) or (y < 0 or y > self.index_position.shape[1] - 1):
            return

        # Return if it already has the same block in the index
        if self.index_position[x][y] == block.id:
            return
        else:
            # Remove previous index data
            self.remove(index)

        new_block = block.copy()
        new_block.position = pygame.math.Vector2((x, y)) * PIXEL

        self.sprite_group.add(new_block)
        self.sprite_dict.update({index: new_block})
        self.index_position[index[0]][index[1]] = new_block.id
        camera.screen_update = True

    def remove(self, index):
        """
        Remove all data in the index.

        :param index: Current index to remove
        """
        if index in self.sprite_dict:
            existence_block = self.sprite_dict.pop(index)
            self.index_position[index[0]][index[1]] = 0
            self.sprite_group.remove(existence_block)
            camera.screen_update = True

    def load(self, file_path: FilePath):
        data = np.genfromtxt(file_path, delimiter = ',', skip_header = 1)[:, 1:]

        if not data.shape == self.index_position.shape:
            raise IndexError(f'World size \'{data.shape}\' does not match current layer {self.index_position.shape}!')

        for x in range(data.shape[0]):
            for y in range(data.shape[1]):
                data_index_current = data[x][y]
                if data_index_current == 0:
                    continue

                index = (x, y)
                block = block_dict[data_index_current].copy()
                block.position = pygame.math.Vector2(index) * PIXEL
                self.index_position[x][y] = block.id
                self.sprite_group.add(block)
                self.sprite_dict.update({index: block})


class WorldEditor:
    def __init__(self, world_size:tuple[int, int]):
        self.__world_size: tuple[int, int] = world_size
        self.__base_world_index: np.ndarray = np.zeros(world_size).astype(np.int8)
        self.rect: pygame.Rect = pygame.Rect((0, 0), (world_size[0] * PIXEL, world_size[1] * PIXEL))
        self.background_layer: Layer = Layer(world_size)

        self.grid_visible: bool = True
        self.rect_visible: bool = True

    def GetCurrentWorldIndex(self, mouse_position: pygame.math.Vector2) -> (tuple[int, int] | tuple[None, None]):
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

    def __draw_grid(self):
        """
        Display world grid.
        """
        if not self.grid_visible:
            return

        x_line = list(np.linspace(0, self.__world_size[0], self.__world_size[0] + 1))
        y_line = list(np.linspace(0, self.__world_size[1], self.__world_size[1] + 1))
        for x in x_line:
            pygame.draw.line(camera.screen, WORLD_GRID_COLOR, WorldToScreenCoordinate((x * PIXEL, y_line[0] * PIXEL)),
                             WorldToScreenCoordinate((x * PIXEL, y_line[-1] * PIXEL)))
        for y in y_line:
            pygame.draw.line(camera.screen, WORLD_GRID_COLOR, WorldToScreenCoordinate((x_line[0] * PIXEL, y * PIXEL)),
                             WorldToScreenCoordinate((x_line[-1] * PIXEL, y * PIXEL)))

    def __draw_rect(self):
        if not self.rect_visible:
            return

        pygame.draw.rect(camera.screen, "YELLOW", self.rect, 4)

    def __draw_terrain_layer(self):
        """
        Draw terrain layers.
        """
        self.background_layer.draw()

    def draw(self):
        camera.screen.fill((0, 0, 0))
        self.__draw_terrain_layer()
        self.__draw_grid()
        self.__draw_rect()

    def key_input(self, event: pygame.event.Event):
        if event.key == pygame.K_g:
            self.grid_visible = not self.grid_visible
            camera.screen_update = True
        elif event.key == pygame.K_m:
            self.rect_visible = not self.rect_visible
            camera.screen_update = True

    def update(self):
        self.rect.topleft = WorldToScreenCoordinate((0, 0))
        self.rect.w = self.__world_size[0] * PIXEL * camera.scale
        self.rect.h = self.__world_size[1] * PIXEL * camera.scale

    def save(self):
        data: np.ndarray = self.background_layer.index_position.astype(np.int8)
        DF = pd.DataFrame(data)
        DF.to_csv('Data/Save/world_editor_save1.csv')

        print('Successfully saved.')

    def load(self, file_path: FilePath):
        self.background_layer.load(file_path)


class DebuggingTool:
    def __init__(self):
        self.text: str = ""

    def event_update(self, event):
        self.text = str(event)

    def log(self):
        text_surface = font.render(self.text, False, DEBUG_LOG_FONT_STYLE_COLOR)
        text_rect = text_surface.get_rect(center=(SCREEN_SIZE[0] // 2,SCREEN_SIZE[1] // 1.5))
        camera.screen.blit(text_surface, text_rect)

debug = DebuggingTool()
world_editor = WorldEditor(WORLD_SIZE)