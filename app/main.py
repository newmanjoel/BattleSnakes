import json
import os
import random
import bottle
import logging
from snake_logic import Game, Snake, Board, TD

import math, cmath
import networkx as nx
from api import ping_response, start_response, move_response, end_response
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)


def pretty_print(game, chosen_direction, angle):
    text = ""
    text += "W:{}\tH:{}\tT:{}\n".format(game.board.width, game.board.height, game.turn)
    text += "{}".format(game.stored_legal_direction) +" {} {}\n".format(chosen_direction, angle)
    for x in range(game.board.width):
        for y in range(game.board.height):
            text+= game.board.check_index(y, x) + "|"
        text+= "\n"
    print(text)

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json
    
    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    #print("Start: {}".format(data))
    logging.debug("Start Post")

    color = "#00FF00"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json
    logging.warning("The version of network x is {}".format(nx.__version__))
    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """

    logging.debug("Move: {}".format(data))
    game = Game(data)
    z = sum(game.board.calc_vectors(game.my_snake))
    angle = math.degrees(cmath.phase(z))
    logging.info("Sum of vectors {}<{}".format(abs(z),angle ))

    ideal_direction = ""
    direction = ""

    '''
    TODO: confirm these angles
    '''

    if angle>45 and angle<135:
        ideal_direction = 'up'
    elif angle>135 and angle<=180:
        ideal_direction = 'left'
    elif angle<45 and angle>-45:
        ideal_direction = 'right'
    elif angle<-45 and angle >-135:
        ideal_direction = 'down'
    elif angle<-135 and angle>-180:
        ideal_direction = 'left'


    #logging.info(repr(game.board))
    [legal_directions, nodes, safe] = game.legal_moves()
    logging.info("Head: {}, Legal Directions: {}, Nodes: {}, Safe:{}".format(game.board.ms.head, legal_directions, nodes, safe))
    #safe_directions = game.safe_moves(legal_directions, nodes)
    safe_directions = []
    for i in range(len(safe)):
        if safe[i]:
            logging.info("Safe direction {}".format(legal_directions[i]))
            safe_directions.append(legal_directions[i])
        
    if len(safe_directions)  == 0:
        if len(legal_directions) == 0:
            # we are screwed at this point just hope that we are wrong and have luck
            directions = ['up', 'down', 'left', 'right']
            logging.critical("Could not find a legal direction")
        else:
            directions = legal_directions
            logging.info("No safe directions, defaulting to legal moves")
    else:
        directions = safe_directions
    
    direction = random.choice(directions)

    pretty_print(game, direction, angle)
    logging.info("Legal Moves: {}\nChose: {}".format(directions, direction))
    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    #print("End: {}".format(data))
    #logging.debug("End: {}".format(data))
    #print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()


if __name__ == '__main__':
    logging.info("setting up server at 192.168.86.46:8080")
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
    logging.info("shutting down application")
