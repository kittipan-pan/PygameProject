import pygame.mouse

from Mindustry_clone.Scripts.Engine.Menu import *
from Mindustry_clone.Scripts.Engine.Editor import world_editor

FPS: int = 60
clock: pygame.time.Clock = pygame.time.Clock()

class Main:
    def __init__(self):
        ...

    def handle_event(self, mouse_position):
        mouse_pressed = pygame.mouse.get_pressed()

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

            brush_menu.custom_draw()
            block_menu.custom_draw()

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