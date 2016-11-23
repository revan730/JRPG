#!usr/bin/python

# -*- coding: utf-8 -*-

from enum import Enum, unique
import pygame as pg
from ResourceHelpers import SettingsHelper as Settings, SpritesHelper as Sprites
from Events import TeleportEvent, EncounterEvent, BattleEvent
from Events import BattleEnum as Battle
import random as rand
import pyganim

P_HEIGHT = 18
P_WIDTH = 15


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


class PlayerParty(pg.sprite.Sprite):
    """
    Class used to represent player characters' party on world and location map
    """

    def __init__(self, x, y):
        """

        :param x: party's start x coordinate
        :param y: party's start y coordinate
        :return:
        """
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((P_WIDTH, P_HEIGHT))
        self.rect = pg.Rect(x, y, P_WIDTH, P_HEIGHT)
        self.iter = 0
        self.xvel = 0
        self.yvel = 0
        self.iter_index = 0
        self.up = self.down = self.left = self.right = False
        self.set_animations()
        self.current_anim = None
        self.paused = False
        item = Usable('Phoenix Down', 300, 'Ressurects fallen party members')
        sitem = Weapon('BFG', 228, 228, 'Instant kill')
        self.inventory = [item, sitem]  # content of common inventory
        self.gold = 20  # Starting gold amount
        self.create_party()

    def create_party(self):
        """
        Create party members for a new game
        :return:
        """
        self.warrior = Warrior()
        self.mage = Mage()
        self.healer = Healer()
        self.ranger = Ranger()

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def set_animations(self):
        """
        Load and initialize animations for player actions
        :return:
        """
        anim_delay = 0.15
        self.init_animations(anim_delay, *self.load_animations())

    def init_animations(self, anim_delay, anim_down_f, anim_idle_f, anim_left_f, anim_right_f, anim_up_f):
        """
        Initialize animations loaded form sprite files
        :param anim_delay: delay between animation frames
        :param anim_down_f: tuple of down walk animation frame file paths
        :param anim_idle_f: idle sprite
        :param anim_left_f: tuple of left walk animation frame file paths
        :param anim_right_f: tuple of right walk animation frame file paths
        :param anim_up_f: tuple of up walk animation frame file paths
        :return:
        """
        anim = []
        for a in anim_up_f:
            anim.append((a, anim_delay))
        self.anim_up = pyganim.PygAnimation(anim)
        self.anim_up.play()
        anim.clear()
        for a in anim_down_f:
            anim.append((a, anim_delay))
        self.anim_down = pyganim.PygAnimation(anim)
        self.anim_down.play()
        anim.clear()
        for a in anim_left_f:
            anim.append((a, anim_delay))
        self.anim_left = pyganim.PygAnimation(anim)
        self.anim_left.play()
        anim.clear()
        for a in anim_right_f:
            anim.append((a, anim_delay))
        self.anim_right = pyganim.PygAnimation(anim)
        self.anim_right.play()
        self.anim_idle = pyganim.PygAnimation(anim_idle_f)
        self.anim_idle.play()
        self.anim_idle.blit(self.image, (0, 0))

    def load_animations(self):
        """
        Get all player animations paths
        :return: all player animations
        """
        helper = Sprites()
        anim_up_f = helper.get_animation('warrior', 'up')
        anim_down_f = helper.get_animation('warrior', 'down')
        anim_left_f = helper.get_animation('warrior', 'left')
        anim_right_f = helper.get_animation('warrior', 'right')
        anim_idle_f = [(anim_down_f[1], 0.1)]
        bg_color = "#7bd5fe"
        self.image.set_colorkey(pg.Color(bg_color))
        return anim_down_f, anim_idle_f, anim_left_f, anim_right_f, anim_up_f

    def update(self, colliders, teleports, npcs):
        defvel = 2

        if not self.paused:
            if self.left:
                self.xvel = -defvel
                self.anim_left.blit(self.image, (0, 0))
                self.current_anim = self.anim_left

            if self.right:
                self.xvel = defvel
                self.anim_right.blit(self.image, (0, 0))
                self.current_anim = self.anim_right

            if self.up:
                self.yvel = -defvel
                self.anim_up.blit(self.image, (0, 0))
                self.current_anim = self.anim_up

            if self.down:
                self.yvel = defvel
                self.anim_down.blit(self.image, (0, 0))
                self.current_anim = self.anim_down

            if not (self.left or self.right):
                self.xvel = 0

            if not (self.up or self.down):
                self.yvel = 0

            if not (self.up or self.down or self.left or self.right):
                self.anim_idle.blit(self.image, (0, 0))
                self.current_anim = self.anim_down

            self.rect.x += self.xvel
            self.collide_x(colliders)
            self.rect.y += self.yvel
            self.collide_y(colliders)

            self.collide_teleport(teleports)
            self.collide_npc(npcs)

    def pause(self):
        """
        Stop player animation and movement (called on state pause)
        :return:
        """
        self.left = self.right = self.up = self.down = False
        self.current_anim.pause()
        self.paused = True

    def resume(self):
        """
        Resume player animation and movement
        :return:
        """
        self.current_anim.play()
        self.paused = False

    def collide_x(self, colliders):
        """
        Handles player party's collisions on x axis
        :param colliders: list of pygame rect objects to check collision on
        :return:
        """
        for c in colliders:
            if self.rect.colliderect(c):
                self.rect.x -= self.xvel
                self.xvel = 0

    def collide_y(self, colliders):
        """
        Handles player party's collisions on x axis
        :param colliders: list of pygame rect objects to check collision on
        :return:
        """
        for c in colliders:
            if self.rect.colliderect(c):
                self.rect.y -= self.yvel
                self.yvel = 0

    def collide_teleport(self, teleports):
        """
        Handles player party's collision on teleports,
        :param teleports: list of pygame rect object of teleport tiles to check on
        :return:
        """
        for t in teleports:
            if self.rect.colliderect(t.rect):
                event_args = {'teleport': t}
                tp_event = pg.event.Event(TeleportEvent, event_args)
                pg.event.post(tp_event)

    def collide_npc(self, npcs):
        for n in npcs:
            if self.rect.colliderect(n['rect']):
                event_args = {'npc': n['name'], 'party_members': n['party_members'], 'bg': n['bg']}
                npc_event = pg.event.Event(EncounterEvent, event_args)
                pg.event.post(npc_event)

    def scale_up(self):
        """
        Scale player party sprite and rect two times (for local map state)
        :return:
        """
        self.rect.width *= 2
        self.rect.height *= 2

    def get_scaled(self):
        return pg.transform.scale(self.image, (P_WIDTH * 2, P_HEIGHT * 2))

    def reset_scale(self):
        self.rect.width = P_WIDTH
        self.rect.height = P_HEIGHT
        self.image = pg.transform.scale(self.image, (P_WIDTH, P_HEIGHT))

    def add_items(self, *items):
        """
        Add items to inventory
        :param items: items to add
        :return:
        """
        items = list(items)
        self.inventory.extend(items)

    def add_spells(self, *spells):
        spells = list(spells)
        for s in spells:
            if s.char == CharacterEnum.Warrior:
                self.warrior.add_spells(s)
            elif s.char == CharacterEnum.Mage:
                self.mage.add_spells(s)
            elif s.char == CharacterEnum.Healer:
                self.healer.add_spells(s)
            elif s.char == CharacterEnum.Ranger:
                self.ranger.add_spells(s)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def __getitem__(self, item):
        if item == 0:
            return self.warrior
        elif item == 1:
            return self.mage
        elif item == 2:
            return self.healer
        elif item == 3:
            return self.ranger
        else:
            raise IndexError

    def __len__(self):
        return 4

    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = self[self.iter_index]
            self.iter_index += 1
            return item
        except IndexError:
            self.iter_index = 0
            raise StopIteration


