#!/usr/bin/python

# -*- coding: utf-8 -*-

from Game import Game
from GameStates import MainMenuState
from ResourceHelpers import SettingsHelper as Settings
import pygame as pg

pg.init()
h = 600
w = 800
DISPLAY = (w, h)
settings = Settings()
settings.set('screen_width', w)
settings.set('screen_height', h)
screen = pg.display.set_mode(DISPLAY)
pg.display.set_caption('Sephiroth engine')
g = Game(screen, MainMenuState)
g.run()
