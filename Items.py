#!usr/bin/python

# -*- coding: utf-8 -*-


class BaseItem:
    """
    Represents basic inventory item class
    """

    def __init__(self, name, cost, info):
        self.name = name
        self.cost = int(cost)
        self.info = info


class Weapon(BaseItem):
    """
    Represents weapon item class for inventory
    """

    def __init__(self, name, dmg, cost, info):
        """

        :param name: string - weapon name
        :param dmg: int - weapon damage (will be added to owner's physical damage)
        :param cost: int - weapon cost
        """
        super().__init__(name, cost, info)
        self.dmg = dmg

    def __str__(self):
        return '{} (+{})'.format(self.name, self.dmg)


class Armor(BaseItem):
    """
    Represents armor item class for inventory
    """

    def __init__(self, name, defence, cost, info):
        super().__init__(name, cost, info)
        self.defence = defence

    def __str__(self):
        return '{} (+{})'.format(self.name, self.defence)


class Usable(BaseItem):
    """
    Represents usable item like potion, which applies some effect to user
    """

    def __init__(self, name, cost, info):
        super().__init__(name, cost, info)

    def __str__(self):
        return '{} ({} G)'.format(self.name, self.cost)

    def apply_effect(self, target):
        """
        apply item effect on it's target
        :param target: player or enemy party member
        """
        pass

