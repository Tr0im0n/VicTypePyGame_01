
import pygame

from tiles.building import Building, goods_price_dict
from sprites.textSprites import TextSprite, TextButtonSprite


class AbstractMenu:
    menu_color = (127, 63, 0)
    size = (40, 40)
    pos = (20, 20)
    tabs = (20, 120, 220)
    col_size = 80
    row_size = 40

    text_color = (0, 0, 0)
    font_size = 24

    def __init__(self):
        self.image = pygame.Surface(self.size)
        self.image.fill(self.menu_color)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.group = pygame.sprite.Group()
        self.font = pygame.font.Font(None, self.font_size)
        self.hover = False

    def add_text_to_group(self, message: str, col: int, row: int, *,
                          group: pygame.sprite.Group | pygame.sprite.GroupSingle = None) -> None:
        TextSprite(message, (col*self.col_size + 20, row*self.row_size + 20), self.font).add(group or self.group)

    def construct_groups(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)


class MarketMenu(AbstractMenu):
    size = (340, 680)

    def __init__(self, market_dict: dict):
        super().__init__()
        self.construct_groups(market_dict)
        self.group.draw(self.image)

    def construct_groups(self, market_dict: dict):
        text = self.add_text_to_group

        text("Good", 0, 4)
        text("Supply", 1, 4)
        text("Demand", 2, 4)
        text("Price", 3, 4)

        for i, (key, value) in enumerate(market_dict.items()):
            text(key, 0, 5)
            text(f"{value.supply}", 1, 5)
            text(f"{value.demand}", 2, 5)
            price = goods_price_dict[key] * value.price_mult()
            text(f"{price}", 3, 5)


class BuildingMenu(AbstractMenu):
    size = (340, 680)

    def __init__(self, building: Building, cord: tuple[int, int] = None):
        super().__init__()
        self.building = building
        self.cord = cord
        self.upgrade_button: TextButtonSprite = None
        self.construct_groups()
        self.group.draw(self.image)

    def construct_groups(self):
        text = self.add_text_to_group

        text(f"{self.building.name}", 0, 0)
        text(f"Level: {self.building.level}", 0, 1)
        self.upgrade_button = TextButtonSprite("Upgrade Building",
                                               (0 * self.col_size + 20, 2 * self.row_size + 20),
                                               self.font, border=3)
        text(f"Cash reserve: {self.building.cash_reserve}", 0, 3)

        # text("Good", 0, 4)
        # text("Supply", 1, 4)
        # text("Demand", 2, 4)
        # text("Price", 3, 4)
        #
        # for i, (key, value) in enumerate(self.building.market_dict.items()):
        #     text(key, 0, 5)
        #     text(f"{value.supply}", 1, 5)
        #     text(f"{value.demand}", 2, 5)

        MarketMenu.construct_groups(self, self.building.market_dict)

    def update(self, mouse_pos: tuple[int, int]):
        self.upgrade_button.update((mouse_pos[0] - self.pos[0], mouse_pos[1] - self.pos[1]))
        self.hover = self.upgrade_button.hover

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)
        self.upgrade_button.draw(screen, self.pos)
