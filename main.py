#!/usr/bin/python
# -*- coding: utf-8 -*-

from Game import Game
from GameStates import SplashState, MainMenuState, WorldMapState
import pygame as pg

pg.init()
DISPLAY = (800, 640)
screen = pg.display.set_mode(DISPLAY)
pg.display.set_caption('Sephiroth engine')
g = Game(screen, SplashState)
g.run()
