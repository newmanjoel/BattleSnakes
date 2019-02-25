import bottle
import os
import networkx as nx
import numpy as np
import random



@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.get('/')
def index():
    #head_url = '%s://%s/static/head.png' % (
    #    bottle.request.urlparts.scheme,
    #    bottle.request.urlparts.netloc
    #)
    
    
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
    
    
    

    #head_url = '%s://%s/static/head.png' % (
    #    bottle.request.urlparts.scheme,
    #    bottle.request.urlparts.netloc
    #)
    return {
        'color': '#00ff00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': 'fang',
        'name': 'Vengeful Mittens'
    }



@bottle.post('/move')
def move():
    data = bottle.request.json 
    try:
        snek = Snake(data['game_id'],data['width'],data['height'])
        move = snek.turn(data)
        taunt = 'tis but a flesh wound...'
    except Exception as e:
        move = random.choice(['up','down','left','right'])
        taunt = e.message
        

    return {
        'move': move,
        'taunt': taunt
    }


@bottle.post('/end')
def end():
    data = bottle.request.json

    # TODO: Do things with data

    return {
        'taunt': 'battlesnake-python!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
