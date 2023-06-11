import math

import pygame
from pygame import Vector2

from tiles.building import Building, MarketGood, PopGroup
from sprites.textSprites import TextSprite


class HexGrid:
    """
    Pointy top hexgrid

    Example cords: { \n
    (0, 0), (2, 0), (4, 0), (6, 0), \n
    (1, 1), (3, 1), (5, 1), (7, 1), \n
    (0, 2), (2, 2), (4, 2), (6, 2), \n
    (1, 3), (3, 3), (5, 3), (7, 3)}

    An observation, pairs are always \n
    (even, even) or (uneven, uneven)
    """
    angles = [30+i for i in range(0, 360, 60)]

    def __init__(self, inside_radius: float = 100) -> None:
        self.inside_radius = inside_radius
        self.height_offset = inside_radius * math.sqrt(3)
        self.outside_radius = self.height_offset / 1.5
        self.grid = dict()
        self.vertices = [Vector2.from_polar((self.outside_radius, angle)) for angle in self.angles]

    def add_3(self) -> None:
        """Add some Hexes"""
        self.grid[(3, 1)] = Building("test", (255, 0, 0))
        self.grid[(5, 1)] = Building("test", (0, 255, 0))
        self.grid[(4, 2)] = Building("test", (0, 0, 255), 1, {"Grain": MarketGood(0, 10)})
        self.grid[(6, 2)] = Building("Wheat farm", (0, 127, 0), 1,
                                     {"Grain": MarketGood(20, 0)}, [PopGroup("Laborer", 5_000)])

    def total_offset(self, cord: tuple[int, int], scroll: Vector2) -> Vector2:
        """pos + scroll"""
        return scroll + (cord[0] * self.inside_radius, cord[1] * self.height_offset)

    def get_vertices(self, total_offset: Vector2) -> list[Vector2, ...]:
        """total_offset + vertices"""
        return [total_offset+vertex for vertex in self.vertices]

    def draw_single(self, screen: pygame.Surface, scroll: Vector2,
                    cord: tuple[int, int], color: tuple[int, int, int], width: int = 0) -> None:
        """Draw 1 hex in grid \nUsed for hover outline"""
        total_offset = self.total_offset(cord, scroll)
        pygame.draw.polygon(screen, color, self.get_vertices(total_offset), width)

    def draw(self, screen: pygame.Surface, scroll: Vector2) -> None:
        """Draw all hexes in grid"""
        for cord, building in self.grid.items():
            offset = self.total_offset(cord, scroll)
            pygame.draw.polygon(screen, building.color, self.get_vertices(offset))
            TextSprite(building.name, tuple(offset), anker_point="center").draw(screen)

    def cord_of_collision_with_point(self, point: tuple[float, float]) -> tuple[int, int]:
        """Return cord of hex pointed at"""
        x_float = point[0] / self.inside_radius
        y_float = point[1] / self.height_offset
        y_3 = (y_float % 1) * 3
        # if y in the rectangle part of the hexagon
        if y_3 <= 1 or y_3 >= 2:
            round_y = round(y_float)
            round_y_even = round_y % 2 == 0
            x_return = 2*round(x_float/2) if round_y_even else 2*round((x_float + 1)/2) - 1
            return x_return, round_y
        # else:
        floor_y = math.floor(y_float)
        floor_x = math.floor(x_float)
        floor_y_even = floor_y % 2 == 0
        floor_x_even = floor_x % 2 == 0
        # x1, y1 pair even x2, y2 pair uneven
        y1, y2 = (floor_y, floor_y + 1) if floor_y_even else (floor_y + 1, floor_y)
        x1, x2 = (floor_x, floor_x + 1) if floor_x_even else (floor_x + 1, floor_x)
        # calculate distance from the given point to p1 and p2
        d12 = pow(x_float-x1, 2) + pow(y_float-y1, 2)
        d22 = pow(x_float-x2, 2) + pow(y_float-y2, 2)
        # return the (p1 or p2) which is closest to the given point
        return (x1, y1) if d12 < d22 else (x2, y2)

    def total_market_dict(self) -> dict[str, MarketGood]:
        """Build total market of all buildings in grid"""
        ans = dict()
        for building in self.grid.values():
            for key, value in building.market_dict.items():
                if key not in ans:
                    ans[key] = value
                else:
                    ans[key] += value
        return ans

    def next_turn(self):
        tmd = self.total_market_dict()
        for building in self.grid.values():
            building.next_turn(tmd)
