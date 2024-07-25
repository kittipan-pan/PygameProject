from Mindustry_clone.Scripts.Engine.Menu import *

FPS: int = 60
clock: pygame.time.Clock = pygame.time.Clock()

world_editor.load('Data/Save/world_editor_save1.csv')

class WorldEditorScreen:
    def __init__(self):
        ...

    def handle_draw(self):
        if camera.screen_update:
            world_editor.update()
            camera.screen.fill((0, 0, 0))
            world_editor.draw_layer()
            world_editor.draw_grid()
            world_editor.draw_rect()
            brush_menu.custom_draw()
            block_menu.custom_draw()
            debug.log()
            camera.draw_panning_border()
            pygame.display.update()

        camera.screen_update = False

    def handle_event(self, mouse_position):
        for event in pygame.event.get():
            # Exit the game.
            if event.type == pygame.QUIT:
                world_editor.save()
                pygame.quit()
                exit()

            # MOUSE DOWN
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    brush_menu.brush_select()
                    block_menu.block_select()

                if event.button == 3:
                    # Start using the panning mouse.
                    camera.start_panning = mouse_position

            # Mouse scroll zoom
            if event.type == pygame.MOUSEWHEEL:
                camera.mouse_scroll_y = event.y

            # KEY DOWN
            if event.type == pygame.KEYDOWN:
                camera.key_input(event)
                world_editor.key_input(event)

                # Change 'pen' and 'erase' brush size
                brush_tool.change_pen_head_size(event)

                # Toggle brush menu
                if event.key == pygame.K_b:
                    brush_menu.toggle_tab()
                    block_menu.toggle_tab()

        camera.editor_movement(mouse_position)

        if not mouse_on_menu_tabs(mouse_position):
            brush_tool.paint(world_editor.background_layer, mouse_position)

    def run(self):
        # Start frame
        # Avoid move camera offset
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