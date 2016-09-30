# -*- coding: utf-8 -*-

import pygame as pg
from Events import StateCallEvent, StateExitEvent
from ResourceHelpers import StringsHelper, SettingsHelper
import UI as ui
from Player import PlayerParty, Camera
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

    def set_persistent(self, persistent):
        self.peek().persistent = persistent

    def update(self, dt):
        """
        Call update method of current state
        :param dt: time since last frame
        :return:
        """

        self.peek().update(dt)

    def get_event(self, event):
        """
        Gives one specific event for state to process
        :param event: event passed to game state
        :return:
        """
        self.peek().get_event(event)

    def send_callback(self, callback):
        self.peek().on_return(callback)


class GameState:

    def __init__(self, persistent=None):
        self.quit = False
        self.finish = False
        self.screen_rect = pg.display.get_surface().get_rect()
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

    def exit(self, args_dict=None):
        """
        Called when state ends and game should return to previous state
        :param args_dict: dictionary of callback arguments,which will be received by previous state in stack
        :return:
        """
        exit_event = pg.event.Event(StateExitEvent, {'state': '','args': args_dict})
        pg.event.post(exit_event)

    def call_state(self, state, args_dict=None):
        event_args = {'state': state, 'args': args_dict}
        call_event = pg.event.Event(StateCallEvent, event_args)
        pg.event.post(call_event)

    def on_return(self, callback):
        """
        Executed when called state was successfully ended
        :param callback: callback from called state (e.g. list of monster loot,new player coordinates)
        :return:
        """
        pass


class SplashState(GameState):
    def __init__(self):
        super().__init__()
        self.font = pg.font.Font(None, 24)
        self.text = self.font.render('JRPG Engine', True, pg.Color('dodgerblue'))
        self.text_rect = self.text.get_rect(center=self.screen_rect.center)
        self.bg = pg.Surface((800, 640))
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


class MainMenuState(GameState):
    def __init__(self, persistent=None):
        super().__init__(persistent)
        helper = StringsHelper("en")
        self.font = pg.font.Font(None, 24)
        self.bg = pg.Surface((800, 640))
        self.bg.fill(pg.Color('black'))
        menu_strings = helper.get_strings("main_menu")
        self.cursor_pos = 0

        x = self.bg.get_width() / 2
        y = 250

        self.menu_items = []
        for i in sorted(menu_strings.keys()):
            self.menu_items.append(ui.MenuItem(i, menu_strings[i], None, 36, 'white', 'dodgerblue', x, y))
            y += 30

    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        for i in self.menu_items:
            surface.blit(i.text, i.rect)

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
        if self.cursor_pos == 0:
            args_dict = {'player_party': None, 'pos_x': 0, 'pos_y': 0, 'map_file': 'resources/maps/world_test.tmx'}
            self.call_state(WorldMapState, args_dict)
        elif self.cursor_pos == 1:
            pass
        elif self.cursor_pos == 2:
            pass
        elif self.cursor_pos == 3:
            pass
        elif self.cursor_pos == 4:
            self.quit = True


class WorldMapState(GameState):
    def __init__(self, persistent=None):
        super().__init__(persistent)
        #self.player_party = self.persist['player_party']
        settings = SettingsHelper()
        detailed_water = settings.get('world_water_tiled', False)
        self.tiled_map = load_pygame(self.persist['map_file'])
        self.player_party = PlayerParty(360, 360)
        self.camera = Camera(Camera.camera_configure_world, 800, 800)
        self.colliders = self.create_colliders()
        self.tile_size = self.tiled_map.tilewidth
        self.scale_factor = 2 # Tiles are 16x16,so we must draw them 2 times larger
        self.water = None
        if not detailed_water:
            self.water = pg.Surface((800, 640))
            self.water.fill(pg.Color(self.tiled_map.background_color))

    def update(self, dt):
        self.player_party.update(self.colliders)
        self.camera.update(self.player_party)

    def draw(self, surface):
        scaled_size = self.tile_size * self.scale_factor
        if self.water:
            surface.blit(self.water, (0, 0))
        for layer in self.tiled_map.visible_layers:
            if layer.name == 'water' and self.water is not None:
                continue
            for x, y, image in layer.tiles():
                scaled_image = pg.transform.scale(image, (scaled_size, scaled_size))
                surface.blit(scaled_image, self.camera.apply(pg.Rect(x * scaled_size, y * scaled_size, scaled_size, scaled_size)))
            surface.blit(self.player_party.image, self.camera.apply(self.player_party.rect))
            
    def exit(self, args_dict=None):
        super(WorldMapState, self).exit(args_dict)
                
    def get_event(self, event):
        super().get_event(event)
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.call_menu()
        elif event.type == pg.KEYDOWN and event.key == pg.K_w:
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

            
    def call_menu(self):  # TODO: It's still not done!!
        self.exit()

    def create_colliders(self):
        """
        Create rectangles to be used as colliders for collision check
        :return: list of pygame rect objects
        """
        colliders = []
        tile_width = self.tiled_map.tilewidth
        for i in range(0, len(self.tiled_map.layers)):
            for x, y, image in self.tiled_map.layers[i].tiles():
                p = self.tiled_map.get_tile_properties(x, y, i)
                if p['walkable'] == 'false':
                    width = p['width']
                    height = p['height']
                    rect = pg.Rect(x * 32, y * 32, width, height)
                    colliders.append(rect)
        return colliders







