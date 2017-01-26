#!usr/bin/python

# -*- coding: utf-8 -*-

import pygame as pg

EngineEvent = pg.USEREVENT + 1
TeleportEvent = pg.USEREVENT + 2
EncounterEvent = pg.USEREVENT + 3
BattleEvent = pg.USEREVENT + 4  # Raised when some battle state related event occurs
MenuQuitEvent = pg.USEREVENT + 5  # Pygame allows only 9 user events.Don't forget about that and create subevents!
