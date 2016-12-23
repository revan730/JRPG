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

    def __init__(self, name, cost, info, side):
        super().__init__(name, cost, info)
        self.side = side

    def __str__(self):
        return '{} ({} G)'.format(self.name, self.cost)

    def apply_effect(self, target):
        """
        apply item effect on it's target
        :param target: player or enemy party member
        """
        pass

    def check_appliable(self, target):
        pass


class ManaPotion(Usable):

    def __init__(self):
        super().__init__('Mana potion', 50, 'Restores 20 MP', 1)

    def apply_effect(self, target):
        target.restore_mana(20)

    def check_appliable(self, target):
        if target.KO is not True and target.MP < target.MAX_MP:
            return True
        else:
            return False


class PhoenixDown(Usable):

    def __init__(self):
        super().__init__('Phoenix Down', 300, 'Resurrects party member',1)

    def apply_effect(self, target):
        target.resurrect()

    def check_appliable(self, target):
        if target.KO is True:
            return True
        else:
            return False


class FireBlade(Weapon):
    """
    Drops from fire elemental
    """

    def __init__(self):
        super().__init__('Fire blade', 10, 85, 'Blade made of elemental fire')
