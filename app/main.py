import bottle
import os
import networkx as nx
import numpy as np
import random


class Snake(object):
    def __init__(self,newName,row,col,unique=1,method = 'a_star',a = 0.5,b = 0.5,c = 0.25):
        self.legendString = '~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQURTUVWXYZ!@#$%^&*()_+<>?:"{}|\][/.,'
        self.legendMatrix = []
        self.n = row
        self.rows = row
        self.cols = col
        self.walls = self.generateWalls()
        self.id = unique
        self.method = method
        self.name = newName
        self.hunger = 100
        self.a = a
        self.b = b
        self.c = c
        self.gameID = ''
        for row in range(self.rows+2):
            for col in range(self.cols+2):
                self.legendMatrix.append(self.legendString[row]+self.legendString[col])
        self.legendMatrix = np.asarray(self.legendMatrix)
        self.G = nx.Graph()
        self.G.add_nodes_from(self.legendMatrix)
        self.legendMatrix = self.legendMatrix.reshape((self.rows+2,self.cols+2))

    def addBarriers(self,beforeFrame,toAdd):
        localFrame = np.copy(beforeFrame)
        try:
            for snake in range(len(toAdd)):
                for i in range(len(toAdd[snake])):
                    localFrame[toAdd[snake][i][0],toAdd[snake][i][1]] = 1
        except Exception as e:
            pass
        #localFrame
        return localFrame
    
    def generateWalls(self):
        output_args = np.ones((self.rows+2,self.cols+2))
        output_args[1:self.rows+1,1:self.cols+1] = np.zeros((self.rows,self.cols))
        return output_args
    
    def makeDecision(self):
        try:
            if(self.path==''):
                return 'up'
            if(len(self.path)==1):
                return 'down'
            if(self.path[1]==self.legendMatrix[self.snakeHead[0]+1,self.snakeHead[1]]):
                return 'up'
            if(self.path[1]==self.legendMatrix[self.snakeHead[0]-1,self.snakeHead[1]]):
                return 'down'
            if(self.path[1]==self.legendMatrix[self.snakeHead[0],self.snakeHead[1]+1]):
                return 'right'
            if(self.path[1]==self.legendMatrix[self.snakeHead[0],self.snakeHead[1]-1]):
                return 'left'
        except Exception as e:
            print 'DECISION ERROR: '+ e.message
            print 'snakeHead: '
            print self.snakeHead
            print 'Path:%s'%(self.path)
            print 'Path Length:%d'%(len(self.path))
          
    
    def generateDanger(self):
        self.weights = np.zeros((self.rows+2,self.cols+2))
        for row in range(1,self.rows+1):
            for col in range(1,self.cols+1):
                self.weights[row,col] = self.currentFrame[row,col]*self.b+self.c + self.currentFrame[row+1,col]*self.b+self.currentFrame[row-1,col]*self.b+self.currentFrame[row,col+1]*self.b+self.currentFrame[row,col-1]*self.b
        self.weights = self.weights+self.walls
        
    def generateMoveset(self):
        for row in range(1,self.rows+1):
            for col in range (1,self.cols+1):
                
                if(self.currentFrame[row,col]==0 and self.currentFrame[row+1,col]==0):
                    self.G.add_edge(self.legendMatrix[row,col],self.legendMatrix[row+1,col], weight = (self.weights[row,col]*self.a + self.weights[row+1,col]*self.b))
                        
                if(self.currentFrame[row,col]==0 and self.currentFrame[row-1,col]==0):
                    self.G.add_edge(self.legendMatrix[row,col],self.legendMatrix[row-1,col], weight = (self.weights[row,col]*self.a + self.weights[row-1,col]*self.b))
    
                if(self.currentFrame[row,col]==0 and self.currentFrame[row,col+1]==0):
                    self.G.add_edge(self.legendMatrix[row,col],self.legendMatrix[row,col+1], weight = (self.weights[row,col]*self.a + self.weights[row,col+1]*self.b))
    
                if(self.currentFrame[row,col]==0 and self.currentFrame[row,col-1]==0):
                    self.G.add_edge(self.legendMatrix[row,col],self.legendMatrix[row,col-1], weight = (self.weights[row,col]*self.a + self.weights[row,col-1]*self.b))
                if(self.currentFrame[row,col]!=0):
                    try:
                        self.G.remove_edge(self.legendMatrix[row,col],self.legendMatrix[row+1,col])
                    except Exception:
                        pass
                    try:
                        self.G.remove_edge(self.legendMatrix[row,col],self.legendMatrix[row-1,col])
                    except Exception:
                        pass
                    try:
                        self.G.remove_edge(self.legendMatrix[row,col],self.legendMatrix[row,col+1])
                    except Exception:
                        pass
                    try:
                        self.G.remove_edge(self.legendMatrix[row,col],self.legendMatrix[row,col-1])
                    except Exception:
                        pass
        
    def feed(self):
        self.hunger = 100
        
    def getHunger(self):
        return self.hunger
    
    def setID(self,newValue):
        self.id = newValue
        
    def getOrignalID(self):
        return self.orignalID
    
    def dist(self,start,finish):
        deltaX = np.linalg.norm([start[0],finish[0]])
        deltaY = np.linalg.norm([start[1],finish[1]])
        return np.linalg.norm([deltaX,deltaY])
        
    def calcDist(self,unsorted):
        ans= np.array([])
        for uns in unsorted: 
            #print uns
            dx = uns[0]-self.snakeHead[0]
            dy = uns[1]-self.snakeHead[1]
            temp = [pow(pow(dx,2)+pow(dy,2),0.5)]
            ans=np.append(ans,temp)
        return ans
        
    def turn(self,data):
        
        unsortedFood = np.copy(data['food'])
        self.food = np.copy(data['food'])
        self.hunger -=1                 # loose a hunger, cause a turn has passed
        self.a = self.hunger/100.0
        self.b = self.hunger/100.0
        localSnakes = data['snakes']   # make sure we dont change the orignal
        self.currentFrame = self.addBarriers(self.walls,[[0,0]])     #add all of the snakes to the current frame
        
        #self.currentFrame = self.addBarriers(self.currentFrame,snek['coords'])
        for snek in localSnakes:
            self.currentFrame = self.addBarriers(self.currentFrame,snek['coords'])
            if snek['name']=='Vengeful Mittens':
                snake = snek['coords']    # isolate just our snake from all the snakes
        
        
        #localSnakes = np.delete(localSnakes,self.id,0)              # remove our snake from the local snakes (why, IDK?!)
        self.snakeHead = snake[0]                                   # set the snake head to the first thing in the snake array
        self.currentFrame[self.snakeHead[0],self.snakeHead[1]]=0    # make sure the head is not 1! EXTREMEMLY IMPORTANT
        snake = np.roll(snake,-1,0)     # circular shift, put the head at the back of the array
        snakeBody = snake[:-1]          # copy everything but the head
        self.generateDanger()           # generate the danger matrix
        self.generateMoveset()          # generate the moveset
        self.path = ''

        
        index = 0
        while len(unsortedFood)!=0:
            distanceFood = self.calcDist(unsortedFood)
            maxFood = np.argmin(distanceFood)
            self.food[index]=unsortedFood[maxFood]
            unsortedFood = np.delete(unsortedFood,maxFood,0)
            index+=1
        
        points = np.array(self.food.tolist())
        if(len(points)!=0):
            points = np.append(points,[[snakeBody[-1,0],snakeBody[-1,1]]],0)
        else:
            points = np.array([[snakeBody[-1,0],snakeBody[-1,1]]])
        points = np.append(points,[[snakeBody[-1,0]+1,snakeBody[-1,1]]],0)
        points = np.append(points,[[snakeBody[-1,0]-1,snakeBody[-1,1]]],0)
        points = np.append(points,[[snakeBody[-1,0],snakeBody[-1,1]+1]],0)
        points = np.append(points,[[snakeBody[-1,0],snakeBody[-1,1]-1]],0)
        
        for point in points:
            if self.method == 'a_star':
                try:
                    self.path =  nx.astar_path(self.G,self.legendMatrix[self.snakeHead[0],self.snakeHead[1]],self.legendMatrix[point[0],point[1]])
                    return self.makeDecision()
                    break
                except Exception as e:
                    #print self.name + '-> Tail Exception: '+ e.message
                    pass
            if self.method =='dijkstra_path':
                try:
                    self.path =  nx.dijkstra_path(self.G,self.legendMatrix[self.snakeHead[0],self.snakeHead[1]],self.legendMatrix[point[0],point[1]])
                    return self.makeDecision()
                    break
                except Exception as e:
                    #print self.name + '-> Tail Exception: '+ e.message
                    pass
        return self.makeDecision()
      



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
        'color': '#00ffff',
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
        taunt = 'W:%s'%(move)
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
    global snakes
    snakes=[]
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
