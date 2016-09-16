#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame as pg

class GameState:

    def __init__(self):
        self.finish = False
        self.next_state = None
        self.screen_rect = pg.display.get_surface().get_rect()
        self.persist = {}


    def get_state(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass

    def on_start(self, persistent):
        self.persist = persistent