class Camera(object):
    """
    Camera class used to follow player party in world and location states
    """

    def __init__(self, camera_func, width, heigth):
        """

        :param camera_func: camera function used to configurate camera behavior
        :param width: width of camera's field of view
        :param heigth: height of camera's field of view
        :return:
        """
        settings = Settings()
        self.screen_w = settings.get('screen_width', 800)
        self.screen_h = settings.get('settings_height', 640)
        self.width = width
        self.height = heigth
        self.camera_func = camera_func
        self.state = pg.Rect(0, 0, width, heigth)

    def apply(self, rect):
        """
        Called for every image to be rendered inside camera's POV
        :param rect: image's rectangle
        :return: rect moved relative to camera
        """
        return rect.move(self.state.topleft)

    def update(self, target):
        """
        Called to update camera's posotion related to target
        :param target: camera's target to focus
        :return:
        """
        self.state = self.camera_func(self.state, target.rect, (self.screen_w, self.screen_h))

    def camera_configure_world(self, target_rect, screen_size):
        l, t, _, _ = target_rect
        screen_w, screen_h = screen_size
        _, _, w, h = self
        l, t = -l + screen_w / 2, -t + screen_h / 2

        l = min(0, l)
        l = max(-(self.width - screen_w), l)
        t = max(-(self.height - screen_h), t)
        t = min(0, t)

        return pg.Rect(l, t, w, h)


