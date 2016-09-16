#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import pygame as pg


class Game:
    """
    Main engine class responsible for event handling,rendering and running game states
    """

    def __init__(self, screen, states, start_state):
        '''
        Game engine initializator
        :param screen: pygame display
        :param states: dict of game states
        :param start_state: name of starting state
        '''

        self.finish = False
        self.screen = screen
        self.clock = pg.time.Clock()
        self.fps = 60
        self.states = states
        self.state_name = start_state
        self.state = self.states[self.state_name]

    def event_loop(self):
        '''
        Handles all events
        '''
        for event in pg.event.get():
            self.state.get_event(event)

    def set_state(self, state_name, args):
        '''
        Switch to specified state
        :param state_name: name of state to switch on
        :param args: dictionary of arguments to be used by state
        '''
        self.state_name = state_name
        self.state = self.states[self.state_name]

    def update(self, dt):
        '''
        Handles active state update
        :param dt: time in millis since last frame
        '''

        self.state.update(dt)

    def draw(self):
        """
        Pass display to active state for drawing
        """

        self.state.draw(self.screen)

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
