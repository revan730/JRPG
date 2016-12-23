#!usr/bin/python

# -*- coding: utf-8 -*-

import os
import pygame as pg
from Events import *
from Enums import BattleEnum as Battle, SideEnum as Sides, ActionsEnum as Actions, GameEnum
from ResourceHelpers import StringsHelper, SettingsHelper, MapsHelper, SpritesHelper
import UI
from Player import PlayerParty, Camera, Teleport, BaseMember
from NPC import Test, FireElemental, BaseNPC, MapNPC, MapTrader, MapWizard
from pytmx import load_pygame


class StateStack:
    def __init__(self):
        self.states = []

    def is_empty(self):
        return self.states == []

    def push(self, state):
        self.states.append(state)

    def pop(self):
        return self.states.pop()

    def peek(self):
        return self.states[len(self.states) - 1]

    def size(self):
        return len(self.states)

    def reset(self):
        """
        Removes all states but first
        """
        while self.size() > 1:
            self.pop()

    def set_persistent(self, persistent):
        self.peek().persistent = persistent

    def update(self, dt):
        """
        Call update method of current state
        :param dt: time since last frame
        """

        self.peek().update(dt)

    def get_event(self, event):
        """
        Gives one specific event for state to process
        :param event: event passed to game state
        """
        self.peek().get_event(event)

    def send_callback(self, callback):
        self.peek().on_return(callback)


class GameState:

    def __init__(self, persistent=None):
        self.quit = False
        self.finish = False
        self.screen_rect = pg.display.get_surface().get_rect()
        self.screen_width = self.screen_rect.width
        self.screen_height = self.screen_rect.height
        self.persist = persistent

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True

    def update(self, dt):
        pass

    def draw(self, surface):
        pass

    def on_pause(self):
        pass

    def on_resume(self):
        pass

    def on_save(self):
        pass

    def on_load(self):
        pass

    def exit(self, args_dict=None):
        """
        Called when state ends and game should return to previous state
        :param args_dict: dictionary of callback arguments,which will be received by previous state in stack
        """
        exit_event = pg.event.Event(EngineEvent, {'sub': GameEnum.StateExitEvent, 'state': '', 'args': args_dict})
        pg.event.post(exit_event)

    def call_state(self, state, args_dict=None):
        event_args = {'sub': GameEnum.StateCallEvent, 'state': state, 'args': args_dict}
        call_event = pg.event.Event(EngineEvent, event_args)
        pg.event.post(call_event)

    def reset_states(self):
        """
        Called to clear all states from stack but first one
        """
        event = pg.event.Event(EngineEvent, {'sub': GameEnum.StackResetEvent})
        pg.event.post(event)

    def on_return(self, callback):
        """
        Executed when called state was successfully ended
        :param callback: callback from called state (e.g. list of monster loot,new player coordinates)
        """
        pass


class SplashState(GameState):
    def __init__(self):
        super().__init__()
        self.font = pg.font.Font(None, 24)
        self.text = self.font.render('JRPG Engine', True, pg.Color('dodgerblue'))
        self.text_rect = self.text.get_rect(center=self.screen_rect.center)
        self.bg = pg.Surface((self.screen_width, self.screen_height))
        self.bg.fill(pg.Color('black'))

    def get_event(self, event):
        super().get_event(event)
        if event.type == pg.KEYDOWN and event.key == pg.K_t:
            args_dict = {}
            self.call_state(MainMenuState, args_dict)

    def call_state(self, state, args_dict=None):
        super(SplashState, self).call_state(state, args_dict)

    def on_return(self, callback):
        print('Callback from called state:{}'.format(callback['r_val']))

    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        surface.blit(self.text, self.text_rect)


