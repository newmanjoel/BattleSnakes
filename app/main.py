import bottle
import os
import networkx as nx
import numpy as np
import random
import logging



@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.get('/')
def index():
    return {
        'color': '#ffffff',
        'head': 'fang'
    }


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']
    return {
        "color": "#ff00ff",
        "headType": "bendr",
        "tailType": "pixel"
    }



@bottle.post('/move')
def move():
    data = bottle.request.json 
    try:
        raise Exception("This is a general exception")
    except Exception as e:
        move = random.choice(['up','down','left','right'])
        taunt = e.message
    return {
        'move': move
    }

@bottle.post('/')
@bottle.post('/ping')
def ping():
    return {
            'response':200
            }


@bottle.post('/end')
def end():
    data = bottle.request.json
    # TODO: Do things with data
    return {
        'response':200
    }



# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
