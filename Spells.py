#!usr/bin/python

# -*- coding: utf-8 -*-

from enum import Enum, unique
from Player import CharacterEnum as Character

@unique
class SideEnum(Enum):
    NPC = 0
    Player = 1

class Spell:
    """
    Represents spell, which can be applied to characters
    """

    def __init__(self, name, cost, mp_cost, info, character, side):
        """

        :param name: string - spell name
        :param cost: int - cost in gold
        :param mp_cost: int - mana cost
        :param info: string - spell description
        :param character: CharacterEnum - determines which character can learn this spell
        :param side: SideEnum - determines if spell is used on Player or NPC party
        """
        self.name = name
        self.cost = int(cost)
        self.mp = int(mp_cost)
        self.info = info
        self.char = character
        self.side = side

    def apply(self, target):
        """
        apply spell on it's target
        :param target: player or enemy party member
        """
        pass

    def check_appliable(self, target):
        """
        Check if spell can be applied to target
        :param target:
        :return:
        """
        pass

    def __str__(self):
        return '{} ({} MP)'.format(self.name, self.mp)


class Heal(Spell):

    def __init__(self):
        super().__init__('Heal', 50, 5, 'Heal 5 MP', Character.Healer, SideEnum.Player)

    def apply(self, target):
        target.heal(5)

    def check_appliable(self, target):
        if target.KO is not True and target.HP < target.MAX_HP:
            return True
        else:
            return False