#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 15:08:30 2019

@author: joelnewman
"""

import networkx as nx
import logging

class Game():
    def __init__(self, play_state):
        self.id = play_state["game"]["id"]
        self.turn = int(play_state["turn"])
        self.board = Board(play_state["board"])
    
    def load_data(self, play_state):
        if self.id == play_state["game"]["id"]:
            logging.info("Loading Data into the wrong game")
        self.turn = int(play_state["turn"])
        self.board.load_data(play_state["board"])
        
    

class Board():
    def __init__(self, play_state):
        ''' where all of the board specific data lives'''
        self.height = int(play_state["height"])
        self.width = int(play_state["width"])
        self.food = []
        self.snakes = []
        self.distances = {}
        self.board = nx.grid_2d_graph(self.height, self.width)
        logging.info("board created with playspace of {},{}".format(self.height, self.width))
    
    def load_data(self, play_state):
        ''' 
        Used to load the data into the board from the json data provided
        by the server
        '''
        self.snakes = []
        for snek in play_state["snakes"]:
            self.snakes.append(Snake(snek))
        
        self.food = []
        for fuud in play_state["food"]:
            self.food.append(Food(fuud))
        
        self.possible_moves()
        self.calc_distances()
        
    def possible_moves(self):
        '''
        Remove all the bodies from being a valid move.
        Moving to where a head currently sits is a valid move

        TODO: Confirm that this is correct about the head positions
        '''
        for snake in self.snakes:
            for body in snake.body:
                try:
                    self.board.remove_node((body.x, body.y))
                except Exception as e:
                    logging.critical(e)
    
    def calc_distances(self):
        '''
        Calculate how far each node is from every other node.
        Note that this only calculates the distance, not the path.
        '''
        self.distances = dict(nx.all_pairs_shortest_path_length(self.board))
            

class Snake():
    def __init__(self, snake_info):
        ''' This is the initialization of the snake '''
        self.id = snake_info["id"]
        self.name = snake_info["name"]
        self.health = int(snake_info["health"])
        self.body = []
        self.head = None
        for link in snake_info["body"]:
            if(self.head is None):
                self.head = Body(link)
            else:
                self.body.append(Body(link))
    
    def __str__(self):
        body_data = ""
        for link in self.body:
            body_data = body_data + " " + str(link)
        return "{} | {} | {} {}".format(self.name, self.health, self.head, body_data)
            
class Point():
    def __init__(self):
        self.x = -1
        self.y = -1
    def __str__(self):
        return "({},{})".format(self.x, self.y)
    
class Body(Point):
    def __init__(self, body_info):
        self.x = int(body_info["x"])
        self.y = int(body_info["y"])

class Food(Point):
    def __init__(self, food_info):
        self.x = int(food_info["x"])
        self.y = int(food_info["y"])

class TD:
    def __init__(self):
        self.turn = """{
  "game": {
    "id": "game-id-string"
  },
  "turn": 4,
  "board": {
    "height": 15,
    "width": 15,
    "food": [
      {
        "x": 1,
        "y": 3
      }
    ],
    "snakes": [
      {
        "id": "snake-id-string",
        "name": "Sneky Snek",
        "health": 90,
        "body": [
          {
            "x": 1,
            "y": 3
          },
          {
            "x": 2,
            "y": 3
          },
          {
            "x": 3,
            "y": 3
          }
        ]
      }
    ]
  },
  "you": {
    "id": "snake-id-string",
    "name": "Sneky Snek",
    "health": 90,
    "body": [
      {
        "x": 1,
        "y": 3
      }
    ]
  }
}
"""

        self.start = """{
  "game": {
    "id": "game-id-string"
  },
  "turn": 4,
  "board": {
    "height": 15,
    "width": 15,
    "food": [
      {
        "x": 1,
        "y": 3
      }
    ],
    "snakes": [
      {
        "id": "snake-id-string",
        "name": "Sneky Snek",
        "health": 90,
        "body": [
          {
            "x": 1,
            "y": 3
          },
          {
            "x": 2,
            "y": 3
          },
          {
            "x": 3,
            "y": 3
          }
        ]
      }
    ]
  },
  "you": {
    "id": "snake-id-string",
    "name": "Sneky Snek",
    "health": 90,
    "body": [
      {
        "x": 1,
        "y": 3
      }
    ]
  }
}
"""
