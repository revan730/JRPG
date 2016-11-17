#!usr/bin/python

# -*- coding: utf-8 -*-

import pygame as pg
from ResourceHelpers import SpritesHelper


class BaseNPC(pg.sprite.Sprite):
    """
    Defines basic NPC class for battle state
    """

    def __init__(self):
        super().__init__()
        self.spells = []  # List of spell objects which NPC can cast
        self._res_name = None
        self.HP = 0
        self.MP = 0
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


class Test(BaseNPC):
    """
    Test NPC
    """

    def __init__(self):
        super().__init__()
        self.HP = 10
        self.MP = 5
        self.DMG = 2

    def load_sprites(self):
        helper = SpritesHelper()
        self.image = pg.transform.scale(pg.image.load(helper.get_sprite('test','battle_idle')), (30, 38))
        self.rect = self.image.get_rect()