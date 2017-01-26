#!usr/bin/python

# -*- coding: utf-8 -*-

import pygame as pg
from ResourceHelpers import SettingsHelper as Settings, SpritesHelper as Sprites
from Events import TeleportEvent, EncounterEvent, BattleEvent
from Enums import BattleEnum as Battle
import Items
import Spells
import random as rand
import pyganim

P_HEIGHT = 18
P_WIDTH = 15


class KOError(Exception):
    """
    Raised when KOed character gets damage
    """

    def __init__(self, character):
        self.value = 'action cannot be applied to {}: character is knocked out'.format(character.name)

    def __str__(self):
        return repr(self.value)


class PlayerParty(pg.sprite.Sprite):
    """
    Class used to represent player characters' party on world and location map
    """

    def __init__(self, x, y):
        """

        :param x: party's start x coordinate
        :param y: party's start y coordinate
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
        item = Items.HealthPotion()
        sitem = Items.Weapon('BFG', 228, 228, 'Instant kill')
        self.inventory = [item, sitem]  # content of common inventory
        self.gold = 1000  # Starting gold amount
        self.create_party()
        self.current_alive = self.get_alive()
        self.alive_iter = iter(self.current_alive)

    def create_party(self):
        """
        Create party members for a new game
        """
        self.warrior = Warrior()
        self.mage = Mage()
        self.healer = Healer()
        self.ranger = Ranger()
        self.members = {0: self.warrior, 1: self.mage, 2: self.healer, 3: self.ranger}

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def on_load(self):
        """
        Called when game state is loaded (to avoid dead pygame surfaces)
        """
        self.image = pg.Surface((P_WIDTH, P_HEIGHT))
        self.set_animations()
        for i in self:
            i.load_sprites()

    def set_animations(self):
        """
        Load and initialize animations for player actions
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
        """
        self.left = self.right = self.up = self.down = False
        self.current_anim.pause()
        self.paused = True

    def resume(self):
        """
        Resume player animation and movement
        """
        self.current_anim.play()
        self.paused = False

    def enter_battle(self):
        self.pause()
        self.current_alive = self.get_alive()
        self.alive_iter = iter(self.current_alive)

    def exit_battle(self):
        for i in self:
            i.regenerate()
        self.current_alive = None
        self.alive_iter = None
        self.resume()

    def collide_x(self, colliders):
        """
        Handles player party's collisions on x axis
        :param colliders: list of pygame rect objects to check collision on
        """
        for c in colliders:
            if self.rect.colliderect(c):
                self.rect.x -= self.xvel
                self.xvel = 0

    def collide_y(self, colliders):
        """
        Handles player party's collisions on x axis
        :param colliders: list of pygame rect objects to check collision on
        """
        for c in colliders:
            if self.rect.colliderect(c):
                self.rect.y -= self.yvel
                self.yvel = 0

    def collide_teleport(self, teleports):
        """
        Handles player party's collision on teleports,
        :param teleports: list of pygame rect object of teleport tiles to check on
        """
        for t in teleports:
            if self.rect.colliderect(t.rect):
                event_args = {'teleport': t}
                tp_event = pg.event.Event(TeleportEvent, event_args)
                pg.event.post(tp_event)

    def collide_npc(self, npcs):
        for n in npcs:
            if self.rect.colliderect(n.rect):
                event_args = {'npc': n}
                npc_event = pg.event.Event(EncounterEvent, event_args)
                pg.event.post(npc_event)

    def scale_up(self):
        """
        Scale player party sprite and rect two times (for local map state)
        """
        self.rect.width *= 2
        self.rect.height *= 2

    def get_scaled(self):
        return pg.transform.scale(self.image, (P_WIDTH * 2, P_HEIGHT * 2))

    def reset_scale(self):
        self.rect.width = P_WIDTH
        self.rect.height = P_HEIGHT
        self.image = pg.transform.scale(self.image, (P_WIDTH, P_HEIGHT))

    def add_items(self, items):
        """
        Add items to inventory
        :param items: list of items to add
        """
        self.inventory.extend(items)

    def remove_item(self, item):
        """
        Remove item from inventory
        :param item: Item object
        """
        self.inventory.remove(item)

    def add_exp(self, exp):
        """
        Add experience to all party members
        :param exp: int - added experience
        """
        for i in self:
            i.add_exp(exp)

    def add_spells(self, *spells):
        spells = list(spells)
        for s in spells:
            if s.char.value in self.members.keys():
                self.members[s.char.value].add_spells(s)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def __getitem__(self, item):
        if item in self.members.keys():
            return self.members[item]
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

    def get_index(self, character):
        """
        Get index of character in party order
        :param character: BaseMember object
        :return: int - index
        """
        for key, val in self.members.items():
            if character is val:
                return key

        raise TypeError('parameter is not a party member object')

    def get_battle_sprites(self):
        """
        Returns list of tuples with battle sprites of each not KOed member
        :return: list of tuples
        """
        sprites = []
        alive = self.get_alive()
        for i in alive:
            pair = (i.battle_image, i.battle_rect)
            sprites.append(pair)

        return sprites

    def get_alive(self):
        """
        Returns list of not KOed characters
        :return: list of BaseMember objects
        """
        return [i for i in self if not i.KO]

    def get_next_alive(self):
        """
        Returns next alive party member,which stands in order after prev parameter.
        Raises StopIteration if prev was last in order or there are no more alive members
        :return: BaseMember object
        """
        if len(self.current_alive) != len(self.get_alive()):
            self.current_alive = self.get_alive()
            self.alive_iter = iter(self.current_alive)
        try:
            return next(self.alive_iter)
        except StopIteration:
            self.current_alive = self.get_alive()
            self.alive_iter = iter(self.current_alive)
            raise StopIteration

    def get_usable_items(self):
        return [i for i in self.inventory if isinstance(i, Items.Usable)]


class Camera(object):
    """
    Camera class used to follow player party in world and location states
    """

    def __init__(self, camera_func, width, heigth):
        """

        :param camera_func: camera function used to configurate camera behavior
        :param width: width of camera's field of view
        :param heigth: height of camera's field of view
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
        self.armor = Items.Armor('Coat', 2, 10, 'coat')  # Armor item
        self.weapon = Items.Weapon('Knife', 2, 8, 'knife')  # Weapon item
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
        """
        self.EXP += exp
        if self.EXP >= self.UP_EXP:
            self.lvl_up()

    def lvl_up(self):
        """
        Called when member reaches maximum experience for current level.Counts new base stats values
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

    def regenerate(self):
        self.HP = self.MAX_HP
        self.MP = self.MAX_MP
        
    def resurrect(self):
        self.KO = False
        self.regenerate()

    def recalculate_stats(self):
        self.MAX_HP = self.DUR * self.hp_multiplier  # Maximal health points
        self.HP = self.MAX_HP  # Current HP, always regenerates to maximum when not in battle
        self.MAX_MP = self.INT * self.mp_multiplier  # Maximal mana points
        self.MP = self.MAX_MP  # Also regenerates after battle
        self.DMG = self.STR * self.dmg_multiplier + self.weapon.dmg  # Physical damage
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
        sp = list(spells)
        for s in sp:
            if not any(isinstance(x, s.__class__) for x in self.spells):
                self.spells.append(s)

    def apply_damage(self, dmg):
        """
        Apply physical damage to party member.Lowered by armor rating or dodged completely
        :param dmg: int - damage dealt
        :return: bool - True if damage wasn't dodged
        """
        if not self.KO:
            if rand.random() < self.EVS:  # Damage was dodged
                return False
            else:
                damage = dmg - self.DEF
                if damage <= 0:
                    damage = 1  # To make sure that armor can't consume all damage - that's what evasion is for
                if damage < self.HP:
                    self.HP -= damage
                    return True
                else:  # damage is enough to knock out
                    self.HP = 0
                    self.KO = True
                    self.raise_event(Battle.CharacterKO)
                    return True
        else:
            raise KOError(self)

    def apply_magic_damage(self, damage):
        """
        Apply magical damage, which ignores armor and evasion
        """
        if not self.KO:
            if damage < self.HP:
                self.HP -= damage
            else:
                self.HP = 0
                self.KO = True
                self.raise_event(Battle.CharacterKO)
        else:
            raise KOError(self)

    def cast_spell(self, spell, target):
        """
        Cast spell on specified target
        :param spell: Spell object which belongs to this party member
        :param target: Spell target
        :return: bool - True if spell was successfully casted (enough mana,target is alive)
        """
        if spell in self.spells:
            if self.MP >= spell.mp:
                spell.apply(target)
                self.MP -= spell.mp
                return True
                # KOed players (except for revive spells)
            else:
                return False  # Not enough mana
        else:
            return False

    def heal(self, points):
        """
        Regenerates specified amount of HP
        :param points: int - HP
        """
        if not self.KO:
            if points > self.MAX_HP - self.HP:
                self.HP = self.MAX_HP
            else:
                self.HP += points
        else:
            raise KOError(self)

    def restore_mana(self, points):
        """
        Regenerates specified amount of MP
        :param points: int - MP
        """
        if not self.KO:
            if points > self.MAX_MP - self.MP:
                self.MP = self.MAX_MP
            else:
                self.MP += points
        else:
            raise KOError(self)

    def raise_event(self, subevent):
        """
        Raise player related event (Knocked out, damage dodged etc.)
        :param subevent: BattleEnum - related event
        """
        args_dict = {'sub': subevent, 'pc': self}
        event = pg.event.Event(BattleEvent, args_dict)
        pg.event.post(event)


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
        self.spells.append(Spells.Fireball())

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
        self.spells.append(Spells.Heal())

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
