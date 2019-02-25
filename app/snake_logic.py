#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 15:08:30 2019

@author: joelnewman
"""

class Game():
    def __init__(self):
        self.id = ""
        self.turn = 0
        self.board = Board()
    
        

class Board():
    def __init__(self):
        ''' where all of the board specific data lives'''
        self.height = 0
        self.width = 0
        self.food = {}
        self.snakes = {}

class Snake():
    def __init__(self):
        ''' This is the initialization of the snake '''
        self.id = ""
        self.name = ""
        self.health = 0
        self.body = {}
