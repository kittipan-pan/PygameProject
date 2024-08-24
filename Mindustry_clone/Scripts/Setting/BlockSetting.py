from Scripts.Engine.CameraScreen import *

class Block(pygame.sprite.Sprite):
    def __init__(self, image_source: FilePath = ""):
        super().__init__()
        self.image_source: str = image_source
        self.name: str = ""
        self.id: int = 0

        if not len(self.image_source):
            self.original_image: pygame.Surface = pygame.image.load('Images/NOT_FOUND.png').convert_alpha()
        else:
            self.original_image: pygame.Surface = pygame.image.load(self.image_source).convert_alpha()

        self.image: pygame.Surface = self.original_image
        self.rect: pygame.Rect = self.image.get_rect()
        self.position: pygame.math.Vector2 = pygame.math.Vector2()

        self.visible: bool = True

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
        self.visible = True
        self.rect.topleft = WorldToScreenCoordinate(self.position)

        # On-Off block visibility
        if self.rect.x < camera.fake_screen.left - PIXEL * camera.scale or self.rect.x > camera.fake_screen.right:
            self.visible = False
        if self.rect.y < camera.fake_screen.top - PIXEL * camera.scale or self.rect.y > camera.fake_screen.bottom:
            self.visible = False

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

block_dict: dict[int, Block] = {
    1: Grass, 2: Rock, 3: Sand, 4: Water
}