import pygame


class TextSprite(pygame.sprite.Sprite):
    """Simple class to make text sprites"""
    def __init__(self,
                 message: str,
                 pos: tuple[int, int],
                 font: pygame.font.Font = None,
                 color: tuple[int, int, int] = (255, 255, 255),
                 *,
                 anker_point: str = "topleft",
                 font_name: str | None = None,
                 font_size: int = 30):
        super().__init__()
        self.font = font if font else pygame.font.Font(font_name, font_size)

        self.image = self.font.render(message, True, color)
        self.rect = self.image.get_rect(**{anker_point: pos})

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)


class TextButtonSprite(TextSprite):
    def __init__(self,
                 message: str,
                 pos: tuple[int, int],
                 font: pygame.font.Font = None,
                 color: tuple[int, int, int] = (255, 255, 255),
                 *,
                 anker_point: str = "topleft",
                 font_name: str | None = None,
                 font_size: int = 30,
                 border: int = 2):
        super().__init__(message, pos, font, color,
                         anker_point=anker_point, font_name=font_name, font_size=font_size)
        self.border = border
        self.color = color
        self.hover = False

    def update(self, mouse_pos: tuple[int, int]):
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, screen: pygame.Surface, pos: tuple[int, int] = None) -> None:
        my_rect = self.rect if not pos else self.rect.move(pos)
        screen.blit(self.image, my_rect)
        if not self.border:
            return
        if self.hover:
            pygame.draw.rect(screen, self.color, my_rect.inflate(18, 14), width=self.border+2, border_radius=4)
        else:
            pygame.draw.rect(screen, self.color, my_rect.inflate(16, 12), width=self.border, border_radius=4)


"""
class FadingTextSprite(TextSprite):
    def __init__(self,
                 message: str,
                 pos: tuple[int, int],
                 color: tuple[int, int, int] = (127, 127, 127),
                 fade: int = 2,
                 *,
                 font_name: str | None = None,
                 font_size: int = 50):
        super().__init__(message, pos, color, font_name=font_name, font_size=font_size)
        self.image.set_alpha(254)
        self.fade = fade

    def update(self):
        new_alpha = self.image.get_alpha()
        if new_alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(new_alpha - self.fade)
            self.rect.move_ip(0, -1)
"""