class MenuState(GameState):
    """
    Base state for menu screens
    """

    def __init__(self):
        super().__init__()

    def load_items(self, res_name, y):
        helper = StringsHelper("en")
        self.font = pg.font.Font(None, 24)
        self.bg = pg.Surface((self.screen_width, self.screen_height))
        self.bg.fill(pg.Color('black'))
        menu_strings = helper.get_strings(res_name)

        x = self.bg.get_width() / 2

        self.menu_items = []
        for i in sorted(menu_strings.keys()):
            self.menu_items.append(UI.MenuItem(i, menu_strings[i], None, 36, 'white', 'dodgerblue', x, y))
            y += 30

        self.cursor_pos = 0
        self.set_cursor()

    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        for i in self.menu_items:
            surface.blit(i.image, i.rect)

    def get_event(self, event):
        super().get_event(event)
        if event.type == pg.KEYDOWN and (event.key == pg.K_s or event.key == pg.K_DOWN):
            self.next_item()
        elif event.type == pg.KEYDOWN and (event.key == pg.K_w or event.key == pg.K_UP):
            self.prev_item()
        elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
            self.choose_item()

    def set_cursor(self):
        self.menu_items[self.cursor_pos].set_active()

    def next_item(self):
        if self.cursor_pos + 1 < len(self.menu_items):
            self.menu_items[self.cursor_pos].set_inactive()
            self.cursor_pos += 1
            self.set_cursor()

    def prev_item(self):
        if self.cursor_pos > 0:
            self.menu_items[self.cursor_pos].set_inactive()
            self.cursor_pos -= 1
            self.set_cursor()

    def choose_item(self):
        pass


class MainMenuState(MenuState):
    def __init__(self):
        super().__init__()
        self.load_items("main_menu", 250)

    def choose_item(self):
        if self.cursor_pos == 0:
            args_dict = {'player_party': None, 'pos_x': 0, 'pos_y': 0, 'map_file': 'resources/maps/world_test.tmx'}
            self.call_state(WorldMapState, args_dict)
        elif self.cursor_pos == 1:
            self.call_state(LoadState, {})
        elif self.cursor_pos == 2:
            pass
        elif self.cursor_pos == 3:
            pass
        elif self.cursor_pos == 4:
            self.quit = True


class LoadState(MenuState):
    """
    Load screen,accessed from main menu
    """

    def __init__(self, persistent=None):
        super().__init__()
        self.menu = None
        self.load_items("load_menu", 150)

    def get_event(self, event):
        if self.menu is None:
            super().get_event(event)
            if event.type == pg.KEYDOWN and event.key == pg.K_BACKSPACE:
                self.exit(None)
        else:
            if event.type == pg.KEYDOWN and event.key == pg.K_q:
                self.menu = None

    def draw(self, surface):
        super().draw(surface)
        if self.menu is not None:
            self.menu.draw(surface)

    def choose_item(self):
        path = 'saves/save_{}.sf'.format(self.cursor_pos)
        if os.path.isfile(path):
            args_dict = {'sub': GameEnum.GameLoadEvent, 'path': path}
            event = pg.event.Event(EngineEvent, args_dict)
            pg.event.post(event)
        else:
            self.menu = UI.MessageWindow(self.screen_width / 2 - 100, self.screen_height / 2 - 75, 200, 150, "No data in this slot")
            print("h {} w {}".format(self.screen_height, self.screen_width))


