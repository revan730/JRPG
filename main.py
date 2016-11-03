#!/usr/bin/python
# -*- coding: utf-8 -*-

from Game import Game
from GameStates import MainMenuState
from ResourceHelpers import SettingsHelper as Settings
import pygame as pg

pg.init()
DISPLAY = (860, 640)
settings = Settings()
settings.set('screen_width', 860)
settings.set('screen_height', 640)
screen = pg.display.set_mode(DISPLAY)
pg.display.set_caption('Sephiroth engine')
g = Game(screen, MainMenuState)
g.run()
