#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import cmath
import networkx as nx
import json
import logging


class Game():
    def __init__(self, play_state):
        ''' Used to store information thats 'above' the board. '''
        self.stored_legal_direction = []
        self.id = play_state["game"]["id"]
        self.turn = int(play_state["turn"])
        self.board = Board(play_state["board"])
        nx.set_node_attributes(self.board.board, True, "Safe")
        nx.set_edge_attributes(self.board.board, 1, "cost")
        self.my_snake = play_state["you"]["id"]
        self.board.set_my_snake(self.my_snake)
        self.safe_move_generation()
        self.cost()

    def legal_moves(self, x, y):
        '''
        This function calculates the legal moves from a given x,y location.

        TODO: Replace the two outputs with a dictionary for simplicity

        Parameters
        ----------
        x : int
            x location to check for legal moves
        y : int
            y location to check for legal moves

        Returns
        -------
        legal_directions : array of strings
            an array that contains the legal (u,d,l,r) all legal moves
            I dont care if they are safe or not.
        legal_nodes : array of nodes
            an array that contains the legal nodes that the snake can move to
        '''
        head = (x, y)
        logging.info("head at {}".format(head))
        try:
            nodes = list(nx.neighbors(self.board.board, head))
        except Exception as e:
            logging.critical("Could not find {} in nodes {}".format(head, self.board.board))
            return [[], []]
        logging.debug("The current head has {} legal nodes that are {}".format(len(nodes), nodes))

        legal_direction = []
        legal_nodes = []
        self.stored_legal_direction = []

        '''
        TODO: Replace this with the relative direction function
        '''
        for node in nodes:
            # node contains 2 elements
            x_diff = head[0] - node[0] # x value
            y_diff = head[1] - node[1] # y value

            if x_diff > 0:
                legal_direction.append('left')
                legal_nodes.append(node)
                self.stored_legal_direction.append("L")
            elif x_diff < 0:
                legal_direction.append('right')
                legal_nodes.append(node)
                self.stored_legal_direction.append("R")
            elif y_diff > 0:
                legal_direction.append('up')
                legal_nodes.append(node)
                self.stored_legal_direction.append("U")
            elif y_diff < 0:
                legal_direction.append('down')
                legal_nodes.append(node)
                self.stored_legal_direction.append("D")
            if len(legal_direction) == 4:
                logging.critical("non-legal move, nodes:{}, node: {}, x_diff: {}, y_diff: {}".format(
                        nodes, node, x_diff, y_diff))
        return [legal_direction, legal_nodes]

    def relative_direction(self, starting_node, ending_node):
        '''
        Returns the relative direction from a starting node to an ending node
        TODO: Convert this to a @staticmethod No need that this needs
              access to 'self'

        Parameters
        ----------
        starting_node : Point
            the tail of the vector we are trying to find, usually the head of
            the snake or other ROI

        ending_node : Point or Tuple
            the tip of the vector we are trying to find, usually the next step
            in a path

        Examples
        --------
        get the relative direction from two points

        >>> head = (1, 2)
        >>> tail = (2, 2)
        >>> relative_direction(head, tail)
        "right"
        >>> relative_direction(tail, head)
        "left"

        '''
        if isinstance(ending_node, tuple):
            x_diff = starting_node.x - ending_node[0]
            y_diff = starting_node.y - ending_node[1]
        else:
            x_diff = starting_node.x - ending_node.x
            y_diff = starting_node.y - ending_node.y
        logging.info("X: {}, Y: {}".format(x_diff, y_diff))
        if int(x_diff) > 0.1:
            return 'left'
        elif int(x_diff) < 0.1:
            return 'right'
        elif int(y_diff) > 0.1:
            return 'up'
        else:
            return 'down'

    def go_to_tail(self, head, tail):
        '''
        Generate the path to the tail of the snake

        Parameters
        ----------
        head : Point
            This is the starting point of the path, This will also be at the
            0th position in the path
        tail : Point
            This is the ending point. Technically it could be any point.
            If you wanted to use other points it should work no problem.

        Returns
        -------
        path : array
            a path that is from the head to the tail. If a path is not found
            an empty arary is returned
        '''

        head_t = (head.x, head.y)
        tail_t = (tail.x, tail.y)
        all_nodes = list(self.board.board.nodes)
        path = []
        if(head_t in all_nodes and tail_t in all_nodes):
            try:
                path =  nx.astar_path(self.board.board, head_t, tail_t, weight='cost')
            except Exception as e:
                logging.critical("Could not get from head to tail: {}".format(e))

        return path

    def go_to_closest_food(self, head):
        '''
        This will find the closes food. The food that is found is the closest
        food by actual path distance.

        Parameters
        ----------
        head : Point
            where the head of the snake is. This is the starting point of where
            to look for food

        Returns
        -------
        path : array
            a path going to the nearest food. if no path is found, an empty
            array is returned

        '''
        head_t = (head.x, head.y)
        target = (-1, -1)
        max_dist = 100
        path = []
        for i in self.board.food:
            x1 = i.x
            y1 = i.y
            x2 = head.x
            y2 = head.y
            dist = 1000
            try:
                '''
                Usage astar_path_length(G, source, target, heuristic=None, weight='weight')
                '''
                dist = nx.astar_path_length(self.board.board, (x2, y2), (x1, y1))
            except Exception as e:
                logging.warning("Cant find a path to food at {}".format(i))
            if dist <= max_dist:
                max_dist = dist
                target = (i.x, i.y)
        if target == (-1, -1):
            logging.critical("Found no food, chasing tail")
            try:
                path = self.go_to_tail(self.board.ms.head, self.board.ms.body[-1])
            except Exception as e:
                logging.critical("No path found")
        logging.info("Chasing the food at {},{}".format(target[0], target[1]))
        try:
            path = nx.astar_path(self.board.board, head_t, target)
        except Exception as e:
            logging.critical("No Path found")
        return path

    def cost(self):
        '''
        Creates the costmap that is used in A*

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        for snake in self.board.snakes:
            if snake == self.board.ms:
                continue
            added_cost = 5
            head = (snake.head.x, snake.head.y)
            for edge in nx.bfs_edges(self.board.board, source=head, depth_limit=1):
                logging.debug("adding the cost of {} edge to {}".format(added_cost, edge))
                self.board.board.edges[edge]['cost'] = added_cost

    def safe_move_generation(self):
        '''
        Generates the "safe" moves. This is supposed to identify the spots NOT
        to go. This should also eliminate tunnels and stuff

        Parameters
        ----------
        None

        Returns
        -------
        None

        '''
        something_changed = True
        amount_changed = 0
        while something_changed and amount_changed < 100:
            something_changed = False
            degrees = self.board.board.degree()
            for deg in degrees:
                if (deg[1] == 1 or deg[1] == 1) and self.board.board.nodes[deg[0]]["Safe"] == True:
                    amount_changed += 1
                    something_changed = True
                    logging.debug("Trying to change {}".format(deg[0]))
                    try:
                        self.board.board.nodes[deg[0]]["Safe"] = False
                    except Exception as e:
                        logging.critical("Cant set safe mode: {}".format(e))

        for snake in self.board.snakes:
            if snake == self.board.ms:
                continue
            head = (snake.head.x, snake.head.y)
            try:
                if len(self.board.ms.body) <= len(snake.body):
                    nodes = list(nx.neighbors(self.board.board, head))
                    for node in nodes:
                        logging.info("Setting node {} to unsafe".format(node))
                        self.board.board.nodes[node]["Safe"] = False
            except Exception as e:
                logging.critical("Cant set safe mode: {}".format(e))

    def safe_moves(self, directions, nodes):
        '''
        Identifies if a direction is safe or not from a given node with related
        directions.

        Parameters
        ----------
        directions : array
            a array containing the relative directions
        nodes : array of tuples
            an array containing the nodes related to the directions in the
            direction array

        Returns
        -------
        results : array
            an array containing a subset of the orignal directions matrix

        TODO: Replace the two input arrays with a dict to make things simpler
        '''
        results = []
        for i in range(len(nodes)):
            if self.board.is_safe(nodes[i]):
                logging.debug("{}, {}, found to be safe".format(nodes[i], directions[i]))
                results.append(directions[i])
        return results


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
        logging.debug("board created with playspace of {},{}".format(self.height, self.width))

    def __repr__(self):
        ''' The string representation of the board object '''
        text = ""
        text += "Snakes:\n"
        for snake in self.snakes:
            text += "\t{}\n".format(str(snake))
        text += "Food:\n"
        for food in self.food:
            text += "\t{}\n".format(str(food))
        return text

    def __str__(self):
        ''' The string representation of the board object '''
        return self.__repr__()

    def is_safe(self, node):
        ''' Checks if a given node is marked as being safe

        Parameters
        ----------
        node : point or tuple
            the point on the board that you want to check the safety of

        Returns
        -------
        results : boolean
            returns True if point is safe, returns false otherwise
        '''
        return self.board.nodes[(node)]["Safe"]

    def set_my_snake(self, snake_id):
        '''
        Sets the My Snake object (ms) based on the 'snake id'

        Parameters
        ----------
        snake_id : string
            unique string identify a snake. Note there is no checking to see
            if the id is contained in the snake set. Thats on you!

        Returns
        -------
        None
        '''
        self.ms = None
        for snake in self.snakes:
            if snake.id == snake_id:
                self.ms = snake
                break

    def load_data(self, play_state):
        '''
        Used to load the data into the board from the json data provided
        by the server

        Parameters
        ----------
        play_state : dict
            a dict that is created from parsing the data from the json data
            given to us from the battlesnake server

        Returns
        -------
        None

        '''
        self.snakes = []
        for snek in play_state["snakes"]:
            self.snakes.append(Snake(snek))

        self.food = []
        for fuud in play_state["food"]:
            self.food.append(Food(fuud))

        self.possible_moves()

    def possible_moves(self):
        '''
        Remove all the bodies from being a valid move.
        Moving to where a head currently sits is a valid move (checked in
        another function).
        This dosn't remove the head or the last node of the body.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        for snake in self.snakes:
            for body in range(len(snake.body)-1):
                try:
                    self.board.remove_node((snake.body[body].x, snake.body[body].y))
                except Exception as e:
                    logging.critical(e)

    def calc_vectors(self, snake_id):
        '''
        Calculate how much the snake or food should push or pull the our snake
        Not used anymore.
        TODO: Remove this
        '''
        mann_dist = []

        for snake in self.snakes:
            if snake.id != snake_id:
                mann_dist.append(self.ms.head*snake.head)

        for food in self.food:
            mann_dist.append(self.ms.head*food)

        return mann_dist

    def check_index(self, x, y):
        '''
        Checks the given index if its food, snake, head, or nothing

        Parameters
        ----------
        x : int
            x position in the grid
        y : int
            y position in the grid

        Returns
        -------
        result : string
            returns 'F' for food, 'B' for a body link, 'S' for a head,
            ' ' for nothing, and '?' for an error
        '''
        for food in self.food:
            if x == food.x and y == food.y:
                return "F"
        for snake in self.snakes:
            for link in snake.body:
                if x == link.x and y == link.y:
                    return "B"
            if x == snake.head.x and y == snake.head.y:
                return "S"
        if (x, y) in self.board:
            return " "
        return "?"


class Snake():
    def __init__(self, snake_info):
        ''' All information relating to a specific snake '''
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
    def __init__(self, lx=-1, ly=-1):
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
        '''
        Used for testing.
        TODO: Move this to an external file so that it can create a more
            complete testing venu
        '''
        self.start = """
        {
          "game": {
            "id": "game-id-string"
          },
          "turn": 4,
          "board": {
            "height": 15,
            "width": 15,
            "food": [
              {
                "x": 10,
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


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)
    td = TD()
    game = Game(td.start)
    #[dirs, nods] = game.legal_moves(game.board.ms.head)
    #game.go_to_tail(game.board.ms.head, game.board.ms.body[-1]))

