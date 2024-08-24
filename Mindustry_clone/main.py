import pygame

from Scripts.Engine.Menu import *

class WorldEditorScreen:
    def __init__(self):
        self.WORLD_SIZE: tuple[int, int] = (32, 32)
        self.editor = WorldEditor(self.WORLD_SIZE)
        self.editor.load('Data/Save/world_editor_saved_1')

    def handle_draw(self):
        if camera.screen_update:
            self.editor.draw()
            brush_menu.custom_draw()
            block_menu.custom_draw()
            camera.draw_panning_border()
            debug.log()

            pygame.display.update()

        camera.screen_update = False

    def __quit_event(self, event: pygame.event.Event):
        # Exit the game.
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    def __camera_event(self, event: pygame.event.Event, mouse_position):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                # Start using the panning mouse.
                camera.start_panning = mouse_position

        # Mouse scroll zoom
        if event.type == pygame.MOUSEWHEEL:
            camera.mouse_scroll_y = event.y

    def __ui_interacting_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            # Change current pen head size
            brush_tool.change_pen_head_size(event)

            # Toggle tabs interacting
            camera.toggle_tab(event)
            self.editor.toggle_tab(event)
            if event.key == pygame.K_b:
                brush_menu.toggle_tab()
                block_menu.toggle_tab()

            # Save world map
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.editor.save("Data/Save/world_editor_saved_1")

        # Menu interacting
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                brush_menu.brush_select()
                block_menu.block_select()


    def handle_event(self, mouse_position):
        for event in pygame.event.get():
            self.__quit_event(event)
            self.__camera_event(event, mouse_position)
            self.__ui_interacting_event(event)


        if not mouse_on_menu_tabs(mouse_position):
            brush_tool.index_selected = self.editor.GetCurrentWorldIndex(mouse_position)
            brush_tool.paint(self.editor.background_layer)

        camera.movement(mouse_position)
        self.editor.update()


    def run(self):
        # Start frame
        # Avoid moving camera-offset in the start frame
        mouse_position = pygame.math.Vector2((camera.screen.get_size()[0] // 2, camera.screen.get_size()[1] // 2))

        # Update frame
        while True:
            self.handle_event(mouse_position)
            self.handle_draw()

            clock.tick(FPS)
            pygame.display.set_caption(f'{clock.get_fps():.2f}') # Display FPS
            mouse_position = pygame.math.Vector2(pygame.mouse.get_pos()) # Updating mouse position

if __name__ == '__main__':
    WorldEditorScreen().run()