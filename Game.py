#!/usr/bin/py
# -*- coding: utf-8 -*-
import pygame as pg
import Events as evs
from GameStates import StateStack


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
            if event.type == evs.StateCallEvent:
                self.state_stack.push(event.state(event.args))
                self.state_stack.set_persistent(event.args)
            elif event.type == evs.StateExitEvent:
                self.state_stack.pop()
                self.state_stack.send_callback(event.args)
            elif event.type is evs.StackResetEvent:
                self.state_stack.reset()
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
