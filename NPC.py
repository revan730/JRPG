#!usr/bin/python

# -*- coding: utf-8 -*-

import pygame as pg
from ResourceHelpers import SpritesHelper
from Events import BattleEnum as Battle
from Events import BattleEvent


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
        self.load_sprites()

    def decide(self, player_party, npc_party):
        """
        Method which is called when npc must decide what to do on it's turn
        :param player_party: player party object
        :param npc_party: list of npc party members
        :return:
        """
        pass

    def load_sprites(self):
        """
        Loads all sprite images
        :return:
        """
        pass

    def get_attributes(self):
        attrs = {'hp': self.HP, 'max_hp': self.MAX_HP, 'mp': self.MP, 'max_mp': self.MAX_MP}

        return attrs

    def apply_damage(self, dmg):
        if dmg >= self.HP:
            self.HP = 0
            self.KO = True
            args_dict = {'sub': Battle.CharacterKO, 'pc': self}
            event = pg.event.Event(BattleEvent, args_dict)
            pg.event.post(event)
        else:
            self.HP -= dmg


class Test(BaseNPC):
    """
    Test NPC
    """

    def __init__(self):
        super().__init__()
        self.HP = self.MAX_HP =  100
        self.MP = self.MAX_MP = 5
        self.DMG = 15
        self.name = 'Test NPC'

    def load_sprites(self):
        helper = SpritesHelper()
        self.image = pg.transform.scale(pg.image.load(helper.get_sprite('test','battle_idle')), (30, 38))
        self.rect = self.image.get_rect()

    def decide(self, player_party, npc_party):
        player_party.get_alive()[0].apply_damage(self.DMG)