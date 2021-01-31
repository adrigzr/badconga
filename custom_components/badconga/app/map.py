""" map """
# pylint: disable=invalid-name,too-many-instance-attributes
import math
from io import BytesIO
from PIL import Image, ImageDraw
from .entities import Position

# target
color_background = (0, 0, 0, 0)
color_wall = (58, 252, 236, 255)
color_external = (0, 0, 0, 0)
color_missing = (0, 0, 0, 0)
color_done_area = (44, 168, 158, 255)
color_pending_area = (154, 227, 221, 255)
color_charger = (93, 133, 129, 255)
color_robot = (11, 48, 45, 255)

# native
pixel_background = 0
pixel_external = 1
pixel_missing = 2
pixel_charger = 5
pixel_robot = 6
pixel_wall = 255

# animation steps
steps = (22, 33, 44, 33, 22, 11)

def calc_ellipse(pos, radius):
    """ calc_ellipse """
    (pos_x, pos_y) = pos
    return [(pos_x - radius, pos_y - radius), (pos_x + radius, pos_y + radius)]

def calc_segment(center, aperture, rotate=0):
    """ calculate start and end degrees of a circle segment pointing
        at center and opening aperture degrees both ways """
    center += rotate
    return (center + aperture, center - aperture)

def colorize_map(map_image):
    """ colorize_map """
    map_image = map_image.convert('RGBA')
    pixdata = map_image.load()
    for y in range(map_image.size[1]):
        for x in range(map_image.size[0]):
            color = pixdata[x, y][0]
            if color == pixel_background:
                pixdata[x, y] = color_background
            elif color == pixel_wall:
                pixdata[x, y] = color_wall
            elif color == pixel_external:
                pixdata[x, y] = color_external
            elif color == pixel_missing:
                pixdata[x, y] = color_missing
            elif color == pixel_charger:
                pixdata[x, y] = color_charger
            elif color == pixel_robot:
                pixdata[x, y] = color_robot
            elif color >= 60:
                pixdata[x, y] = color_done_area
            elif color >= 10:
                pixdata[x, y] = color_pending_area
            else:
                raise Exception(pixdata[x, y])
    return map_image

def crop_map(map_image):
    """ crop_map """
    cropbox = map_image.getbbox()
    margin = 15
    cropbox_with_margin = (cropbox[0] - margin, cropbox[1] - margin,
                           cropbox[2] + margin, cropbox[3] + margin)
    map_image = map_image.crop(cropbox_with_margin)
    return map_image

class Map:
    """ Map """
    def __init__(self):
        self.grid = None
        self.size_x = 0
        self.size_y = 0
        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0
        self.charger = Position()
        self.robot = Position()
        self.cache = None
        self.animate = False
        self.frame = 0

    def get_position(self, pos):
        """ get_position """
        (pos_x, pos_y) = pos
        grid_x = (pos_x - self.min_x) * self.size_x / (self.max_x - self.min_x)
        grid_y = (pos_y - self.min_y) * self.size_y / (self.max_y - self.min_y)
        return (grid_x, grid_y)

    def draw_elements(self, map_image):
        """ draw_elements """
        draw = ImageDraw.ImageDraw(map_image)
        if self.charger.isvalid():
            pos = self.get_position((self.charger.x, self.charger.y))
            aperture = 66
            start, end = calc_segment(math.degrees(self.charger.phi),
                                      aperture, rotate=180)
            draw.pieslice(calc_ellipse(pos, 3),
                          start, end,
                          fill=pixel_charger, outline=pixel_charger, width=1)
        if self.robot.isvalid():
            pos = self.get_position((self.robot.x, self.robot.y))
            if self.robot.phi == 0.0:
                aperture = 0.1
            else:
                step = self.frame % len(steps) if self.animate else 0
                aperture = steps[step]
            start, end = calc_segment(math.degrees(self.robot.phi),
                                      aperture)
            draw.pieslice(calc_ellipse(pos, 3),
                          start, end,
                          fill=pixel_robot, outline=pixel_robot, width=1)
        return map_image

    def invalidate(self):
        """ invalidate cache """
        self.frame += 1
        self.cache = None

    @property
    def image(self):
        """ image """
        if not self.grid:
            return None
        cached = self.cache
        if cached is not None:
            return cached
        img = Image.frombytes('L', (self.size_x, self.size_y), self.grid)
        img = self.draw_elements(img)
        img = crop_map(img)
        img = colorize_map(img)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        image = buffer.getvalue()
        self.cache = image
        return image
