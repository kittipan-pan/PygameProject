from Scripts.Engine.Editor import *

def _bucket_fill(arr: np.ndarray, index: tuple[int, int]) -> list[tuple[int, int]]:
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

class BrushTool:
    def __init__(self):
        self.__pen_list = [pen1, pen2, pen3, pen4, pen5, pen6]
        self.__pen_head_size: int = 1

        self.brush_current: str = ""
        self.block_current: [Block | None] = None

        # Handle on-off the brush copy
        self.is_holding_copy_brush: bool = False

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

    def __pen_draw(self, layer: Layer, mouse_position: pygame.math.Vector2):
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

    def __pen_erase(self, layer: Layer, mouse_position: pygame.math.Vector2):
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
            debug.event_update(f'Pen head size: {self.__pen_head_size}')
        elif event.key == pygame.K_2:
            self.__pen_head_size = 2
            debug.event_update(f'Pen head size: {self.__pen_head_size}')
        elif event.key == pygame.K_3:
            self.__pen_head_size = 3
            debug.event_update(f'Pen head size: {self.__pen_head_size}')
        elif event.key == pygame.K_4:
            self.__pen_head_size = 4
            debug.event_update(f'Pen head size: {self.__pen_head_size}')
        elif event.key == pygame.K_5:
            self.__pen_head_size = 5
            debug.event_update(f'Pen head size: {self.__pen_head_size}')
        elif event.key == pygame.K_6:
            self.__pen_head_size = 6
            debug.event_update(f'Pen head size: {self.__pen_head_size}')
        elif event.key == pygame.K_7:
            self.__pen_head_size = 7
            debug.event_update(f'Pen head size: {self.__pen_head_size}')

    def __fill(self, layer: Layer, mouse_position: pygame.math.Vector2):
        """
        Bucket filling area on the layer.

        :param layer: Current layer
        :param mouse_position: Mouse position
        """
        index = world_editor.GetCurrentWorldIndex(mouse_position)
        if index == (None, None):
            return

        indices = _bucket_fill(layer.index_position, index)
        if self.block_current is None:
            for i in indices:
                layer.remove(i)
        else:
            for i in indices:
                layer.add(i, self.block_current)

    def __copy_block(self, layer: Layer, mouse_position: pygame.math.Vector2):
        """
        Copying the current index block on the layer.

        :param layer: Current layer
        :param mouse_position: Mouse position
        """
        index = world_editor.GetCurrentWorldIndex(mouse_position)
        if index == (None, None):
            return

        if layer.index_position[index[0]][index[1]] == 0:
            self.block_current = None
            debug.event_update('Copied \'None\'')
        else:
            # Copy current block data
            block = layer.sprite_dict[index]
            self.block_current = block
            debug.event_update(f'Copied \'{block.name}\'')

        debug.event_update(f'Change brush: \'pen\'')
        self.is_holding_copy_brush = False

    def __change_brush_type(self):
        """
        Change brush 'copy' -> 'pen' after copied the block.
        """
        if not self.is_holding_copy_brush:
            self.brush_current = 'pen'
            camera.screen_update = True

    def paint(self, layer: Layer, mouse_position: pygame.math.Vector2):
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

brush_tool = BrushTool()