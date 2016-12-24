#!/usr/bin/python

# -*- coding: utf-8 -*-

from Game import Game
from GameStates import MainMenuState, SplashState
from ResourceHelpers import SettingsHelper as Settings
from moonphase import phase, position
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
if phase(position()) == "Full Moon":
    g = Game(screen, SplashState)
else:
    g = Game(screen, MainMenuState)
g.run()  # TODO: Global!! Animations in BattleState,more maps,NPCs