class MapState(GameState):
    def __init__(self, persistent):
        super().__init__(persistent)
        self.tiled_map = load_pygame(self.persist['map_file'])
        if self.persist['player_party'] is not None:
            self.player_party = self.persist['player_party']
        else:
            self.player_party = PlayerParty(360, 360)
        if 'npc_reg' in self.persist.keys():
            self.npc_registry = self.persist['npc_reg']
        else:
            self.npc_registry = []
        self.camera = Camera(Camera.camera_configure_world, self.screen_width, self.screen_width)
        self.tile_size = self.tiled_map.tilewidth
        self.scale_factor = 2  # Tiles are 16x16,so we must draw them 2 times larger
        self.scaled_size = self.tile_size * self.scale_factor
        self.colliders = self.create_colliders()
        self.teleports = self.create_teleports()
        self.npcs = self.create_npcs()
        self.pause_menu = None
        self.menu = None

    def update(self, dt):
        self.player_party.update(self.colliders, self.teleports, self.npcs)
        self.camera.update(self.player_party)

    def draw(self, surface):
        if self.bg:
            surface.blit(self.bg, (0, 0))

    def get_event(self, event):
        super().get_event(event)
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:  # Handle pause menu (de)activation
            self.toggle_pause_menu()
        elif self.pause_menu is None and event.type == pg.KEYDOWN and event.key == pg.K_p:
            self.toggle_menu(UI.PartyWindow)
        elif self.pause_menu is None and event.type == pg.KEYDOWN and event.key == pg.K_i:
            self.toggle_menu(UI.InventoryWindow)
        elif self.pause_menu is None and event.type == EncounterEvent and isinstance(event.npc, MapTrader):
            self.toggle_menu(UI.TraderWindow)
        elif self.pause_menu is None and event.type == EncounterEvent and isinstance(event.npc, MapWizard):
            self.toggle_menu(UI.WizardWindow)
        elif event.type == EncounterEvent and isinstance(event.npc, MapNPC):
            self.enter_battle(event)
        elif event.type == MenuQuitEvent and event.window == UI.PauseWindow:
            self.toggle_pause_menu()
        elif event.type == MenuQuitEvent and event.window is not UI.SelectCharacterWindow:
            self.toggle_menu(event.window)
        elif event.type == pg.KEYDOWN and event.key == pg.K_l:  # Call game load\save menu
            self.toggle_menu(UI.LoadSaveWindow)
        elif self.pause_menu is None and self.menu is None:  # Handle player control only if menu is not active
            self.player_control(event)
        elif self.pause_menu is not None and event.type == pg.KEYDOWN:  # Let the pause menu handle input first
            self.pause_menu.update(event.key)
        elif self.menu is not None and event.type == pg.KEYDOWN:
            self.menu.update(event.key)

    def player_control(self, event):
        """
        Handle key press events related to player control
        :param event: pygame KEYDOWN or KEYUP event
        """
        if event.type == pg.KEYDOWN and event.key == pg.K_w:
            self.player_party.up = True
        elif event.type == pg.KEYUP and event.key == pg.K_w:
                self.player_party.up = False
        elif event.type == pg.KEYDOWN and event.key == pg.K_s:
            self.player_party.down = True
        elif event.type == pg.KEYUP and event.key == pg.K_s:
            self.player_party.down = False
        elif event.type == pg.KEYDOWN and event.key == pg.K_a:
            self.player_party.left = True
        elif event.type == pg.KEYUP and event.key == pg.K_a:
            self.player_party.left = False
        elif event.type == pg.KEYDOWN and event.key == pg.K_d:
            self.player_party.right = True
        elif event.type == pg.KEYUP and event.key == pg.K_d:
            self.player_party.right = False

    def toggle_pause_menu(self):
        if self.pause_menu is None:
            self.on_pause()
            width = self.screen_width / 4
            height = self.screen_height / 4
            x = self.screen_width / 2 - width / 2
            y = self.screen_height / 2 - height / 2
            self.pause_menu = UI.PauseWindow(x, y, width, height)
        else:
            self.pause_menu = None
            self.on_resume()

    def toggle_menu(self, menu):
        if self.menu is None:
            self.on_pause()
            width = self.screen_width * 0.55
            height = self.screen_height * 0.5
            x = self.screen_width / 2 - width / 2
            y = self.screen_height / 2 - height / 2
            self.menu = menu(x, y, width, height, self.player_party)
        else:
            self.menu = None
            self.on_resume()

    def on_pause(self):
        self.player_party.pause()

    def on_resume(self):
        self.player_party.resume()

    def on_save(self):
        self.tiled_map = None

    def on_load(self):
        self.tiled_map = load_pygame(self.persist['map_file'])  # reload tiled map
        self.player_party.on_load()  # reload all sprites
        for i in self.npcs:
            i.on_load()
        self.set_bg()

    def create_colliders(self):
        """
        Create rectangles to be used as colliders for collision check
        :return: list of pygame rect objects
        """
        size = self.scaled_size
        colliders = []
        for i in range(0, len(self.tiled_map.layers) - 1):
            for x, y, image in self.tiled_map.layers[i].tiles():
                p = self.tiled_map.get_tile_properties(x, y, i)
                if p['walkable'] == 'false':
                    rect = pg.Rect(x * size, y * size, self.scaled_size, self.scaled_size)
                    colliders.append(rect)
        return colliders

    def create_teleports(self):
        """
        Create rectangles to be used as colliders for teleport check
        :return: list of pygame rect objects
        """
        size = self.scaled_size
        teleports = []
        tp_index = int(self.tiled_map.properties['tp_layer_index'])
        for x, y, image in self.tiled_map.get_layer_by_name('teleports').tiles():
            rect = pg.Rect(x * size, y * size, size / 2, size / 2)  # collision occurs too early if size is not halfed
            p = self.tiled_map.get_tile_properties(x, y, tp_index)
            pos_x = int(p['pos_x'])
            pos_y = int(p['pos_y'])
            map_f = MapsHelper.get_map(p['map_f'])
            world = p['world']
            tp = Teleport(rect, pos_x, pos_y, map_f, world)
            teleports.append(tp)

        return teleports

    def create_npcs(self):
        npcs = []
        for obj in self.tiled_map.get_layer_by_name('npc'):
            p = obj.properties
            name = p['npc']  # Reserved - Trader, Wizard
            x = int(obj.x) * self.scale_factor
            y = int(obj.y) * self.scale_factor
            if name == 'trader':
                npc = MapTrader(x, y)
            elif name == 'wizard':
                npc = MapWizard(x, y)
            else:
                party = p['party_members'].split(',') if 'party_members' in p.keys() else None
                bg = p['bg'] if 'bg' in p.keys() else None
                identifier = int(p['nid']) if 'nid' in p.keys() else None
                if identifier is not None and self.npc_registry.count(identifier) == 0:
                    npc = MapNPC(x, y, party, bg, identifier)
                else:
                    continue
            npcs.append(npc)

        return npcs

    def enter_battle(self, event):
        self.player_party.enter_battle()
        args_dict = {'player_party': self.player_party, 'party_members': event.npc.party, 'bg': event.npc.bg, 'id': event.npc.id}
        self.call_state(BattleState, args_dict)


