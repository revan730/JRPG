# -*- coding: utf-8 -*-
import pygame as pg
from ResourceHelpers import StringsHelper
from Events import StateExitEvent


class MenuItem:
    """
    Represents text menu item,which can be active or inactive
    """
    def __init__(self, id, text, font, size, color_inactive, color_active, x, y):
        """
        Initialize menu item
        :param text: text of item
        :param font: font file
        :param size: size
        :return:
        """
        self.id = id
        self.caption = text
        self.color_active = color_active
        self.color_inactive = color_inactive
        self.font = pg.font.Font(font, size)
        self.set_inactive()
        self.rect = self.text.get_rect(center=(x, y))

    def set_active(self):
        self.text = self.font.render(self.caption, True, pg.Color(self.color_active))

    def set_inactive(self):
        self.text = self.font.render(self.caption, True, pg.Color(self.color_inactive))


class Window:
    """
    Basic window class for menu's,like pause,battle action,inventory
    """
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bg = pg.Surface((width, height))
        self.bg.fill(pg.Color('#000060'))

    def draw(self, surface):
        surface.blit(self.bg, (self.x, self.y))

    def update(self, key):
        """
        Update window state
        :param key: pygame key code of pressed key
        :return:
        """
        pass


class PauseWindow(Window):
    """
    Pause window which is called by game state when it's paused
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        helper = StringsHelper("en")
        menu_strings = helper.get_strings("pause_menu")
        self.quit = False
        self.menu_items = []
        self.add_items(menu_strings)
        self.cursor_pos = 0
        self.set_cursor()

    def add_items(self, item_strings):
        """x = self.x + self.width / 2
        y =  self.y + 50
        """
        font_size = 36
        x = self.x + self.width / 2
        padding = self.height / 2 + self.y - font_size / 2 # calculate starting padding for first item to be near window center
        y = padding
        for i in sorted(item_strings.keys()):
            self.menu_items.append(MenuItem(i, item_strings[i], None, font_size, 'white', 'green', x ,y))
            y += font_size

    def draw(self, surface):
        super().draw(surface)
        for i in self.menu_items:
            surface.blit(i.text, i.rect)

    def update(self, key):
        if key == pg.K_w or key == pg.K_UP:
            self.prev_item()
        elif key == pg.K_s or key == pg.K_DOWN:
            self.next_item()
        elif key == pg.K_RETURN or key == pg.K_f:
            self.choose_item()

    def next_item(self):
        if self.cursor_pos + 1 < len(self.menu_items):
            self.menu_items[self.cursor_pos].set_inactive()
            self.cursor_pos += 1
            self.set_cursor()

    def prev_item(self):
        if self.cursor_pos > 0:
            self.menu_items[self.cursor_pos].set_inactive()
            self.cursor_pos -= 1
            self.set_cursor()

    def choose_item(self):
        if self.cursor_pos == 0:
            self.quit = True
        elif self.cursor_pos == 1:
            exit_event = pg.event.Event(StateExitEvent, {'state': '', 'args': None})
            pg.event.post(exit_event)

    def set_cursor(self):
        self.menu_items[self.cursor_pos].set_active()

