from core.common.names import *
import math
from math import sqrt
win_size = [1280, 720]

def scale_image(img, factor=4.0):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pg.transform.scale(img, size).convert()
def max_height_vertical(u, g):
    return (u * u) / (2 * g)


def find_u(height, g):
    return sqrt(height * 2 * g)


def blit_center(img, screen):
    screen.blit(
        img, [win_size[0] - (img.get_width() / 2), win_size[1] - (img.get_height() / 2)]
    )


def center_pos(img):
    return [
        win_size[0] / 2 - (img.get_width() / 2),
        win_size[1] / 2 - (img.get_height() / 2),
    ]


def swap_color(img, col1, col2):
    pg.transform.threshold(img, img, col1, (10, 10, 10), col2, 1, None, True)


def angle_between(points):
    return math.atan2(points[1][1] - points[0][1], points[1][0] - points[0][0])*180/math.pi


# clip function from daflufflyportato
def clip(surf, x, y, x_size, y_size):
    handle_surf = surf.copy()
    clipR = pg.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()


class SpriteSheet:
    def __init__(self, sheet, size, colorkey=[0, 0, 0]):
        self.spritesheet = sheet
        self.colorkey = colorkey
        self.size = [
            self.spritesheet.get_width() / size[0],
            self.spritesheet.get_height() / size[1],
        ]
        self.sheet = []
        for i in range(size[1]):
            self.sheet.append([])
            for j in range(size[0]):
                image = pg.Surface((self.size))
                image.set_colorkey(self.colorkey)
                image.blit(
                    self.spritesheet,
                    (0, 0),
                    [j * self.size[0], i * self.size[1], self.size[0], self.size[1]],
                )
                self.sheet[i].append(image)

    def get(self, loc):
        return self.sheet[loc[1]][loc[0]]

def now():
    return pg.time.get_ticks() / 1000