class Teleport:
    """
    Class which represents on map teleport tile, with it's destination and collider rectangle
    """

    def __init__(self, rect, x, y, map_f, world):
        """
        Teleport object constructor
        :param rect: pygame rect object
        :param x: player x coord on new location
        :param y: player y coord on new location
        :param map_f: map file path
        :param world: world, either 'overworld' or 'localworld'
        :return:
        """
        self.rect = rect
        self.pos_x = x
        self.pos_y = y
        self.map_f = map_f
        self.world = world


class BaseMember:
    """
    Represents base game class to be derived by actual classes like Warrior
    """

    def __init__(self):
        self.LVL = 1  # Starting level is 1
        self.MAX_LVL = 25
        self.spells = []  # List of spell objects which Warrior can cast
        self.armor = Armor('Coat', 2, 10, 'coat')  # Armor item
        self.weapon = Weapon('Knife', 2, 8, 'knife')  # Weapon item
        self.KO = False  # Knocked out
        self.EXP = 0  # Starting experience
        self.UP_EXP = 0
        self.INT = 0
        self.STR = 0
        self.DEX = 0
        self.DUR = 0
        self.INT_INC = 0
        self.STR_INC = 0
        self.DEX_INC = 0
        self.DUR_INC = 0
        self.hp_multiplier = 0
        self.mp_multiplier = 0
        self.dmg_multiplier = 0
        self.exp_multiplier = 0
        self.base_evs = 0.05  # Base chance of attack evasion
        self._res_name = None

    def add_exp(self, exp):
        """
        Called when member gets experience points
        :param exp: int value of achieved experience
        :return:
        """
        self.EXP += exp
        if self.EXP >= self.UP_EXP:
            self.lvl_up()

    def lvl_up(self):
        """
        Called when member reaches maximum experience for current level.Counts new base stats values
        :return:
        """
        if self.LVL < self.MAX_LVL:
            self.LVL += 1
            self.UP_EXP = self.LVL * self.exp_multiplier
            self.INT += self.INT_INC
            self.STR += self.STR_INC
            self.DEX += self.DEX_INC
            self.DUR += self.DUR_INC
            self.recalculate_stats()

    def set_weapon(self, weapon):
        self.weapon = weapon
        self.recalculate_stats()

    def set_armor(self, armor):
        self.armor = armor
        self.recalculate_stats()

    def recalculate_stats(self):
        self.MAX_HP = self.DUR * self.hp_multiplier  # Maximal health points
        self.HP = self.MAX_HP  # Current HP, always regenerates to maximum when not in battle
        self.MAX_MP = self.INT * self.mp_multiplier  # Maximal mana points
        self.MP = self.MAX_MP  # Also regenerates after battle
        self.DMG = self.STR * self.dmg_multiplier  # Physical damage
        self.DEF = self.armor.defence  # Damage points consumed by armor
        self.EVS = self.base_evs * self.DEX / 10 # Evasion chance

    def get_attributes(self):
        attrs = {'hp': self.HP, 'max_hp': self.MAX_HP, 'mp': self.MP, 'max_mp': self.MAX_MP, 'str': self.STR, 'int': self.INT, 'dex': self.DEX, 'dur': self.DUR,
                'exp': self.EXP, 'lvl': self.LVL, 'dmg': self.DMG, 'def': self.DEF, 'evs': '{}%'.format(self.EVS * 100)}
        return attrs

    def get_worn_items(self):
        items = {'wp': self.weapon, 'arm': self.armor}
        return items

    def load_sprites(self):
        helper = Sprites()
        portrait_path = helper.get_sprite(self._res_name, 'portrait')
        portrait_image = pg.image.load(portrait_path)
        self.portrait = (portrait_image, portrait_image.get_rect())

        battle_path = helper.get_sprite(self._res_name, 'battle_idle')
        self.battle_image = pg.transform.scale(pg.image.load(battle_path), (30, 38))
        bg_color = "#7bd5fe"
        self.battle_image.set_colorkey(pg.Color(bg_color))
        self.battle_rect = self.battle_image.get_rect()

    def add_spells(self, *spells):
        self.spells.extend(list(spells))

    def apply_damage(self, dmg):
        """
        Apply physical damage to party member.Lowered by armor rating or dodged completely
        :param dmg: int - damage dealt
        """
        if rand.random() < self.EVS:  # Damage was dodged
            self.raise_event(Battle.DamageDodged)
        else:
            damage = dmg - self.DEF
            if damage <= 0:
                damage = 1  # To make sure that armor can't consume all damage - that's what evasion is for
            if damage < self.HP:
                self.HP -= damage
            else:  # damage is enough to knock out
                self.HP = 0
                self.KO = True
                self.raise_event(Battle.CharacterKO)

    def raise_event(self, subevent):
        """
        Raise player related event (Knocked out, damage dodged etc.)
        :param subevent: BattleEnum - related event
        """
        args_dict = {'sub': subevent, 'pc': self}
        event = pg.event.Event(BattleEvent, args_dict)
        pg.event.post(event)

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
        :return:
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
        :return:
        """
        pass


class Spell:
    """
    Represents spell, which can be applied to characters
    """

    def __init__(self, name, cost, mp_cost, info, character):
        """

        :param name: string - spell name
        :param cost: int - cost in gold
        :param mp_cost: int - mana cost
        :param info: string - spell description
        :param character: CharacterEnum - determines which character can learn this spell
        :return:
        """
        self.name = name
        self.cost = int(cost)
        self.mp = int(mp_cost)
        self.info = info
        self.char = character

    def apply(self, target):
        """
        apply spell on it's target
        :param target: player or enemy party member
        :return:
        """
        pass

    def __str__(self):
        return '{} ({} MP)'.format(self.name, self.mp)


class Warrior(BaseMember):
    """
    Represents warrior game class, with it's stats,sprites etc.
    """

    def __init__(self):
        super().__init__()
        self.name = 'Cid'
        self.INT = 10  # Intelligence, influences mana points
        self.STR = 10  # Strength, influences physical damage
        self.DEX = 15  # Dexterity, influences attack evasion chance
        self.DUR = 15  # Durability, influences maximal heath
        self.hp_multiplier = 2  # 2 HP points for each durability point
        self.mp_multiplier = 1  # Only 1 MP for each intelligence point
        self.dmg_multiplier = 1  # 2 Attack points for each strength point
        self.defence_multiplier = 2  # 2 Attack points can be dodged for every dexterity point
        self.exp_multiplier = 10  # Determines how much experience must be achieved for level up
        self.INT_INC = 1
        self.STR_INC = 1
        self.DEX_INC = 2
        self.DUR_INC = 2
        self._res_name = 'warrior'
        self.recalculate_stats()
        self.load_sprites()

    def __str__(self):
        return 'Warrior'


class Mage(BaseMember):
    """
    Represents Mage game class, with it's stats, sprites etc.
    """

    def __init__(self):
        super().__init__()
        self.name = 'Karos'
        self.INT = 15
        self.STR = 5
        self.DEX = 10
        self.DUR = 10
        self.hp_multiplier = 1
        self.mp_multiplier = 2
        self.dmg_multiplier = 1
        self.defence_multiplier = 1
        self.exp_multiplier = 12
        self.INT_INC = 2
        self.STR_INC = 1
        self.DEX_INC = 1
        self.DUR_INC = 2
        self._res_name = 'mage'
        self.recalculate_stats()
        self.load_sprites()

    def __str__(self):
        return 'Mage'


class Healer(BaseMember):
    """
    Class that represents Healer game class.
    """

    def __init__(self):
        super().__init__()
        self.name = 'Rilay'
        self.INT = 15
        self.STR = 5
        self.DEX = 10
        self.DUR = 5
        self.hp_multiplier = 1
        self.mp_multiplier = 2
        self.dmg_multiplier = 1
        self.defence_multiplier = 1
        self.exp_multiplier = 12
        self.INT_INC = 2
        self.STR_INC = 1
        self.DEX_INC = 1
        self.DUR_INC = 2
        self._res_name = 'healer'
        self.recalculate_stats()
        self.load_sprites()
        self.spells.append(Spell('Heal', 5, 5, "Restores 5 HP", CharacterEnum.Healer))

    def __str__(self):
        return 'Healer'


class Ranger(BaseMember):
    """
    Class that represents Ranger game class
    """

    def __init__(self):
        super().__init__()
        self.name = 'Jaden'
        self.INT = 10
        self.STR = 15
        self.DEX = 10
        self.DUR = 10
        self.hp_multiplier = 2
        self.mp_multiplier = 1
        self.dmg_multiplier = 2
        self.exp_multiplier = 10
        self.INT_INC = 1
        self.STR_INC = 2
        self.DEX_INC = 2
        self.DUR_INC = 1
        self._res_name = 'ranger'
        self.recalculate_stats()
        self.load_sprites()

    def __str__(self):
        return 'Ranger'
