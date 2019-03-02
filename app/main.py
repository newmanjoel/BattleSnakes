import json
import os
import random
import bottle
import logging
from snake_logic import Game, Snake, Board, TD

from timeit import default_timer as timer

import math, cmath
import networkx as nx
from api import ping_response, start_response, move_response, end_response
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)


def pretty_print(game, chosen_direction, angle):
    if logging.getLogger().getEffectiveLevel() > 10:
        text = ""
        text += "W:{}\tH:{}\tT:{}\n".format(game.board.width, game.board.height, game.turn)
        text += "{}".format(game.stored_legal_direction) +" {} {}\n".format(chosen_direction, angle)
        for x in range(game.board.width):
            for y in range(game.board.height):
                text+= game.board.check_index(y, x) + "|"
            text+= "\n"
        logging.debug(text)

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

    start1 = timer()
    game = Game(data)
    end = timer()
    logging.info("TURN {}".format(game.turn))
    logging.info("init took {}".format(end-start1))
    start = timer()
    [legal_directions, nodes] = game.legal_moves(game.board.ms.head.x, game.board.ms.head.y)
    end = timer()
    logging.debug("legal moves took {}".format(end-start))
    
    logging.debug("Head: {}, Legal Directions: {}, Nodes: {}".format(game.board.ms.head, legal_directions, nodes))
    start = timer()
    safe_directions = game.safe_moves(legal_directions, nodes)
    end = timer()
    logging.debug("safe took {}".format(end-start))
    path = []
    if(game.board.ms.health > 30):
        logging.info("chasing tail")
        path = game.go_to_tail(game.board.ms.head, game.board.ms.body[-1])
    else:
        #find closest food and go for it
        logging.info("chasing food")
        path = game.go_to_closest_food(game.board.ms.head)
    logging.info("Want to take {} path".format(path))
    
    path_direction = ""
    if len(path) > 0:
        path_direction = game.relative_direction(game.board.ms.head, path[1])
        
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
    #if path_direction in directions and path_direction != "":
    #    logging.info("path direction choice")
    #    direction = path_direction
    #else:
    #    logging.info("random direction choice")
    #    direction = random.choice(directions)
    direction = path_direction
    angle = ""
    #pretty_print(game, direction, angle)
    logging.info("Legal Moves: {}\nChose: {}".format(directions, direction))
    logging.info("Total Time: {}".format(timer()-start1))
    return move_response(direction)


@bottle.post('/end')
def end():
    #data = bottle.request.json

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
