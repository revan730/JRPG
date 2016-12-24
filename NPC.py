#!usr/bin/python

# -*- coding: utf-8 -*-

import pygame as pg

import Spells
from ResourceHelpers import SpritesHelper
from Enums import BattleEnum as Battle
from Events import BattleEvent
import random as rand
from Items import *


def action(func):  # Decorator for NPC actions, posts NextTurn event so NPC can't take several actions at once
    def wrapped(*args, **kwargs):
        status = func(*args, **kwargs)
        event = pg.event.Event(BattleEvent, {'sub': Battle.NextTurn, 'status': status})
        pg.event.post(event)

    return wrapped


class MapNPC:
    """
    Defines NPC for map state
    """

    def __init__(self,x, y, party, bg, id):
        """

        :param party: list of npc party members (turned to objects by eval function)
        :param bg: name of battle background file
        :param id: unique party id (for quests etc.)
        """
        self.party = party
        self.bg = bg
        self.id = id
        self.x = x
        self.y = y
        self.create_map_image()

    def create_map_image(self):
        member = eval(self.party[0])
        self.image = member.load_map_sprite(member)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def on_load(self):
        self.create_map_image()

class MapTrader:
    """
    Defines trader for map state
    """

    def __init__(self,x, y):
        self.x = x
        self.y = y
        self.load_sprite()

    def load_sprite(self):
        helper = SpritesHelper()
        self.image = pg.transform.scale(pg.image.load(helper.get_sprite('trader', 'map')), (30, 38))
        self.image.set_colorkey(pg.Color("#7bd5fe"))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def on_load(self):
        self.load_sprite()

class MapWizard:
    """
    Defines wizard for map state
    """

    def __init__(self,x, y):
        self.x = x
        self.y = y
        self.load_sprite()

    def load_sprite(self):
        helper = SpritesHelper()
        self.image = pg.transform.scale(pg.image.load(helper.get_sprite('wizard', 'map')), (30, 38))
        self.image.set_colorkey(pg.Color("#7bd5fe"))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def on_load(self):
        self.load_sprite()


class BaseNPC(pg.sprite.Sprite):
    """
    Defines basic NPC class for battle state
    """

    def __init__(self, res_name, hp, mp, dmg, exp, gold, loot, spells):
        super().__init__()
        self.spells = spells  # List of spell objects which NPC can cast
        self._res_name = res_name
        self.HP = hp
        self.MAX_HP = hp
        self.MP = mp
        self.MAX_MP = mp
        self.DMG = dmg
        self._loot = loot  # list of Item,Drop Rate dicts
        self.load_sprites()
        self.EXP = exp  # Experience points which every player character gets for defeating this NPC
        self.gold = gold  # Gold for defeating this NPC

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

    def load_map_sprite(self):
        """
        Load map sprite and return it
        :return: pygame image
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
        damaged = player.apply_damage(self.DMG)
        if damaged is False:
            status = "{} dodged {}'s damage".format(player.name, self.name)
        else:
            status = '{} dealt {} damage to {}'.format(self.name, self.DMG, player.name)
        return status

    @action
    def cast_spell(self, spell, target):
        """
        cast selected spell on target
        :param spell: spell object
        :param target: BaseMember or BaseNPC object
        :return: status string - information about spell cast
        """
        spell.apply(target)
        self.MP -= spell.mp
        status = '{} casted {} on {}'.format(self.name, spell, target.name)
        return status

    def get_loot(self):
        """
        Generate loot for this NPC
        :return: list of Item objects
        """
        loot = []
        chance = rand.random()
        for i in self._loot:
            if chance >= i['rate']:
                loot.append(i['item']())

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
        loot = [{'item': ManaPotion, 'rate': 0.25}]
        super().__init__('test', 100, 0, 5, 15, 30, loot, [])
        self.name = 'Test NPC {}'.format(Test.Counter + 1)
        Test.Counter += 1

    def __del__(self):
        Test.Counter -= 1

    def load_sprites(self):
        helper = SpritesHelper()
        self.image = pg.transform.scale(pg.image.load(helper.get_sprite('test', 'battle_idle')), (30, 38))
        self.image.set_colorkey(pg.Color("#7bd5fe"))
        self.rect = self.image.get_rect()

    def load_map_sprite(self):
        helper = SpritesHelper()
        image = pg.transform.scale(pg.image.load(helper.get_sprite('test', 'map')), (30, 38))
        image.set_colorkey(pg.Color("#7bd5fe"))

        return image

    def decide(self, player_party, npc_party):
        alive = player_party.get_alive()
        if len(alive) > 0:
            self.attack(alive[0])


class FireElemental(BaseNPC):
    """
    Fire elemental NPC.Targets player with smallest amount of health first
    """

    Counter = 0

    def __init__(self):
        loot = [{'item': FireBlade, 'rate': 0.1}]
        spells = [Spells.FireBreath()]
        super(FireElemental, self).__init__('fire_elem', 50, 20, 5, 10, 30, loot, spells)
        self.name = 'Fire elemental {}'.format(FireElemental.Counter + 1)
        FireElemental.Counter += 1

    def load_sprites(self):
        helper = SpritesHelper()
        self.image = pg.transform.scale(pg.image.load(helper.get_sprite('fire_elem', 'battle_idle')), (24, 36))
        self.image.set_colorkey(pg.Color("#fec5c5"))
        self.rect = self.image.get_rect()

    def load_map_sprite(self):
        helper = SpritesHelper()
        image = pg.transform.scale(pg.image.load(helper.get_sprite('fire_elem', 'map')), (24, 36))
        image.set_colorkey(pg.Color("#fec5c5"))

        return image

    def decide(self, player_party, npc_party):
        """
        Choose player with smallest amount of health.Cast fire breath if enough MP
        """
        if len(player_party.get_alive()) > 0:
            min_member = player_party.get_alive()[0]
            for i in player_party.get_alive():
                if i.HP < min_member.HP:
                    min_member = i
            if self.MP >= self.spells[0].mp:
                self.cast_spell(self.spells[0], min_member)
            else:
                self.attack(min_member)