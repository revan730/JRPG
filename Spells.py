#!usr/bin/python

# -*- coding: utf-8 -*-

from Enums import CharacterEnum as Character, SideEnum


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
        :param character: CharacterEnum - determines which character can learn this spell (if spell is player-used)
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


class Fireball(Spell):

    def __init__(self):
        super().__init__('Fireball', 50, 10, 'Deal 15 points of damage', Character.Mage, SideEnum.NPC)

    def apply(self, target):
        target.apply_damage(15)

    def check_appliable(self, target):
        return True  # Spell is always appliable to NPC,as they are removed on knock out


class Lightning(Spell):

    def __init__(self):
        super().__init__('Lightning', 100, 20, 'Deal 25 points of damage', Character.Mage, SideEnum.NPC)

    def apply(self, target):
        target.apply_damage(25)

    def check_appliable(self, target):
        return True  # Spell is always appliable to NPC,as they are removed on knock out
        

class FireBreath(Spell):
    """
    Fire elemental spell
    """

    def __init__(self):
        super().__init__('Fire breath', 0, 10, 'Deal 15 points of damage', 0, SideEnum.Player)

    def apply(self, target):
        target.apply_magic_damage(15)

    def check_appliable(self, target):
        if target.KO:
            return False
        else:
            return True