class WorldMapState(MapState):
    def __init__(self, persistent):
        super().__init__(persistent)
        self.bg = None
        self.draw_colliders = False
        self.set_bg()

    def set_bg(self):
        settings = SettingsHelper()
        detailed_water = settings.get('world_water_tiled', False)
        if not detailed_water:
            self.bg = pg.Surface((self.screen_width, self.screen_height))
            self.bg.fill(pg.Color(self.tiled_map.background_color))

    def update(self, dt):
        super().update(dt)

    def draw(self, surface):
        super().draw(surface)
        size = self.scaled_size
        for layer in self.tiled_map.visible_layers:
            if layer.name == 'water' and self.bg is not None:
                continue
            for x, y, image in layer.tiles():
                scaled_image = pg.transform.scale(image, (size, size))
                surface.blit(scaled_image, self.camera.apply(pg.Rect(x * size, y * size, size, size)))
            surface.blit(self.player_party.image, self.camera.apply(self.player_party.rect))

        if self.draw_colliders:
            col_fill = pg.Surface((self.tile_size * 2, self.tile_size * 2))
            col_fill.fill(pg.Color('black'))
            for rect in self.colliders:
                surface.blit(col_fill, self.camera.apply(rect))
        if self.menu is not None:
            self.menu.draw(surface)
        if self.pause_menu is not None:
            self.pause_menu.draw(surface)
            
    def exit(self, args_dict=None):
        super(WorldMapState, self).exit(args_dict)

    def on_return(self, callback):
        self.tiled_map = load_pygame(callback['map_f'])
        self.player_party = callback['player_party']
        self.player_party.set_pos(callback['pos_x'], callback['pos_y'])
        self.npc_registry = callback['npc_reg']
        self.player_party.reset_scale()  # Reset player party's rect scale after local map

    def get_event(self, event):
        super().get_event(event)
        if event.type == TeleportEvent and event.teleport.world == 'localworld':
            tp = event.teleport
            args_dict = {'player_party': self.player_party, 'npc_reg': self.npc_registry, 'pos_x': tp.pos_x, 'pos_y': tp.pos_y, 'map_file': tp.map_f}
            self.call_state(LocalMapState, args_dict)
        if event.type == pg.KEYDOWN and event.key == pg.K_c:
            self.draw_colliders = not self.draw_colliders


