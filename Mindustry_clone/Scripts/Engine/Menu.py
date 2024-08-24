from Scripts.BrushTool.BrushSetting import *

class Button(pygame.sprite.Sprite):
    def __init__(self, size: tuple[int, int], position: tuple[int, int],
                 value = None, image_source: FilePath = ""):
        super().__init__()
        self.image_source: str = image_source
        if not len(self.image_source):
            self.original_image: pygame.Surface = pygame.image.load('Images/NOT_FOUND.png').convert_alpha()
        else:
            self.original_image: pygame.Surface = pygame.image.load(self.image_source).convert_alpha()

        self.size: tuple[int, int] = size
        self.position: pygame.math.Vector2 = pygame.math.Vector2(position)
        self.image = pygame.transform.scale(self.original_image, self.size)
        self.rect: pygame.Rect = self.image.get_rect(topleft=self.position)
        self.value = value

    def is_mouse_click(self) -> bool:
        """
        Check if mouse has clicked the button
        """
        return pygame.Rect.collidepoint(self.rect, pygame.mouse.get_pos())

    def update(self, offset: pygame.math.Vector2):
        """
        Self-display image relatives to the offset.

        :param offset: A relative offset, for example, menu offset or camera offset.
        """
        self.rect.topleft = self.position + offset

class Menu:
    def __init__(self, table: tuple[int, int], cell_size: int):
        self.button_group: pygame.sprite.Group[Button] = pygame.sprite.Group()
        self.button_index_dict: dict[int, Button] = {}

        i: int = 1
        for y in range(table[1]):
            for x in range(table[0]):
                button = Button((cell_size, cell_size), (x * cell_size, y * cell_size))
                self.button_group.add(button)
                self.button_index_dict.update({i: button})
                i += 1

        self.rect: pygame.Rect = pygame.Rect((0, 0), (table[0] * cell_size, table[1] * cell_size))
        self.visible: bool = True
        self.rect_visible: bool = True

        self.start_panning: pygame.math.Vector2 = pygame.math.Vector2()
        self.offset: pygame.math.Vector2 = pygame.math.Vector2()
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

        if len(value_list) > len(self.button_index_dict):
            raise IndexError(f'The value_list has elements greater than the total button. \n'
                             f'The total amount of button values is {len(self.button_index_dict)}, but got \'{len(value_list)}\'.')

        button: Button
        for index, value in enumerate(value_list):
            button = self.button_index_dict[index+1]
            button.value = value

    def _add_button_image(self,image_source_list: list[FilePath]):
        """
        Update each button image source.

        :param image_source_list: List of image file path
        """
        if not isinstance(image_source_list, list):
            image_source_list = [image_source_list]

        if len(image_source_list) > len(self.button_index_dict):
            raise IndexError(f'The image_source_list has elements greater than the total button. \n'
                             f'The total amount of button values is {len(self.button_index_dict)}, but got \'{len(image_source_list)}\'.')

        button: Button
        image_source: PathLike
        for index, image_source in enumerate(image_source_list):
            if image_source == "":
                continue

            button = self.button_index_dict[index+1]
            button.image_source = image_source
            button.original_image = pygame.image.load(image_source).convert_alpha()
            button.image = pygame.transform.scale(button.original_image, button.size)

    def _get_current_button(self) -> (Button | None):
        """
        Return current button.

        :return: Button
        """
        if not self.visible:
            return

        for button in self.button_group:
            if button.is_mouse_click():
                return button


class BrushMenu(Menu):
    def __init__(self):
        super().__init__((1, 4), 50)
        self._add_button_value(['pen', 'erase', 'fill', 'copy'])
        self._add_button_image(['Images/Interfaces/brush_interface/pen.png',
                               'Images/Interfaces/brush_interface/erase.png',
                               'Images/Interfaces/brush_interface/fill.png',
                               'Images/Interfaces/brush_interface/copy.png'
                               ])

        self.brush_rect_dict: dict[str, pygame.Rect] = {"": pygame.Rect((0,0,0,0))}
        for button in self.button_group:
            brush: str = button.value
            self.brush_rect_dict.update({brush: button.rect})

    def brush_select(self):
        """
        Select brush type on the brush menu.

        This method automatically updates the 'brush.current' in the BrushTool.
        """
        button = self._get_current_button()
        if button is None:
            return

        brush_select = button.value
        if brush_select is None:
            return

        if brush_tool.brush_current == brush_select:
            brush_tool.brush_current = ""
            brush_tool.is_holding_copy_brush = False
            camera.screen_update = True

            debug.event_update(f'Cancel \'{brush_select}\'')
        else:
            brush_tool.brush_current = brush_select
            camera.screen_update = True

            debug.event_update(f'Brush: {brush_select}')

        if brush_select == 'copy':
            brush_tool.is_holding_copy_brush = True

    def custom_draw(self):
        self.draw()

        selected_brush_button_rect = self.brush_rect_dict[brush_tool.brush_current]
        pygame.draw.rect(camera.screen, BUTTON_SELECTED_COLOR, selected_brush_button_rect, BUTTON_SELECTED_COLOR_THICKNESS)


class BlockMenu(Menu):
    def __init__(self):
        super().__init__((4, 1), 25)
        block_list = [block for block in block_dict.values()]
        self.offset = pygame.math.Vector2((700, 0))
        self._add_button_value(block_list)
        self._add_button_image([block.image_source for block in block_list])

        self.block_rect_dict: dict[str, pygame.Rect] = {}
        for button in self.button_group:
            block: Block = button.value
            self.block_rect_dict.update({block.name: button.rect})

    def block_select(self):
        """
        Select a block on the block menu.

        This method automatically updates the 'block.current' in the BrushTool.
        """
        button = self._get_current_button()
        if button is None:
            return

        block_select = button.value
        if block_select is None:
            return

        # Check if 'block_current' has a block
        if isinstance(brush_tool.block_current, Block):
            if brush_tool.block_current.name == block_select.name:
                brush_tool.block_current = None
                camera.screen_update = True
                debug.event_update(f'Canceled block \'{block_select.name}\'')
            else:
                brush_tool.block_current = block_select
                camera.screen_update = True
                debug.event_update(f'Block selected : {block_select.name}')
            return

        # If 'block_current' is None, update the variable
        brush_tool.block_current = block_select
        camera.screen_update = True
        debug.event_update(f'Block selected : {block_select.name}')

    def custom_draw(self):
        self.draw()

        if isinstance(brush_tool.block_current, Block):
            selected_block_button_rect = self.block_rect_dict[brush_tool.block_current.name]
        else:
            selected_block_button_rect = pygame.Rect((0, 0), (0, 0))
        pygame.draw.rect(camera.screen, BUTTON_SELECTED_COLOR, selected_block_button_rect, BUTTON_SELECTED_COLOR_THICKNESS // 2)

# Menu Tabs
brush_menu = BrushMenu()
block_menu = BlockMenu()

def mouse_on_menu_tabs(mouse_position: pygame.math.Vector2) -> bool:
    menus: list[Menu] = [brush_menu, block_menu]

    menu: Menu
    for menu in menus:
        if not menu.visible:
            continue
        if pygame.Rect.collidepoint(menu.rect, mouse_position):
            return True
    return False