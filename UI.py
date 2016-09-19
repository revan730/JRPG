# -*- coding: utf-8 -*-
import pygame as pg


class MenuItem():
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