class LocalMapState(MapState):
    def __init__(self, persistent):
        super().__init__(persistent)
        self.player_party.set_pos(persistent['pos_x'], persistent['pos_y'])
        self.npc_registry = persistent['npc_reg']
        self.set_bg()
        self.player_party.scale_up()  # Player party's sprite is 2-x scaled on local map

    def set_bg(self):
        self.bg = pg.Surface((self.screen_width, self.screen_height))
        self.bg.fill(pg.Color(self.tiled_map.background_color))

    def draw(self, surface):
        super().draw(surface)
        size = self.scaled_size
        scaled_party = self.player_party.get_scaled()  # Sprite changes every frame,so it has to be scaled every time
        for layer in self.tiled_map.visible_layers:
            for x, y, image in layer.tiles():
                scaled_image = pg.transform.scale(image, (size, size))
                surface.blit(scaled_image, self.camera.apply(pg.Rect(x * size, y * size, size, size)))
            surface.blit(scaled_party, self.camera.apply(self.player_party.rect))
        # Draw NPCs
        for i in self.npcs:
            surface.blit(i.image, self.camera.apply(i.rect))

        if self.menu is not None:
            self.menu.draw(surface)
        if self.pause_menu is not None:
            self.pause_menu.draw(surface)

    def get_event(self, event):
        super().get_event(event)
        if event.type == TeleportEvent and event.teleport.world == 'overworld':
            tp = event.teleport
            callback_args = {'player_party': self.player_party, 'npc_reg': self.npc_registry, 'pos_x': tp.pos_x, 'pos_y': tp.pos_y, 'map_f': tp.map_f}
            self.exit(callback_args)
        elif event.type == TeleportEvent and event.teleport.world == 'localworld':
            tp = event.teleport
            self.tiled_map = load_pygame(tp.map_f)
            self.player_party.set_pos(tp.pos_x, tp.pos_y)

    def on_return(self, callback):
        self.player_party.exit_battle()
        if 'flee' in callback.keys():  # Player escaped from battle
            return
        else:
            self.player_party.add_items(callback['loot'])
            self.player_party.add_exp(callback['exp'])
            self.player_party.gold += callback['gold']
            self.remove_npc(callback['id'])

    def remove_npc(self, identifier):
        for i in self.npcs:
            if hasattr(i, 'id') and i.id == identifier:
                self.npcs.remove(i)
                self.npc_registry.append(identifier)


