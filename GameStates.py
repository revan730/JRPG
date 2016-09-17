# -*- coding: utf-8 -*-

import pygame as pg
import Events as evs

class StateStack:
    def __init__(self, start_state=None):
        self.states = []

    def is_empty(self):
        return self.items == []

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

    def exit(self,args_dict=None):
        """
        Called when state ends and game should return to previous state
        :return:
        """
        exit_event = pg.event.Event(evs.StateExitEvent, args_dict)
        pg.event.post(exit_event)

    def call_state(self, args_dict=None):
        call_event = pg.event.Event(evs.StateCallEvent, args_dict)
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
            args_dict = {'state':'TESTTRANSFER', 'args': {'text': 'Kirov reporting'}}
            self.call_state(args_dict)
    def exit(self):
        super().exit()

    def call_state(self, args_dict=None):
        super(SplashState, self).call_state(args_dict)
        print('TestTransferState called,should be printing some red shit now')

    def on_return(self, callback):
        print('Callback from called state:{}'.format(callback['r_val']))

    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        surface.blit(self.text, self.text_rect)


class TestTransferState(GameState):
    def __init__(self, persistent):
        super().__init__(persistent)
        self.font = pg.font.Font(None, 24)
        self.text = self.font.render(self.persist['text'], True, pg.Color('red'))
        self.text_rect = self.text.get_rect(center=self.screen_rect.center)
        self.bg = pg.Surface((800, 640))
        self.bg.fill(pg.Color('black'))

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN and event.key == pg.K_s:
            args_dict = {'state': '', 'args': {'r_val': 42}}
            self.exit(args_dict)

    def exit(self, args_dict=None):
        super(TestTransferState, self).exit(args_dict)
        print('transfer state ended,should return to splash state')

    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        surface.blit(self.text, self.text_rect)