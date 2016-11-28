#!usr/bin/python

# -*- coding: utf-8 -*-

import pygame as pg
from enum import Enum, unique

StateCallEvent = pg.USEREVENT + 1
StateExitEvent = pg.USEREVENT + 2
TeleportEvent = pg.USEREVENT + 3
EncounterEvent = pg.USEREVENT + 4
BattleEvent = pg.USEREVENT + 5  # Raised when some battle state related event occurs
MenuQuitEvent = pg.USEREVENT + 6  # Pygame allows only 9 user events.Don't forget about that and create subevents!
StackResetEvent = pg.USEREVENT + 7  # Raised when state stack reset to first state is called


@unique
class BattleEnum(Enum):
    """
    Battle state subevents
    """
    ActionSelected = 0  # Raised when user selects action for character in battle
    NPCSelected = 1
    CharacterKO = 2  # Raised when (non) player character is knocked out
    DamageDodged = 3  # Raised when damage dealt to player is dodged
    GameOver = 4  # Raised when all player characters are knocked out
    BattleWon = 5  # Raised when all NPC are knocked out (dead)
    NextTurn = 6  # Raised when turn is passed to next character (NPC or PC)
    StatusUpdate = 7  # Raised when status bar update is called
    AICall = 8  # Raised when ai method on current npc should be called