class BattleState(GameState):  # TODO: Animations
    """
    Game state in which battle with NPC's is handled
    """

    def __init__(self, persistent):
        super().__init__(persistent)
        self.screen_width = self.screen_rect.width
        self.screen_height = self.screen_rect.height
        self.player_party = self.persist['player_party']
        self.bg = None
        self.pause_menu = None
        self.npc_party = None
        self.npc_iter = None  # iterator over npc list
        self.npc_turn = False  # Select character from npc party if true
        self.current_character = None
        self.current_window = None
        self.loot = []
        self.gold = 0  # Total amount of gold party gets for battle
        self.experience = 0  # Total amount of experience every member get for battle
        self.sprites = []
        self.windows = []
        self.dialog_width = self.screen_width * 0.3
        self.dialog_height = self.screen_height * 0.298
        self.dialog = None  # Action select dialog
        self.last_action = None  # Save last action to know what to do with selected NPC
        self.load_npc()
        self.calculate_loot()
        self.load_sprites()
        self.set_ui()
        self.choose_player_character()

    def update(self, dt):
        super().update(dt)
        if self.pause_menu is not None:
            if self.pause_menu.quit:
                self.pause_menu = None
                self.on_resume()

    def load_npc(self):
        """
        Load npc party information
        """
        self.npc_party = []

        members = self.persist['party_members']

        for i in members:
            self.npc_party.append(eval(i)())

        self.npc_iter = iter(self.npc_party)

    def calculate_loot(self):
        """
        Calculate loot and experince for npc's
        """

        for i in self.npc_party:
            self.loot.extend(i.get_loot())
            self.gold += i.gold
            self.experience += i.EXP

    def load_sprites(self):
        """
        Loads sprites of player and npc characters and places them on screen, appends to sprites list
        """
        helper = SpritesHelper()
        image = pg.image.load(helper.get_bg(self.persist['bg']))
        rect = image.get_rect()
        rect.height = self.screen_height
        rect.width = self.screen_width
        image = pg.transform.scale(image, (self.screen_width, self.screen_height))
        self.bg = (image, rect)

        x = self.screen_width * 0.1
        y = self.screen_height * 0.3

        for i in self.npc_party:
            i.rect.x = x
            i.rect.y = y
            self.sprites.append((i.image, i.rect))
            y += i.rect.height + 10

        y = self.screen_height * 0.3
        x = self.screen_width * 0.8
        for i in self.player_party:
            i.battle_rect.x = x
            i.battle_rect.y = y
            self.sprites.append((i.battle_image, i.battle_rect))
            y += i.battle_rect.height + 10

    def set_ui(self):
        self.party_window = UI.PartyInfoWindow(self.screen_width * 0.498, self.screen_height * 0.698, self.screen_width * 0.5, self.screen_height * 0.3, self.player_party)
        self.npc_window = UI.NPCInfoWindow(0, self.screen_height * 0.698, self.screen_width * 0.5, self.screen_height * 0.3, self.npc_party)
        self.status_bar = UI.StatusBar(0, self.screen_height * 0.65, self.screen_width * 0.998, self.screen_height * 0.05, 2000)
        self.windows.append(self.party_window)
        self.windows.append(self.npc_window)
        self.windows.append(self.status_bar)

    def draw(self, surface):
        surface.blit(*self.bg)
        for i in self.npc_party:
            surface.blit(i.image, i.rect)
        for i in self.player_party.get_battle_sprites():
            surface.blit(*i)
        for i in self.windows:
            i.draw(surface)
        if self.dialog is not None:
            self.dialog.draw(surface)
        if self.pause_menu is not None:
            self.pause_menu.draw(surface)

    def get_event(self, event):
        super().get_event(event)
        if event.type is BattleEvent:
            self.handle_battle_events(event)
        if event.type is MenuQuitEvent:
            self.pause_menu = None
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:  # Handle pause menu (de)activation
            self.toggle_pause_menu()
        if event.type == pg.KEYDOWN and event.key == pg.K_q:
            self.cancel_action()
        elif self.pause_menu is not None and event.type == pg.KEYDOWN:  # Let the pause menu handle input first
            self.pause_menu.update(event.key)
        elif self.dialog is not None and event.type == pg.KEYDOWN:
            self.dialog.update(event.key)
        elif self.current_window is not None and event.type == pg.KEYDOWN:
            self.current_window.update(event.key)

    def handle_battle_events(self, event):
        if event.sub == Battle.ActionSelected:
            self.take_action(event.action)
        if event.sub == Battle.TargetSelected:
            self.apply_action(event.npc)
        if event.sub == Battle.CharacterKO:
            self.knock_out(event.pc)
        if event.sub is Battle.NextTurn:
            if hasattr(event, 'status'):
                self.status_bar.set_status(event.status)
            self.next_turn()
        if event.sub is Battle.GameOver:
            self.game_over()
        if event.sub is Battle.BattleWon:
            self.win_battle()
        if event.sub is Battle.StatusUpdate:
            self.status_bar.set_status(event.status)
        if event.sub is Battle.AICall:
            self.call_ai()
            self.wait(1000)
        if event.sub is Battle.SpellSelected:
            self.dialog = None
            self.last_action_func = event.spell
            self.functor_target()
        if event.sub is Battle.ItemSelected:
            self.dialog = None
            self.last_action_func = event.item
            self.functor_target()

    def toggle_pause_menu(self):
        if self.pause_menu is None:
            self.on_pause()
            width = self.screen_width / 4
            height = self.screen_height / 4
            x = self.screen_width / 2 - width / 2
            y = self.screen_height / 2 - height / 2
            self.pause_menu = UI.PauseWindow(x, y, width, height)
        else:
            self.pause_menu = None
            self.on_resume()

    def choose_player_character(self):
        try:
            self.party_window.disable()
            self.current_character = self.player_party.get_next_alive()
            self.party_window.set_current(self.current_character)
            self.call_action_menu()
        except StopIteration:
            self.party_window.disable()
            self.npc_turn = True
            self.raise_event(Battle.NextTurn)

    def choose_npc_character(self):
        try:
            self.current_character = next(self.npc_iter)
            self.raise_event(Battle.AICall)
        except StopIteration:
            self.npc_turn = False
            self.current_character = None
            self.npc_iter = iter(self.npc_party)
            self.npc_window.disable()
            self.raise_event(Battle.NextTurn)

    def next_turn(self):
        if self.npc_turn is True:
            self.choose_npc_character()
        else:
            self.choose_player_character()

    def call_action_menu(self):
        self.dialog = UI.SelectActionWindow(self.screen_width / 2 - self.dialog_width, self.screen_height * 0.7, self.dialog_width, self.dialog_height)

    def call_spells_menu(self):
        player = self.current_character
        self.dialog = UI.SelectSpellWindow(self.screen_width / 2 - self.dialog_width, self.screen_height * 0.7, self.dialog_width, self.dialog_height, player)

    def call_items_menu(self):
        items = self.player_party.get_usable_items()
        self.dialog = UI.SelectItemWindow(self.screen_width / 2 - self.dialog_width, self.screen_height * 0.7, self.dialog_width, self.dialog_height, items)

    def take_action(self, action):
        """
        Set action target selection state for specified action
        :param action:  Action enum
        """
        self.dialog = None
        if action == Actions.Attack:
            self.last_action = action
            self.current_window = self.npc_window
            self.current_window.enable()
        if action == Actions.Magic:
            if len(self.current_character.spells) > 0:
                self.last_action = action
                self.party_window.disable()
                self.call_spells_menu()
            else:
                self.status_bar.set_status('{} has no spells :('.format(self.current_character.name))
                self.call_action_menu()
        if action == Actions.Item:
            if len(self.player_party.get_usable_items()) > 0:
                self.last_action = action
                self.party_window.disable()
                self.call_items_menu()
            else:
                self.status_bar.set_status('Party has no usable items')
                self.call_action_menu()
        if action == Actions.Flee:
            if self.flee() == False:
                self.call_action_menu()

    def apply_action(self, npc):
        """
        Apply action on selected target
        :param npc: target npc
        """
        if self.last_action == Actions.Attack:
            dmg = self.current_character.DMG
            npc.apply_damage(dmg)
            status = '{} dealt {} DMG to {}'.format(self.current_character.name, dmg, npc.name)
            self.status_bar.set_status(status)
        elif self.last_action == Actions.Magic:
            if not self.action_magic(npc):
                return
        elif self.last_action == Actions.Item:
            if not self.action_item(npc):
                return
        self.npc_window.update_items()
        self.party_window.update_items()
        self.current_window.disable()
        self.current_window = None
        self.last_action = None
        self.last_action_func = None
        self.next_turn()

    def action_magic(self, npc):
        if self.current_character.MP >= self.last_action_func.mp:
            if self.last_action_func.check_appliable(npc):
                self.current_character.cast_spell(self.last_action_func, npc)
                status = '{} casted {} on {}'.format(self.current_character.name, self.last_action_func, npc.name)
                self.status_bar.set_status(status)
                return True
            else:
                status = 'Cannot cast {} on {}'.format(self.last_action_func, npc.name)
                self.status_bar.set_status(status)
                return False
        else:
            status = 'Not enough mana to cast {}'.format(self.last_action_func)
            self.status_bar.set_status(status)
            return False

    def action_item(self, npc):
        if self.last_action_func.check_appliable(npc):
            self.last_action_func.apply_effect(npc)
            self.player_party.remove_item(self.last_action_func)
            status = '{} used on {}'.format(self.last_action_func, npc.name)
            self.status_bar.set_status(status)
            return True
        else:
            status = 'Cannot use {} on {}'.format(self.last_action_func, npc.name)
            self.status_bar.set_status(status)
            return False

    def cancel_action(self):
        """
        Returns to action select menu
        """
        if self.npc_turn is False and self.last_action:
            self.dialog = None
            if self.current_window:
                self.current_window.disable()
                self.current_window = None
            self.call_action_menu()

    def functor_target(self):
        """
        Enable NPC or Player window to choose spell target
        """
        if self.last_action_func.side is Sides.NPC:
            self.current_window = self.npc_window
            self.current_window.enable()
        else:
            self.current_window = self.party_window
            self.current_window.enable()

    def call_ai(self):
        """
        Call current NPC's AI function
        """
        self.npc_window.disable()
        self.npc_window.set_current(self.current_character)
        self.current_character.decide(self.player_party, self.npc_party)
        for i in self.windows:
            if i is not self.status_bar:
                i.update_items()

    def raise_event(self, subevent):
        event = pg.event.Event(BattleEvent, {'sub': subevent})
        pg.event.post(event)

    def knock_out(self, character):
        """
        Remove character from battle if it's NPC, block in UI and change sprite if player
        :param character: BaseNPC or BaseMember instance
        """
        if isinstance(character, BaseNPC):
            self.npc_party.remove(character)
            self.npc_window.refresh_items()
            if len(self.npc_party) == 0:
                self.raise_event(Battle.BattleWon)
        elif isinstance(character, BaseMember):
            if len(self.player_party.get_alive()) == 0:
                self.raise_event(Battle.GameOver)


    def game_over(self):  # TODO: Game over screen
        """
        Called when player loses the battle
        """
        self.reset_states()

    def win_battle(self):
        """
        Called when all NPC's are defeated.Returns to previous map state
        """
        args_dict = {'loot': self.loot, 'gold': self.gold, 'exp': self.experience, 'id': self.persist['id']}
        self.exit(args_dict)

    def flee(self):
        """
        Called when player wants to escape battle.Possible only if all members are alive
        """
        if len(self.player_party.get_alive()) == 4:
            self.exit({'flee': True})
        else:
            self.status_bar.set_status("Cannot flee: you have KO'ed members")
            return False

    def wait(self, time):
        """
        waits specified amount of time (in millis).Blocks UI thread!!!
        :param time: time (in milliseconds)
        """
        pg.time.delay(time)
