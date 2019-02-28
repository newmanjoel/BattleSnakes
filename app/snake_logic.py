#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 15:08:30 2019

@author: joelnewman
"""

import networkx as nx
import json
import logging
import cmath
import math

class Prev():
    def __init__(self):
        self.last_direction = 'North'
    
    def get_new_direction(self, absolute_direction):
        directions = {"North":{"North": "up", "East":"right", "South": "down", "West":"left"},
                      "East":{},
                      "South":{},
                      "West":{}
                      }
        return directions[self.last_direction][absolute_direction]

class Game():
    def __init__(self, play_state):
        self.stored_legal_direction = []
        self.id = play_state["game"]["id"]
        self.turn = int(play_state["turn"])
        self.board = Board(play_state["board"])
        self.my_snake = play_state["you"]["id"]
        self.board.set_my_snake(self.my_snake)
    
    def load_data(self, play_state):
        if self.id == play_state["game"]["id"]:
            logging.info("Loading Data into the wrong game")
        self.turn = int(play_state["turn"])
        self.board.load_data(play_state["board"])
        self.my_snake = play_state["you"]["id"]
        self.board.set_my_snake(self.my_snake)
    
    def legal_moves(self):
        try:
            head = (self.board.ms.head.x, self.board.ms.head.y)
        except Exception as e:
            logging.critical("{}".format(e))
            self.stored_legal_direction = []
            return None
        nodes = list(nx.neighbors(self.board.board, head))
        logging.info("The current head has {} legal nodes that are {}".format(len(nodes), nodes))
        
        #directions = ['up', 'down', 'left', 'right']
        legal_direction = []
        self.stored_legal_direction = []
        for node in nodes:
            # node contains 2 elements
            x_diff = head[0] - node[0] # x value
            y_diff = head[1] - node[1] # y value
            
            if x_diff > 0:
                legal_direction.append('left')
                self.stored_legal_direction.append("L")
            elif x_diff < 0:
                legal_direction.append('right')
                self.stored_legal_direction.append("R")
            elif y_diff > 0:
                legal_direction.append('up')
                self.stored_legal_direction.append("U")
            elif y_diff < 0:
                legal_direction.append('down')
                self.stored_legal_direction.append("D")
            if len(legal_direction) == 4:
                logging.critical("non-legal move, nodes:{}, node: {}, x_diff: {}, y_diff: {}".format(
                        nodes, node, x_diff, y_diff))
        return legal_direction
    
    

class Board():
    def __init__(self, play_state):
        ''' where all of the board specific data lives'''
        self.height = int(play_state["height"])
        self.width = int(play_state["width"])
        self.food = []
        self.snakes = []
        self.distances = {}
        self.board = nx.grid_2d_graph(self.height, self.width)
        self.load_data(play_state)
        logging.info("board created with playspace of {},{}".format(self.height, self.width))
    
    def __repr__(self):
        text = ""
        text += "Snakes:\n"
        for snake in self.snakes:
            text += "\t{}\n".format(str(snake))
        text += "Food:\n"
        for food in self.food:
            text += "\t{}\n".format(str(food))
        return text
    
    def __str__(self):
        return self.__repr()
    
    def set_my_snake(self, snake_id):
        self.ms = None
        for snake in self.snakes:
            if snake.id == snake_id:
                self.ms = snake
                break
        
    
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
            
    def calc_vectors(self, snake_id):
        '''
        Calculate how much the snake or food should push or pull the our snake
        '''
        mann_dist = []
        
        for snake in self.snakes:
            if snake.id != snake_id:
                mann_dist.append(self.ms.head*snake.head)
        
        for food in self.food:
            mann_dist.append(self.ms.head*food)
        
        return mann_dist
    
    def check_index(self, x, y):
        for food in self.food:
            if x==food.x and y==food.y:
                return "F"
        for snake in self.snakes:
            for link in snake.body:
                if x == link.x and y == link.y:
                    return "B"
            if x==snake.head.x and y==snake.head.y:
                return "S"
        if (x, y) in self.board:
            return " "
        return "?"
            
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
        return "{} | {} | {} {}".format(self.name, self.health, self.head, self.bodies())
    
    def bodies(self):
        body_data = ""
        for link in self.body:
            body_data = body_data + " " + str(link)
        return body_data
        
class Point():
    def __init__(self, lx = -1, ly = -1):
        self.x = lx
        self.y = ly
        
    def __str__(self):
        return "({},{})".format(self.x, self.y)
    
    def __repr__(self):
        return "({},{})".format(self.x, self.y)
    
    def __getitem__(self, index):
        return [self.x, self.y]
    
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
    def __abs__(self):
        return (self.x * self.x + self.y * self.y)**0.5
    
    def __mul__(self, other):
        z = complex(self.y, self.x)
        y = complex(other.y, other.x)
        return z-y
    
    
class Body(Point):
    def __init__(self, body_info):
        self.x = int(body_info["x"])
        self.y = int(body_info["y"])
    
    def __mul__(self, other):
        # I want to overload this to go the other way
        z = complex(self.y, self.x)
        y = complex(other.y, other.x)
        return y-z
    
        

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

        self.start = json.loads(self.start)
        
