#!usr/bin/python

# -*- coding: utf-8 -*-

from enum import Enum, unique


@unique
class GameEnum(Enum):
    """
    Game engine subevents
    """
    StateCallEvent = 0
    StateExitEvent = 1
    StackResetEvent = 2
    GameSaveEvent = 3
    GameLoadEvent = 4

@unique
class BattleEnum(Enum):
    """
    Battle state subevents
    """
    ActionSelected = 0  # Raised when user selects action for character in battle
    TargetSelected = 1
    CharacterKO = 2  # Raised when (non) player character is knocked out
    DamageDodged = 3  # Raised when damage dealt to player is dodged
    GameOver = 4  # Raised when all player characters are knocked out
    BattleWon = 5  # Raised when all NPC are knocked out (dead)
    NextTurn = 6  # Raised when turn is passed to next character (NPC or PC)
    StatusUpdate = 7  # Raised when status bar update is called
    AICall = 8  # Raised when ai method on current npc should be called
    SpellSelected = 9
    ItemSelected = 10


@unique
class SideEnum(Enum):
    NPC = 0
    Player = 1


@unique
class CharacterEnum(Enum):
    """
    Enumerate for character type check
    """
    Warrior = 0
    Mage = 1
    Healer = 2
    Ranger = 3


@unique
class ActionsEnum(Enum):
    """
    Enumeration for character battle actions
    """
    Attack = 0
    Magic = 1
    Item = 2
    Flee = 3
