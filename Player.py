import pygame as pg
from ResourceHelpers import SettingsHelper as Settings, AnimationsHelper as Animations
from Events import TeleportEvent
import pyganim


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
        self.image = pg.Surface((15, 18))
        # self.image.fill(pg.Color('#f7646c'))
        self.rect = pg.Rect(x, y, 15, 18)
        self.xvel = 0
        self.yvel = 0
        self.up = self.down = self.left = self.right = False
        self.set_animations()
        self.current_anim = None
        self.paused = False
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
        helper = Animations()
        anim_up_f = helper.get_animation('warrior', 'up')
        anim_down_f = helper.get_animation('warrior', 'down')
        anim_left_f = helper.get_animation('warrior', 'left')
        anim_right_f = helper.get_animation('warrior', 'right')
        anim_idle_f = [(anim_down_f[1], 0.1)]
        bg_color = "#7bd5fe"
        self.image.set_colorkey(pg.Color(bg_color))
        return anim_down_f, anim_idle_f, anim_left_f, anim_right_f, anim_up_f

    def update(self, colliders, teleports):
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

    def draw(self, surface):
        surface.blit(self.image, self.rect)


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
        self.inventory = "PLACEHOLDER - BaseInventory class"  # Warrior's inventory
        self.EXP = 0  # Starting explerience
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
        self.defence_multiplier = 0
        self.dmg_multiplier = 0
        self.exp_multiplier = 0

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

    def recalculate_stats(self):
        self.MAX_HP = self.DUR * self.hp_multiplier  # Warrior's starting heals points at level 1
        self.HP = self.MAX_HP  # Current HP, always regenerates to maximum when not in battle
        self.MAX_MP = self.INT * self.mp_multiplier  # Warrior's starting mana points, he doesn't have much because he's not a magic-oriented class
        self.MP = self.MAX_MP  # Also regenerates after battle. Warrior only has some minor skills which require MP to limit number of their usage
        self.DMG = self.STR * self.dmg_multiplier  # Starting physical damage
        self.MAX_DEF = self.DEX * self.defence_multiplier  # Starting defence (affects only physical damage)


class Warrior(BaseMember):
    """
    Represents warrior game class, with it's stats,sprites etc.
    """

    def __init__(self):
        super().__init__()
        self.INT = 10  # Intelligence, influences mana points
        self.STR = 10  # Strength, influences physical damage
        self.DEX = 15  # Dexterity, influences pure damage taken from physical attacks
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
        self.recalculate_stats()


class Mage(BaseMember):
    """
    Represents Mage game class, with it's stats, sprites etc.
    """

    def __init__(self):
        super().__init__()
        self.INT = 15
        self.STR = 10
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
        self.recalculate_stats()


class Healer(BaseMember):
    """
    Class that represents Healer game class.
    """

    def __init__(self):
        super().__init__()
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
        self.recalculate_stats()


class Ranger(BaseMember):
    """
    Class that represents Ranger game class
    """

    def __init__(self):
        super().__init__()
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
        self.recalculate_stats()
