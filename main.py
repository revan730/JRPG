#!/usr/bin/python

# -*- coding: utf-8 -*-

from Game import Game
from GameStates import MainMenuState, SplashState
from ResourceHelpers import SettingsHelper as Settings
from moonphase import phase, position
import pygame as pg

pg.init()
settings = Settings()
w = settings.get('screen_width', 800)
h = settings.get('screen_height', 600)
DISPLAY = (w, h)
screen = pg.display.set_mode(DISPLAY)
pg.display.set_caption('JRPG')
if phase(position()) == "Full Moon":
    g = Game(screen, SplashState)
else:
    g = Game(screen, MainMenuState)
g.run()
