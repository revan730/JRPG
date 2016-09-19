#!/usr/bin/python
# -*- coding: utf-8 -*-

from Game import Game
from GameStates import SplashState, MainMenuState
import pygame as pg

pg.init()
DISPLAY = (800, 640)
screen = pg.display.set_mode(DISPLAY)
states = {'SPLASH': SplashState, 'MAINMENU': MainMenuState}
pg.display.set_caption('JRPG Engine v0.0.1 pre-alpha')
g = Game(screen, states, 'SPLASH')
g.run()
