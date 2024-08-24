from Scripts.Setting.GameSetting import *

def WorldToScreenCoordinate(world_position: pygame.math.Vector2 | tuple[int, int]) -> pygame.math.Vector2:
    """
    Convert world space --> screen space.

    :param world_position: World position
    :return: Screen coordinate relatives to its offset and scaling.
    """
    screen_x = (world_position[0] - camera.offset.x) * camera.scale
    screen_y = (world_position[1] - camera.offset.y) * camera.scale
    return pygame.math.Vector2((int(screen_x), int(screen_y)))

def ScreenToWorldCoordinate(mouse_position: pygame.math.Vector2 | tuple[int, int]) -> pygame.math.Vector2:
    """
    Convert screen space --> world space.

    :param mouse_position: Mouse position
    :return: Original world coordinate.
    """
    world_x = mouse_position[0] / camera.scale + camera.offset.x
    world_y = mouse_position[1] / camera.scale + camera.offset.y
    return pygame.math.Vector2((int(world_x), int(world_y)))

class Camera:
    def __init__(self):
        self.screen: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE)
        self.offset: pygame.math.Vector2 = pygame.math.Vector2()
        self.scale: float = 1.0
        self.start_panning: pygame.math.Vector2 = pygame.math.Vector2()
        self.mouse_scroll_y: int = 0

        self.screen_update: bool = True

        l: int = CAMERA_PANNING_BORDER['left']
        t: int = CAMERA_PANNING_BORDER['top']
        w: int = self.screen.get_size()[0] - CAMERA_PANNING_BORDER['left'] - CAMERA_PANNING_BORDER['right']
        h: int = self.screen.get_size()[1] - CAMERA_PANNING_BORDER['top'] - CAMERA_PANNING_BORDER['bottom']
        self.__direction: pygame.math.Vector2 = pygame.math.Vector2()
        self.panning_border: pygame.Rect = pygame.Rect(l, t, w, h)

        self.panning_border_visible: bool = True

        # TO TEST OBJECT VISIBILITY ON SCREEN
        self.fake_screen: pygame.Rect = self.panning_border

    def movement(self, mouse_position: pygame.math.Vector2):
        """
        Camera screen panning and zoom. Self-update its offset and scale.
        :param mouse_position: Mouse position
        """
        keys = pygame.key.get_pressed()

        # Return noting while pressed 'shift' to do something
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            return

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
        self.mouse_scroll_y = 0  # Reset value

        # Mouse pressed panning
        mouses = pygame.mouse.get_pressed()
        if mouses[2]:
            self.offset += (self.start_panning - mouse_position) // self.scale
            self.start_panning = mouse_position
            self.screen_update = True

        # # Mouse border panning
        # if pygame.mouse.get_focused():
        #     if mouse_position.x < self.panning_border.left:
        #         self.__direction.x = -1
        #     elif mouse_position.x > self.panning_border.right:
        #         self.__direction.x = 1
        #     else:
        #
        #         self.__direction.x = 0
        #     if mouse_position.y < self.panning_border.top:
        #         self.__direction.y = -1
        #     elif mouse_position.y > self.panning_border.bottom:
        #         self.__direction.y = 1
        #     else:
        #         self.__direction.y = 0
        #     self.offset += self.__direction * MOUSE_PANNING_SPEED
        #     self.screen_update = True

        # Key pressed panning
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

    def draw_panning_border(self):
        """
        Display mouse panning border.
        """
        if not self.panning_border_visible:
            return

        pygame.draw.rect(self.screen, CAMERA_PANNING_BORDER_COLOR, self.panning_border, CAMERA_PANNING_BORDER_THICKNESS)

    def toggle_tab(self, event: pygame.event.Event):
        if event.key == pygame.K_TAB:
            self.panning_border_visible = not self.panning_border_visible
            self.screen_update = True

camera = Camera()