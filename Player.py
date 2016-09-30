import pygame as pg
from ResourceHelpers import SettingsHelper as Settings


class PlayerParty(pg.sprite.Sprite):  # TODO: Must have a sprite, not just dumb pink rectangle
    """
    Class used to represent player characters' party on world and location map
    """

    def __init__(self, x, y):
        """

        :param x: party's start x coordinate
        :param y: party's start y coordinate
        :return:
        """
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((16, 24))
        self.image.fill(pg.Color('#f7646c'))
        self.rect = pg.Rect(x, y, 16, 24)
        self.xvel = 0
        self.yvel = 0
        self.up = self.down = self.left = self.right = False

    def update(self, colliders):
        defvel = 5

        if self.left:
            self.xvel = -defvel

        if self.right:
            self.xvel = defvel

        if self.up:
            self.yvel = -defvel

        if self.down:
            self.yvel = defvel

        if not (self.left or self.right):
            self.xvel = 0

        if not (self.up or self.down):
            self.yvel = 0

        self.rect.x += self.xvel
        self.collide_x(colliders)
        self.rect.y += self.yvel
        self.collide_y(colliders)

    def collide_x(self, colliders):
        """
        Handles player party's collisions on x axis
        :param colliders: list of pygame rect objects to check collision on
        :return:
        """
        for c in colliders:
            if self.rect.colliderect(c):
                self.rect.x -= self.xvel
                self.xvel = 0

    def collide_y(self, colliders):
        """
        Handles player party's collisions on x axis
        :param colliders: list of pygame rect objects to check collision on
        :return:
        """
        for c in colliders:
            if self.rect.colliderect(c):
                self.rect.y -= self.yvel
                self.yvel = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Camera(object):
    """
    Camera class used to follow player party in world and location states
    """

    def __init__(self, camera_func, width, heigth):
        """

        :param camera_func: camera function used to configurate camera behavior
        :param width: width of camera's field of view
        :param heigth: height of camera's field of view
        :return:
        """
        settings = Settings()
        self.screen_w = settings.get('screen_width', 800)
        self.screen_h = settings.get('settings_height', 640)
        self.width = width
        self.height = heigth
        self.camera_func = camera_func
        self.state = pg.Rect(0, 0, width, heigth)

    def apply(self, rect):
        """
        Called for every image to be rendered inside camera's POV
        :param rect: image's rectangle
        :return: rect moved relative to camera
        """
        return rect.move(self.state.topleft)

    def update(self, target):
        """
        Called to update camera's posotion related to target
        :param target: camera's target to focus
        :return:
        """
        self.state = self.camera_func(self.state, target.rect, (self.screen_w, self.screen_h))

    def camera_configure_world(self, target_rect, screen_size):
        l, t, _, _ = target_rect
        screen_w, screen_h = screen_size
        _, _, w, h = self
        l, t = -l + screen_w / 2, -t + screen_h / 2

        l = min(0, l)
        l = max(-(self.width - screen_w), l)
        t = max(-(self.height - screen_h), t)
        t = min(0, t)

        return pg.Rect(l, t, w, h)
