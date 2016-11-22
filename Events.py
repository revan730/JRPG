#!usr/bin/python

# -*- coding: utf-8 -*-

import pygame as pg

StateCallEvent = pg.USEREVENT + 1
StateExitEvent = pg.USEREVENT + 2
TeleportEvent = pg.USEREVENT + 3
EncounterEvent = pg.USEREVENT + 4
ActionSelectedEvent = pg.USEREVENT + 5  # Raised when user selects action for character in battle
CharacterKOEvent = pg.USEREVENT + 6  # Raised when (non) player character is knocked out
NPCSelectedEvent = pg.USEREVENT + 7