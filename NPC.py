#!usr/bin/python

# -*- coding: utf-8 -*-

import pygame as pg
from ResourceHelpers import SpritesHelper
from Events import BattleEnum as Battle
from Events import BattleEvent
import random as rand
import Items


def action(func):  # Decorator for NPC actions, posts NextTurn event so NPC can't take several actions at once
    def wrapped(*args, **kwargs):
        status = func(*args, **kwargs)
        event = pg.event.Event(BattleEvent, {'sub': Battle.NextTurn, 'status': status})
        pg.event.post(event)

    return wrapped

class BaseNPC(pg.sprite.Sprite):
    """
    Defines basic NPC class for battle state
    """

    def __init__(self):
        super().__init__()
        self.spells = []  # List of spell objects which NPC can cast
        self._res_name = None
        self.HP = 0
        self.MAX_HP = 0
        self.MP = 0
        self.MAX_MP = 0
        self.DMG = 0
        self._loot = []  # list of Item,Drop Rate dicts
        self.load_sprites()
        self.EXP = 0  # Experience points which every player character gets for defeating this NPC
        self.gold = 0  # Gold for defeating this NPC

    def decide(self, player_party, npc_party):
        """
        Method which is called when npc must decide what to do on it's turn
        :param player_party: player party object
        :param npc_party: list of npc party members
        """
        pass

    def load_sprites(self):
        """
        Loads all sprite images
        """
        pass

    def get_attributes(self):
        attrs = {'hp': self.HP, 'max_hp': self.MAX_HP, 'mp': self.MP, 'max_mp': self.MAX_MP}

        return attrs

    def apply_damage(self, dmg):
        if dmg >= self.HP:
            self.HP = 0
            args_dict = {'sub': Battle.CharacterKO, 'pc': self}
            event = pg.event.Event(BattleEvent, args_dict)
            pg.event.post(event)
        else:
            self.HP -= dmg

    @action
    def attack(self, player):
        damaged =  player.apply_damage(self.DMG)
        if damaged is False:
            status = "{} dodged {}'s damage".format(player.name, self.name)
        else:
            status = '{} dealt {} damage to {}'.format(self.name, self.DMG, player.name)
        return status

    @action
    def cast_spell(self, spell, target):
        pass

    def get_loot(self):
        """
        Generate loot for this NPC
        :return: list of Item objects
        """
        loot = []
        chance = rand.random()
        for i in self._loot:
            if chance >= i['rate']:
                loot.append(i['item'])

        return loot

    def post_status(self, status):
        """
        Called after making decision to set status explaining npc's action
        :param status: string - action description
        """
        args_dict = {'status': status, 'sub': Battle.StatusUpdate}
        event = pg.event.Event(BattleEvent, args_dict)
        pg.event.post(event)


class Test(BaseNPC):
    """
    Test NPC
    """
    Counter = 0

    def __init__(self):
        super().__init__()
        self.HP = self.MAX_HP = 100
        self.MP = self.MAX_MP = 5
        self.DMG = 5
        self.EXP = 15
        self.gold = 30
        self.name = 'Test NPC {}'.format(Test.Counter)
        Test.Counter += 1
        self._loot = [{'item': Items.Armor('Iron Armor', 5, 30, 'Iron armor'), 'rate': 0.25}]

    def load_sprites(self):
        helper = SpritesHelper()
        self.image = pg.transform.scale(pg.image.load(helper.get_sprite('test','battle_idle')), (30, 38))
        self.rect = self.image.get_rect()

    def decide(self, player_party, npc_party):
        alive = player_party.get_alive()
        if len(alive) > 0:
            self.attack(alive[0])

    # TODO: Define basic actions in superclass, so they can be somehow wrapped for easier status posting

