# -*- coding: utf-8 -*-

import pygame as pg
from Events import StateCallEvent, StateExitEvent
from ResourceHelpers import StringsHelper
import UI as ui


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
        self.next_state = None
        self.screen_rect = pg.display.get_surface().get_rect()
        self.persist = persistent

    def get_event(self, event):
        pass

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
        exit_event = pg.event.Event(StateExitEvent, args_dict)
        pg.event.post(exit_event)

    def call_state(self, args_dict=None):
        call_event = pg.event.Event(StateCallEvent, args_dict)
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
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN and event.key == pg.K_t:
            args_dict = {'state': 'MAINMENU', 'args': None}
            self.call_state(args_dict)

    def exit(self, args_dict=None):
        super().exit()

    def call_state(self, args_dict=None):
        super(SplashState, self).call_state(args_dict)

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
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN and (event.key == pg.K_s or event.key == pg.K_DOWN):
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
            pass
        elif self.cursor_pos == 1:
            pass
        elif self.cursor_pos == 2:
            pass
        elif self.cursor_pos == 3:
            pass
        elif self.cursor_pos == 4:
            self.quit = True
