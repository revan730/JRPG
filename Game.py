#!/usr/bin/py
# -*- coding: utf-8 -*-
import pygame as pg
import Events as evs
from Enums import GameEnum as sub
from GameStates import StateStack
import pickle as pic
import copy


class Game:
    """
    Main engine class responsible for event handling,rendering and running game states
    """

    def __init__(self, screen, start_state):
        """
        Game engine initializator
        :param screen: pygame display
        :param start_state: name of starting state
        """

        self.finish = False
        self.screen = screen
        self.clock = pg.time.Clock()
        self.fps = 60
        self.state_stack = StateStack()
        self.state_stack.push(start_state())

    def event_loop(self):
        """
        Handles all events
        """
        for event in pg.event.get():
            if event.type == evs.EngineEvent:
                if event.sub == sub.StateCallEvent:
                    self.state_stack.push(event.state(event.args))
                    self.state_stack.set_persistent(event.args)
                elif event.sub == sub.StateExitEvent:
                    self.state_stack.pop()
                    self.state_stack.send_callback(event.args)
                elif event.sub is sub.StackResetEvent:
                    self.state_stack.reset()
                elif event.sub is sub.GameSaveEvent:
                    self.save_game(event.path)
                elif event.sub is sub.GameLoadEvent:
                    self.load_game(event.path)
            else:
                self.state_stack.get_event(event)

    def update(self, dt):
        """
        Handles active state update
        :param dt: time in millis since last frame
        """

        self.state_stack.update(dt)
        if self.state_stack.peek().quit:
            self.finish = True

    def draw(self):
        """
        Pass display to active state for drawing
        """

        self.state_stack.peek().draw(self.screen)

    def save_game(self, path):
        """
        Save current game state in file
        :param path: string - path to game save file
        """
        try:
            file = open(path, "wb")
            for i in self.state_stack.states:
                i.on_save()
            pic.dump(self.state_stack, file)
            for i in self.state_stack.states:
                i.on_load()
        except IOError or pic.PicklingError as e:
            print("Game save error: {}".format(e))

    def load_game(self, path):
        """
        Load game state from file
        :param path: string - path to game save file
        """
        temp_stack = self.state_stack
        try:
            file = open(path, 'rb')
            self.state_stack = pic.load(file)
            for i in self.state_stack.states:
                i.on_load()
            del temp_stack
        except IOError or pic.UnpicklingError as e:
            print("Game load error: {}".format(e))
            self.state_stack = temp_stack

    def run(self):
        """
        Main game loop
        """

        while not self.finish:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pg.display.update()
